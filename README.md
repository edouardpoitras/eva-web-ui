Web UI
======

Configure and monitor Eva through a web user interface.

![Web UI](/screenshot.png?raw=true "https://127.0.0.1:8080")

## Installation

Web UI and [Web UI Plugins](https://github.com/edouardpoitras/eva-web-ui-plugins) are installed by default on Eva's first boot in order to facilitate the installation of other plugins through the Web UI.

If you wish to install it manually, simply edit your `eva.conf` file and add `web_ui` to the list of enabled plugins.

You can find the configuration file in any of the following locations:

* ~/eva.conf
* ~/.eva.conf
* ~/eva/eva.conf
* /etc/eva.conf
* /etc/eva/eva.conf

If you can't find the `eva.conf` file, simply create it in one of the locations mentioned above and add the following content:

    [eva]
    enabled_plugins = web_ui

NOTE: This will result in only the `web_ui` and it's dependencies being enabled on next Eva boot.

## Usage

All pages are proteted by HTTP basic authentication.
The default username is `admin` and the default password is `password`.
It is advised to change these, especially if exposing Eva to a network.

Simply browse to the URL and port exposed by Eva. The default is `https://<eva_ip_address>:8080` with `<eva_ip_address>` being anything from `localhost` to an internet accessible IP address depending on how you've setup Eva.

The appropriate URL and port that the Web UI was started on will be printed in the Eva logs.

If you're running Eva across the internet, you may need to configure firewall/router port forwarding rules in order to access the Web UI.

Note: The Web UI only supports HTTPS (not plain HTTP).
A self-signed certificate is generate on first use.

## Developers

This plugin will start a new scheduler job during the `eva.post_boot` trigger.
This job will take care of generating a cert and starting the Web UI on the configured port.

#### Triggers

This plugin enables the following gossip triggers:

`gossip.trigger('eva.web_ui.start', app=app)`

This trigger is fired during the `eva.post_boot` trigger and occures before the web_ui configuration options are parsed, before the certificate is generated, and before the Web UI has started.

The app parameter is the Flask object created for the Web UI.

This trigger is most often used by other plugins in order to add URL rules to create more pages in the Web UI. Here's an example of adding a new page at '/test' which executes a function named 'test':

```python
@gossip.register('eva.web_ui.start')
def web_ui_start(app):
    app.add_url_rule('/test', 'test', test)
```

In this example, a function named 'test' would need to exist and it would have to return a rendered template. See full example below.

`gossip.trigger('eva.web_ui.menu_items', menu_items=menu_items)`

A trigger fired when rebuilding pages that gives plugins a chance to add/modify the menu items of the Web UI.

Any plugin that wishes to add a page to the Web UI would typically trigger this plugin with an empty list and use the resulting list to populate the menus for their newly added page. See full example below.

`gossip.trigger('eva.web_ui.metrics', metrics=metrics)`

A trigger fired when building the Web UI landing page that gives a chance for plugins to add to the list of metrics. It will add a block on the landing page with the title and value specified. See full example below.

`gossip.trigger('eva.web_ui.information')`

Same as the `eva.web_ui.metric` except that it adds an item to the information list on the home page. See full example below.

`gossip.trigger('eva.web_ui.index')`

A trigger that gets fired right before rendering the Web UI index (landing) page.

Note that the menu item, metric, and information triggers have already been fired by the time this trigger is executed.

#### Trigger Full Example

```python
import gossip
from flask import render_template_string

@gossip.register('eva.web_ui.start')
def web_ui_start(app):
    """
    Add a new page at '/test' that executes the `test()` function when a user
    browses to that path.
    """
    app.add_url_rule('/test', 'test', test)

@gossip.register('eva.web_ui.menu_items')
def web_ui_menu_items(menu_items):
    """
    Add a new menu item called 'Test' that points to '/test'.
    """
    menu_item = {'path': '/test', 'title': 'Test'}
    menu_items.append(menu_item)

@gossip.register('eva.web_ui.metrics')
def web_ui_metrics(metrics):
    """
    Add a block in the metrics section of the landing page.
    """
    metric = {'name': 'Some Metric', 'value': 'Value Here'}
    metrics.append(metric)

@gossip.register('eva.web_ui.information')
def web_ui_metrics(information):
    """
    Add an entry in the list of information on the landing page.
    """
    info = {'name': 'Information', 'value': 'Info Here'}
    information.append(info)

def test():
    # Get menu items from all plugins to display on our new page.
    menu_items = []
    gossip.trigger('eva.web_ui.menu_items', menu_items=menu_items)
    test_markup = """
        {% extends "base.html" %}
        {% block content %}
            This is a test.
        {% endblock %}
    """
    return render_template_string(test_markup, menu_items=menu_items)
```

#### Functions

The `web_ui` plugin exposes a `restart_page()` function which is useful when you need to restart Eva and notify the user of it's progress. The function will load a page which restarts Eva, takes care of continously checking until Eva has completed the restart, and redirect the user once the restart is complete.

The function must be called within a Flask route context (such as the 'test' example function above).

Here's an example usage:

```python
conf['plugins']['web_ui']['module'].restart_page(
    restarting_title='Eva', \
    restarting_message='Restarting Eva...', \
    redirect_message='Restart successful, redirecting...', \
    redirect_url='/')
```

## Configuration

Default configurations can be changed by adding a `web_ui.conf` file in your plugin configuration path (can be configured in `eva.conf`, but usually `~/eva/configs`).

To get an idea of what configuration options are available, you can take a look at the `web_ui.conf.spec` file in this repository, or use the [Web UI Plugins](https://github.com/edouardpoitras/eva-web-ui-plugins) plugin and view them at `/plugins/configuration/conversations`.

Here is a breakdown of the available options:

    bind_address
        Type: String
        Default: '0.0.0.0'
        The Flask app binding address where the Web UI will be listening.
    port
        Type: Integer
        Default: 8080
        What port the Flask app will listen on.
    username
        Type: String
        Default: 'admin'
        The Web UI username.
    password
        Type: String
        Default: 'password'
        The Web UI password.
