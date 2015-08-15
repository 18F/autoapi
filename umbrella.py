"""Helpers for configuring API backends on API Umbrella."""
import os

import requests

headers = {
    'X-Api-Key': os.environ.get('AUTOAPI_UMBRELLA_KEY'),
    'X-Admin-Auth-Token': os.environ.get('AUTOAPI_UMBRELLA_TOKEN'),
}

base = 'https://api.data.gov/api-umbrella/v1'
endpoints = {
    'apis': os.path.join(base, 'apis'),
    'publish': os.path.join(base, 'config', 'publish'),
}

def make_backend(name, host):
    """Create or update API backend."""
    backend = get_backend(name, host)
    payload = get_payload(name, host)
    if backend:
        method = 'PUT'
        url = os.path.join(endpoints['apis'], backend['id'])
        version = backend['version'] + 1
    else:
        method = 'POST'
        url = endpoints['apis']
        version = 1
    response = requests.request(method, url, json=payload, headers=headers)
    publish_backend(backend if backend else response.json()['api'], version)

def get_backend(name, host):
    """Get existing API backend matching name and host."""
    response = requests.get(endpoints['apis'], headers=headers)
    backends = response.json()['data']
    return next(
        (
            each for each in backends
            if each['name'] == name and each['backend_host'] == host
        ),
        None,
    )

def get_payload(name, host):
    """Build payload to create or update API backend."""
    return {
        'api': {
            'name': name,
            'frontend_host': 'api.data.gov',
            'backend_host': host,
            'backend_protocol': 'https',
            'balance_algorithm': 'least_conn',
            'servers': [
                {
                    'host': host,
                    'port': 443,
                }
            ],
            'url_matches': [
                {
                    'frontend_prefix': os.path.join('/api-program', name),
                    'backend_prefix': '/',
                }
            ],
        }
    }

def publish_backend(payload, version):
    id = payload['id']
    form = {
        'config[apis][{0}][pending_version]'.format(id): version,
        'config[apis][{0}][publish]'.format(id): version,
    }
    return requests.post(endpoints['publish'], headers=headers, data=form)
