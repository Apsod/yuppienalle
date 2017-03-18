import netifaces


def get_wlan_addr():
    return netifaces.ifaddresses('wlp3s0')[netifaces.AF_INET][0]['addr']
