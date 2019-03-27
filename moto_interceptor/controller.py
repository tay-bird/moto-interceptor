from multiprocessing import Process
import os

import boto3
from moto import server
from werkzeug.serving import run_simple

from moto_interceptor.crypto import create_certs
from moto_interceptor.intercept import Dnsmasq, Hostfile, Resolver
from moto_interceptor.proxy import proxy
from moto_interceptor.utils import get_available_port


class Controller(object):

    def __init__(self, cert_path=None, intercept_method=None, moto_processes=[],
                 multiplex=False, proxy_process=None, proxy_map={},
                 ssl_context=None, target_regions=[], target_services=[]):
        self.proxy_process = proxy_process
        self.proxy_map = proxy_map
        self.moto_processes = moto_processes
        self.multiplex = multiplex

        if cert_path is None:
            self.cert_path = os.getcwd()
        else:
            self.cert_path = os.path.join(os.getcwd(), cert_path)

        if intercept_method is None or intercept_method not in ['dnsmasq', 'hostfile']:
            self.intercept_method = 'hostfile'
        else:
            self.intercept_method = intercept_method

        if ssl_context is None:
            ssl_cert = os.path.join(self.cert_path, 'localhost.crt')
            ssl_key = os.path.join(self.cert_path, 'localhost.key')
            self.ssl_context = (ssl_cert, ssl_key)
        else:
            self.ssl_context = ssl_context

        if target_regions:
            self.target_regions = target_regions
        else:
            self.target_regions = boto3.Session().get_available_regions('ec2')

        if target_services:
            self.target_services = target_services
        else:
            self.target_services = boto3.Session().get_available_services()

    def start_all(self):
        self.start_interceptors()

        try:
            self.start_moto()
            self.start_proxy()
            self.proxy_process.join()

        except:
            raise

        finally:
            self.stop_interceptors()
            self.stop_moto()
            self.stop_proxy()

    def start_interceptors(self):
        region_hosts = [region + '.amazonaws.com' for region in self.target_regions]
        
        short_hosts = [
            service + '.amazonaws.com'
            for service in self.target_services]

        long_hosts = [
            service + '.' + region_host
            for region_host in region_hosts
            for service in self.target_services]

        region_sans = [
            '*.' + region_host
            for region_host in region_hosts]

        service_sans = [
            '*.' + host
            for host in short_hosts + long_hosts]

        certificate_sans = ['*.amazonaws.com'] + region_sans + service_sans

        if self.intercept_method == 'dnsmasq':
            dnsmasq_entry = 'address=/.amazonaws.com/127.0.0.1'
            resolver_entry = 'nameserver 127.0.0.1'

            dnsmasq_interceptor = Dnsmasq()
            dnsmasq_interceptor.add_entries(
                ['address=/.amazonaws.com/127.0.0.1\n'])

            resolver_interceptor = Resolver()
            resolver_interceptor.add_entries(
                ['nameserver 127.0.0.1\n'])

            self.interceptors = [dnsmasq_interceptor, resolver_interceptor]

        elif self.intercept_method == 'hostfile':
            host_entries = [
                '127.0.0.1 ' + host + '\n'
                for host in short_hosts + long_hosts]

            host_interceptor = Hostfile()
            host_interceptor.add_entries(host_entries)
            self.interceptors = [host_interceptor]

        else:
            raise KeyError(
                'Unknown intercept type: {}'.format(self.intercept_method))

        create_certs(self.cert_path, domain='localhost', sans=certificate_sans)

    def start_moto(self):
        if self.multiplex is True:
            for service in self.target_services:
                moto_server = server.DomainDispatcherApplication(
                    server.create_backend_app, service=service)

                port = get_available_port()
                self.proxy_map[service] = port

                moto_process = Process(
                    target=run_simple,
                    args=('localhost', port, moto_server),
                    kwargs={'threaded': True})
                self.moto_processes.append(moto_process)
                
                moto_process.start()
        
        else:
            moto_server = server.DomainDispatcherApplication(
                server.create_backend_app)

            port = get_available_port()
            
            for service in self.target_services:
                self.proxy_map[service] = port
            
            moto_process = Process(
                target=run_simple,
                args=('localhost', port, moto_server),
                kwargs={'threaded': True})
            self.moto_processes.append(moto_process)

            moto_process.start()

    def start_proxy(self):
        proxy.config['PROXY_MAP'] = self.proxy_map

        if self.proxy_process is None:
            self.proxy_process = Process(
                target=run_simple,
                args=('127.0.0.1', 443, proxy),
                kwargs={'ssl_context': self.ssl_context})

        self.proxy_process.start()

    def stop_interceptors(self):
        for interceptor in self.interceptors:
            interceptor.remove_entries()

    def stop_moto(self):
        for p in self.moto_processes:
            p.terminate()

    def stop_proxy(self):
        self.proxy_process.terminate()
