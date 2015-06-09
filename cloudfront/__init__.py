"""
AWS CloudFront Private Content Signing

usage:

    import cloudfront
    cloudfront.sign(url, secs)

"""
import Crypto.Hash.SHA
import Crypto.PublicKey.RSA
import Crypto.Signature.PKCS1_v1_5
from django.conf import settings
import urllib
import base64
import time


KEY_PAIR_ID = getattr(settings, 'CLOUDFRONT_KEY_PAIR_ID', None)
PRIVATE_KEY = getattr(settings, 'CLOUDFRONT_PRIVATE_KEY', None)


def _get_signature(message, private_key):
    key = Crypto.PublicKey.RSA.importKey(private_key)
    signer = Crypto.Signature.PKCS1_v1_5.new(key)
    sha1_hash = Crypto.Hash.SHA.new()
    sha1_hash.update(bytes(message))
    return signer.sign(sha1_hash)


def _base64_encode(msg):
    msg_base64 = base64.b64encode(msg)
    msg_base64 = msg_base64.replace('+', '-')
    msg_base64 = msg_base64.replace('=', '_')
    msg_base64 = msg_base64.replace('/', '~')
    return msg_base64


def _create_url(url, encoded_signature, key_pair_id, expires):
    params = urllib.urlencode({
        'Expires': expires,
        'Signature': encoded_signature,
        'Key-Pair-Id': key_pair_id
    })
    return url + '?' + params


def _get_canned_policy(url, priv_key_string, expires):
    canned_policy = '{"Statement":[{"Resource":"%(url)s","Condition":{"DateLessThan":{"AWS:EpochTime":%(expires)s}}}]}' % {'url': url, 'expires': expires}

    signature = _get_signature(canned_policy, priv_key_string)

    encoded_signature = _base64_encode(signature)

    return encoded_signature


def _get_canned_policy_url(url, priv_key_string, key_pair_id, expires):

    encoded_signature = _get_canned_policy(url, priv_key_string, expires)

    signed_url = _create_url(url, encoded_signature, key_pair_id, expires)

    return signed_url


def _encode_query_param(resource):
    """
    Flash player doesn't like query params,
    so encode them if you're using a streaming distribution
    """
    enc = resource
    enc = enc.replace('?', '%3F')
    enc = enc.replace('=', '%3D')
    enc = enc.replace('&', '%26')
    return enc


def sign(resource, secs=10):
    expires = int(time.time()) + secs

    if not PRIVATE_KEY or not KEY_PAIR_ID:
        assert False, 'Please provide CLOUDFRONT_PRIVATE_KEY and CLOUDFRONT_KEY_PAIR_ID in settings.py'

    signed_url = _get_canned_policy_url(resource, PRIVATE_KEY, KEY_PAIR_ID, expires)

    # for flash streaming
    # enc_url = _encode_query_param(signed_url)
    # print(enc_url)

    return signed_url

# http://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-setting-signed-cookie-canned-policy.html
def set_signed_cookies(response, resource, secs=3600):
    expires = int(time.time()) + secs

    if not PRIVATE_KEY or not KEY_PAIR_ID:
        assert False, 'Please provide CLOUDFRONT_PRIVATE_KEY and CLOUDFRONT_KEY_PAIR_ID in settings.py'

    encoded_signature = _get_canned_policy(resource, PRIVATE_KEY, expires)
    
    response.set_cookie(
        'CloudFront-Expires',
        expires,
        httponly=True,
    )

    response.set_cookie(
        'CloudFront-Signature',
        encoded_signature,
        httponly=True,
    )

    response.set_cookie(
        'CloudFront-Key-Pair-Id',
        KEY_PAIR_ID,
        httponly=True,
    )
    
    return response