import os
import datetime
import gossip
from functools import wraps
from flask import Flask, render_template, request, Response
from flask_bootstrap import Bootstrap
import eva.util
from web_ui_util import get_ip_address
from eva.config import get_eva_directory, get_eva_config_file
from eva import START_TIME
from eva import log
from eva import conf
from eva import scheduler

PATH = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)
Bootstrap(app)

@gossip.register('eva.post_boot')
def eva_post_boot():
    scheduler.add_job(start_web_ui, id="eva_web_ui")

def start_web_ui():
    gossip.trigger('eva.web_ui.start', app=app)
    bind_address = conf['plugins']['web_ui']['config']['bind_address']
    port = conf['plugins']['web_ui']['config']['port']
    key_path = '%s/eva.local.key' %PATH
    crt_path = '%s/eva.local.crt' %PATH
    if not os.path.exists(key_path):
        os.system('/bin/sh %s/gen_cert.sh' %PATH)
    log.info('Starting Web UI at https://%s:%s' %(get_ip_address(), port))
    app.run(host=bind_address, port=port, ssl_context=(crt_path, key_path))

def check_auth(username, password):
    user = conf['plugins']['web_ui']['config']['username']
    passwd = conf['plugins']['web_ui']['config']['password']
    return username == user and password == passwd

def authenticate():
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """
    See: http://flask.pocoo.org/snippets/8/
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.before_request
@requires_auth
def force_login():
    # Force login for all requests.
    pass

def ready_menu_items():
    home_menu = {'path': '/', 'title': 'Home'}
    conf['plugins']['web_ui']['config']['menu_items'] = [home_menu]
    gossip.trigger('eva.web_ui.menu_items')
    return conf['plugins']['web_ui']['config']['menu_items']

def ready_metrics():
    uptime = datetime.datetime.now() - START_TIME
    metrics = [{'name': 'Uptime', 'value': str(uptime).split('.')[0]}]
    conf['plugins']['web_ui']['config']['metrics'] = metrics
    gossip.trigger('eva.web_ui.metrics')
    return conf['plugins']['web_ui']['config']['metrics']

def ready_information():
    information = [{'name': 'Eva Path', 'value': get_eva_directory()},
                   {'name': 'Eva Config File', 'value': get_eva_config_file()},
                   {'name': 'Plugin Path', 'value': conf['eva']['plugin_directory']},
                   {'name': 'Plugin Config Path', 'value': conf['eva']['config_directory']}]
    conf['plugins']['web_ui']['config']['information'] = information
    gossip.trigger('eva.web_ui.information')
    return conf['plugins']['web_ui']['config']['information']

@app.route('/')
def index():
    menu_items = ready_menu_items()
    metrics = ready_metrics()
    information = ready_information()
    gossip.trigger('eva.web_ui.index')
    return render_template('index.html',
                           menu_items=menu_items,
                           metrics=metrics,
                           information=information)

@app.route('/restart')
def restart():
    log.info('Restart initiated from hitting /restart')
    eva.util.restart()

@app.route('/restart-page')
def _restart_page():
    return restart_page()

def restart_page(restarting_title='Eva',
                 restarting_message='Restarting Eva...',
                 redirect_message='Restart successful, redirecting...',
                 redirect_url='/'):
    """
    Can be called by any plugin inside a route context.
    The restart will be initiated by the user through an AJAX call to /restart.
    Alternatively, a plugin can link or redirect to /restart-page if they
    don't care about the specific restart message options.
    """
    menu_items = ready_menu_items()
    return render_template('restarting.html',
                           menu_items=menu_items,
                           restarting_title=restarting_title,
                           restarting_message=restarting_message,
                           redirect_message=redirect_message,
                           redirect_url=redirect_url)
