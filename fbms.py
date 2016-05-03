#!/usr/bin/python3

import requests as rq
import argparse
import config
import json
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
    args = parse_arguments()
    cookie = parse_cookie()

    ses = rq.Session()
    ses.cookies = cookie

    download_thread(args, ses)

def download_thread(args, ses):
    jsondata = fetch_messages(ses, args.thread, args.offset, args.number, args.group)

    users = parse_thread_members(jsondata['payload'], args.thread)

    messages = clean_messages(jsondata['payload'])

    with open("tjenna", 'w') as f:
        f.write(json.dumps(messages))

# Remove unwanted data from messages
# TODO make it possible to choose what to exctract
def clean_messages(payload):
    cleaned_messages = {}
    messages = payload['actions']
    for message in messages:
        message_id = message['message_id']
        author = message['author']
        body = message['body']
        has_attachment = message['has_attachment']
        cleaned_messages[message_id] = (author, body, has_attachment)

    return cleaned_messages

# Parse the command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Download Facebook conversations')
    target_group = parser.add_mutually_exclusive_group()
    parser.add_argument('thread', help='the id of the conversation to be downloaded')
    parser.add_argument('-g', '--group', action='store_true', help='download a group conversation')
    parser.add_argument('number', nargs='?', type=check_negative, metavar='M', default=2000, help='the number of messages to be downloaded')
    parser.add_argument('offset', nargs='?', type=check_negative, default=0, help='number of most recent messages to skip downloading')
    target_group.add_argument('--file', '-f', type=argparse.FileType('w'), help='file to save messages to')
    target_group.add_argument('-p', action='store_true', help='print the messages to stdout')

    return parser.parse_args()

# Download the specified number of messages with the provided thread, with an
# optional offset
def fetch_messages(ses, thread, offset=0, number=2000, group=False):
    data = request_data(thread, offset, number, group)

    res = ses.post(url_thread, data=data, headers=headers)
    res = res.text[9:]

    jsondata = json.loads(res)
    return jsondata

# Parse a cookie from string (as represented in Chrome developer tools)
def parse_cookie():
    cookielist = config.cookie.split(';')
    cookielist = [x.strip().split('=', 1) for x in cookielist]
    cookie = {}
    
    for [a, b] in cookielist:
        cookie[a] = b

    cookie = rq.utils.cookiejar_from_dict(cookie)
    return cookie

# Generate request data for a new message fetching request
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

# Return a list with all members of a thread
# TODO change to a dict mapping used id -> name
def parse_thread_members(payload, thread):
    users = [ config.request_data['__user'] ]
    for user_id in payload['roger'][str(thread)]:
        users[user_id] = 1

    return users

# Validate correct command line arguments
def check_negative(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError('%r is not a positive integer' % value)
    return ivalue

if __name__ == '__main__':
    main()
