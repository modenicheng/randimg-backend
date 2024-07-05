#!/usr/bin/env python

from argparse import ArgumentParser
from base64 import urlsafe_b64encode
from hashlib import sha256
from pprint import pprint
from secrets import token_urlsafe
from sys import exit
from urllib.parse import urlencode
from webbrowser import open as open_url
import time
import requests

from cache import cache

# Latest app version can be found using GET /v1/application-info/android
USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"
REDIRECT_URI = "https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback"
LOGIN_URL = "https://app-api.pixiv.net/web/v1/login"
AUTH_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"


def s256(data):
    """S256 transformation method."""

    return urlsafe_b64encode(
        sha256(data).digest()).rstrip(b"=").decode("ascii")


def oauth_pkce(transform):
    """Proof Key for Code Exchange by OAuth Public Clients (RFC7636)."""

    code_verifier = token_urlsafe(32)
    code_challenge = transform(code_verifier.encode("ascii"))

    return code_verifier, code_challenge


def print_auth_token_response(response):
    data = response.json()

    try:
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
    except KeyError:
        print("error:")
        pprint(data)
        exit(1)

    print("access_token:", access_token)
    print("refresh_token:", refresh_token)
    print("expires_in:", data.get("expires_in", 0))


def login():
    code_verifier, code_challenge = oauth_pkce(s256)
    login_params = {
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "client": "pixiv-android",
    }
    url = LOGIN_URL + "?" + urlencode(login_params)
    open_url(url)

    try:
        code = input("code: ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    response = requests.post(
        AUTH_TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code",
            "include_policy": "true",
            "redirect_uri": REDIRECT_URI,
        },
        headers={"User-Agent": USER_AGENT},
    )

    print_auth_token_response(response)
    try:
        return {
            'access_token': response.json()["access_token"],
            'refresh_token': response.json()["refresh_token"]
        }
    except KeyError:
        print("error:")
        pprint(response.json())
        exit(1)

def refresh(refresh_token):
    response = requests.post(
        AUTH_TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "include_policy": "true",
            "refresh_token": refresh_token,
        },
        headers={"User-Agent": USER_AGENT},
    )
    print_auth_token_response(response)
    try:
        return {
            'access_token': response.json()["access_token"],
            'refresh_token': response.json()["refresh_token"]
        }
    except KeyError:
        print("error:")
        pprint(response.json())
        exit(1)

def auto_refresh():
    while True:
        try:
            if not cache.get('pixiv_refresh_token') and cache.get('pixiv_refresh_token_prev'):
                print('Refresh token expired, refreshing...')
                refresh_token = refresh(cache.get('pixiv_refresh_token_prev'))['refresh_token']
                cache.set('pixiv_refresh_token', refresh_token, expire=3000)
                cache.set('pixiv_refresh_token_prev', refresh_token, expire=3600)
                print('Refresh token refreshed, new token:',
                    cache.get('pixiv_refresh_token'))

            elif not cache.get('pixiv_refresh_token') and not cache.get(
                    'pixiv_refresh_token_prev'):
                data = login()
                refresh_token = data['refresh_token']
                cache.set('pixiv_refresh_token', refresh_token, expire=3000)
                cache.set('pixiv_refresh_token_prev', refresh_token, expire=3600)
            elif cache.get('pixiv_refresh_token') and cache.get('pixiv_refresh_token_prev'):
                logger('Pixiv refresh token has not expired, wait for 2 minutes to refresh.')
                time.sleep(60 * 2)
        except KeyboardInterrupt:
            print('Now quitting')
            exit(0)

import datetime
def logger(*args, type='info'):
    t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if type == 'info':
        print(f'{t} | INFO  |', *args)
    elif type == 'error':
        print(f'{t} | ERROR |', *args)
def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    parser.set_defaults(func=lambda _: parser.print_usage())
    login_parser = subparsers.add_parser("login")
    login_parser.set_defaults(func=lambda _: login())
    refresh_parser = subparsers.add_parser("refresh")
    refresh_parser.add_argument("refresh_token")
    refresh_parser.set_defaults(func=lambda ns: refresh(ns.refresh_token))
    auto_refresh_parser = subparsers.add_parser("auto-refresh")
    # auto_refresh_parser.add_argument("auto_refresh")
    auto_refresh_parser.set_defaults(func=lambda _: auto_refresh())
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
