import logging
import requests

from flask import Flask
from flask import request, Response


proxy = Flask(__name__)
proxy.logger.setLevel(logging.INFO)


def find_proxy_port(proxy_host, proxy_map):
    try:
        proxy_key = proxy_host.split('.')[-3]
        proxy_port = proxy_map[proxy_key]

    except KeyError:
        proxy_key = proxy_host.split('.')[-4]
        proxy_port = proxy_map[proxy_key]

    return (proxy_key, proxy_port)


@proxy.route('/', defaults={'path': ''}, methods=['DELETE', 'GET', 'HEAD', 'POST', 'PUT', 'PATCH'])
@proxy.route('/<path:path>', methods=['DELETE', 'GET', 'HEAD', 'POST', 'PUT', 'PATCH'])
def _proxy(*args, **kwargs):
    proxy_host = None
    proxy_port = None

    try:
        proxy_host = request.headers['Host']
        proxy_map = proxy.config['PROXY_MAP']
        proxy_key, proxy_port = find_proxy_port(proxy_host, proxy_map)

        resp = requests.request(
            method=request.method,
            url=request.url.replace(request.host_url, 'http://localhost:' + str(proxy_port)),
            headers={key: value for (key, value) in request.headers},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False)

        headers = [(name, value) for (name, value) in resp.raw.headers.items()]

        response = Response(resp.content, resp.status_code, headers)
        return response

    except:
        proxy.logger.error('error!')
        raise

    finally:
        proxy.logger.info({
            'host': proxy_host,
            'key': proxy_key,
            'proxy_port': proxy_port,
            'method': request.method,
            'request_headers': request.headers,
            'message': resp.content,
            'target': request.url.replace(request.host_url, 'http://localhost:' + str(proxy_port)),
            'status': resp.status_code})
