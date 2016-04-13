#!/usr/bin/python3

import requests as rq
import argparse
import config

url_thread = 'https://www.facebook.com/ajax/mercury/thread_info.php'

def main():
    parser = argparse.ArgumentParser(description='Download Facebook conversations')
    parser.add_argument('thread', help='the id of the conversation to be downloaded')

    parser.parse_args()
    cookie = parse_cookie()

    ses = rq.Session()
    ses.cookies = cookie

# Parse a cookie from string (as represented in Chrome developer tools)
def parse_cookie():
    cookielist = config.cookie.split(';')
    cookielist = [x.strip().split('=', 1) for x in cookielist]
    cookie = {}
    
    for [a, b] in cookielist:
        cookie[a] = b

    cookie = rq.utils.cookiejar_from_dict(cookie)
    return cookie

if __name__ == '__main__':
    main()
