"""Helpers for verifying SNS signatures."""
import base64

import requests
from cryptography import x509
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def verify(payload):
    key = get_public_key(payload['SigningCertURL'])
    signature = base64.b64decode(payload['Signature'])
    message = get_message(payload)
    verifier = key.verifier(signature, padding.PKCS1v15(), hashes.SHA1())
    verifier.update(message)
    verifier.verify()

def get_public_key(url):
    response = requests.get(url)
    backend = backends.default_backend()
    cert = x509.load_pem_x509_certificate(response.content, backend=backend)
    return cert.public_key()

notification_keys = ['Message', 'MessageId', 'Subject', 'Timestamp', 'TopicArn', 'Type']
confirmation_keys = ['Message', 'MessageId', 'SubscribeURL', 'Timestamp', 'Token', 'TopicArn', 'Type']  # noqa
def get_message(payload):
    if payload['Type'] == 'Notification':
        keys = notification_keys
    elif payload['Type'] in ['SubscriptionConfirmation', 'UnsubscribeConfirmation']:
        keys = confirmation_keys
    else:
        raise ValueError('Unknown type "{0}"'.format(payload['Type']))
    message = ''
    for key in sorted(keys):
        if key in payload:
            message += key + '\n' + payload[key] + '\n'
    return message.encode('utf-8')
