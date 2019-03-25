import argparse

from . import Controller


def main():
    parser = argparse.ArgumentParser(description='Moto Server Proxy.')
    parser.add_argument('target_services', nargs='*', metavar='target_service')
    parser.add_argument('--intercept_method', choices=['dnsmasq', 'hostfile'])
    
    kwargs = vars(parser.parse_args())
    print(kwargs)

    controller = Controller(
        ssl_context=('certs/localhost.crt', 'certs/localhost.key'),
        **kwargs)

    controller.start_all()
