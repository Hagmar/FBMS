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

class Fbms:
    def __init__(self, args):
        self.ses = rq.Session()
        self.ses.cookies = parse_cookie(config.cookie)
        self.thread = args.thread
        self.offset = args.offset
        self.number = args.number
        self.group = args.group
        self.file = args.file

    def run(self):
        thread_contents = self.download_thread()
        # users = self.extract_thread_members(thread_contents['payload'])
        messages = self.extract_messages(thread_contents['payload'])
        self.handle_messages(messages)

    def download_thread(self):
        """Download the specified number of messages from the
        provided thread, with an optional offset
        """
        data = request_data(self.thread, offset=self.offset,
                            limit=self.number, group=self.group)
        res = self.ses.post(url_thread, data=data, headers=headers)

        # Get rid of weird javascript in beginning of response
        res = res.text[9:]

        thread_contents = json.loads(res)
        return thread_contents

# TODO change to a dict mapping used id -> name?
    def extract_thread_members(self, payload):
        """Return a list of all members of a thread"""

        users = { config.request_data['__user'] }
        users.update(set(payload['roger'][self.thread].keys()))
        return users

# TODO make it possible to choose what to extract
    def extract_messages(self, payload):
        """Extract unwanted data from messages"""
        cleaned_messages = set()
        messages = payload['actions']
        for message in messages:
            if message['action_type'] == 'ma-type:user-generated-message':
                timestamp = message['timestamp']
                author = message['author']
                body = message['body']
                cleaned_messages.add((timestamp, author, body))

        return cleaned_messages

    def handle_messages(self, messages):
        """Perform specified action on messages"""
        if self.file:
            with open(self.file, 'w') as f:
                for message in sorted(messages):
                    f.write('{} {}: {}'.format(*message))
        else:
            for message in sorted(messages):
                print('{} {}: {}'.format(*message))


def main():
    args = parse_args()
    fbms = Fbms(args)
    fbms.run()

def parse_cookie(cookie):
    """Parse a cookie from string (as represented
    in Chrome developer tools)
    """
    cookielist = cookie.split(';')
    cookielist = [x.strip().split('=', 1) for x in cookielist]
    cookie = {}
    
    for [a, b] in cookielist:
        cookie[a] = b

    cookie = rq.utils.cookiejar_from_dict(cookie)
    return cookie

def request_data(thread, offset=0, timestamp=int(time()),
                 limit=2000, group=False):
    """Generate request data for a new message-fetching request"""
    conversation_type = 'thread_fbids' if group else 'user_ids'

    data = config.request_data
    data['messages[{}][{}][offset]'.format(conversation_type, thread)] = offset
    data['messages[{}][{}][timestamp]'.format(conversation_type, thread)] = timestamp
    data['messages[{}][{}][limit]'.format(conversation_type, thread)] = limit

    return data

# Validate correct command line arguments
def check_negative(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError('%r is not a positive integer' % value)
    return ivalue

# Parse the command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Download Facebook conversations')
    parser.add_argument('thread',
                        help='the id of the conversation to be downloaded')
    parser.add_argument('-g', '--group', action='store_true',
                        help='download a group conversation')
    parser.add_argument('--number', type=check_negative,
                        metavar='N', default=2000,
                        help='the number of messages to be downloaded')
    parser.add_argument('--offset', type=check_negative, default=0,
                        help='number of most recent messages to skip downloading')
    parser.add_argument('--file', '-f',
                        help='file to save messages to')

    return parser.parse_args()

if __name__ == '__main__':
    main()
