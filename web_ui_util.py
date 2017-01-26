# Thanks to https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
import socket
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
