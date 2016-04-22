#!/usr/bin/python3

import requests as rq
import argparse
import config
from time import time

url_thread = 'https://www.facebook.com/ajax/mercury/thread_info.php'

headers = {
    'accept-encoding'   : 'gzip, deflate',
    'accept-language'   : 'en-US,en;q=0.8',
    'cookie'            : config.cookie,
    'pragma'            : 'no-cache',
    'user-agent'        : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'content-type'      : 'application/x-www-form-urlencoded',
    'accept'            : '*/*',
    'cache-control'     : 'no-cache',
    'referer'           : 'https://www.facebook.com/messages/zuck',
    }

def main():
    parser = argparse.ArgumentParser(description='Download Facebook conversations')
    parser.add_argument('thread', help='the id of the conversation to be downloaded')

    args = parser.parse_args()
    cookie = parse_cookie()

    ses = rq.Session()
    ses.cookies = cookie
    data = request_data(args.thread, True)

    res = ses.post(url_thread, data=data, headers=headers)
    with open("tjenna", 'w') as f:
        f.write(res.text)

# Parse a cookie from string (as represented in Chrome developer tools)
def parse_cookie():
    cookielist = config.cookie.split(';')
    cookielist = [x.strip().split('=', 1) for x in cookielist]
    cookie = {}
    
    for [a, b] in cookielist:
        cookie[a] = b

    cookie = rq.utils.cookiejar_from_dict(cookie)
    return cookie

def request_data(thread, offset=0, limit=2000, group=False):
    if group:
        conversation_type = 'thread_fbids'
    else:
        conversation_type = 'user_ids'

    data = config.request_data
    data['messages[%s][%s][offset]' % (conversation_type, thread)] = offset
    data['messages[%s][%s][timestamp]' % (conversation_type, thread)] = int(time())
    data['messages[%s][%s][limit]' % (conversation_type, thread)] = limit

    return data

if __name__ == '__main__':
    main()
