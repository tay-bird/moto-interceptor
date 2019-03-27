import argparse

from . import Controller


def main():
    parser = argparse.ArgumentParser(description='Moto Server Proxy.')

    parser.add_argument('--cert_path', nargs='?')
    parser.add_argument('--intercept_method', choices=['dnsmasq', 'hostfile'])
    parser.add_argument('--multiplex', action='store_true')
    parser.add_argument('--target_services', nargs='*', metavar='target_service')
    parser.add_argument('--target_regions', nargs='*', metavar='target_region')

    kwargs = vars(parser.parse_args())

    controller = Controller(**kwargs)

    controller.start_all()
