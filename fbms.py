#!/usr/bin/python3

import requests as rq
import argparse
import config
from time import time

url_thread = 'https://www.facebook.com/ajax/mercury/thread_info.php'

def main():
    parser = argparse.ArgumentParser(description='Download Facebook conversations')
    parser.add_argument('thread', help='the id of the conversation to be downloaded')

    args = parser.parse_args()
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

def request_data(thread, group=False):
    if group:
        conversation_type = 'thread_fbids'
    else:
        conversation_type = 'user_ids'

    data = config.request_data
    data['messages[%s][%s][offset]' % (conversation_type, thread)] = 0,
    data['messages[%s][%s][timestamp]' % (conversation_type, thread)] = 0,
    data['messages[%s][%s][limit]' % (conversation_type, thread)] = 0

    return data

if __name__ == '__main__':
    main()
