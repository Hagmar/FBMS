#!/usr/bin/python3

from collections import defaultdict
from time import time
import argparse
import config
import json
import requests as rq

url_thread = 'https://www.facebook.com/ajax/mercury/thread_info.php'

headers = {
    'accept-encoding'   : 'gzip, deflate',
    'accept-language'   : 'en-US,en;q=0.8',
    'pragma'            : 'no-cache',
    'user-agent'        : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'content-type'      : 'application/x-www-form-urlencoded',
    'accept'            : '*/*',
    'cache-control'     : 'no-cache',
    'referer'           : 'https://www.facebook.com/messages/zuck',
    }

class Fbms:
    def __init__(self, args, limit_step=20):
        self.ses = rq.Session()
        self.ses.cookies = parse_cookie(config.cookie)
        self.thread = args.thread
        self.offset = args.offset
        self.number = args.number
        self.all = args.all
        self.group = args.group
        self.file = args.file
        self.hard = args.hard
        self.fetched = 0
        self.end_of_history = False
        self.limit_step = limit_step
        self.quiet = args.quiet
        self.user_message_count = args.user_message_count
        if self.user_message_count:
            self.user_message_counter = defaultdict(int)

    def run(self):
        message_timestamp = int(time())
        limit = 0
        while (not self.end_of_history and
                (self.all or self.fetched < self.number)):
            offset = self.fetched
            limit = min(limit + self.limit_step, 200)
            thread_contents = self.download_thread(limit, offset, message_timestamp)
            # users = self.extract_thread_members(thread_contents['payload'])
            messages = self.extract_messages(
                    thread_contents.get('payload', []))
            self.handle_messages(messages)
            message_timestamp = messages[-1]['timestamp'] - 1
            self.fetched += len(messages)

        self.finish()

    def download_thread(self, limit, offset, message_timestamp):
        """Download the specified number of messages from the
        provided thread, with an optional offset
        """
        data = request_data(self.thread, offset=offset,
                            limit=limit, group=self.group,
                            timestamp=message_timestamp)
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
        """Extract wanted data from messages"""
        cleaned_messages = []
        messages = payload.get('actions', [])
        max_timestamp = 0
        for message in messages:
            if message['action_type'] == 'ma-type:user-generated-message':
                message_dict = {}
                message_dict['timestamp'] = message['timestamp']
                message_dict['author'] = message['author']
                message_dict['body'] = message['body']
                cleaned_messages.append(message_dict)

        if 'end_of_history' in payload:
            self.end_of_history = True

        return sorted(cleaned_messages, reverse=True,
                      key=lambda x: x['timestamp'])

    def handle_messages(self, messages):
        """Perform specified action on messages"""
        if self.hard and self.fetched + len(messages) > self.number:
            messages = messages[:self.number - self.fetched]
        if self.file:
            with open(self.file, 'w') as f:
                for message in messages:
                    if self.user_message_count:
                        self.user_message_counter[message['author']] += 1
                    f.write('{timestamp} {author}: {body}\n'.format(**message))
        else:
            for message in messages:
                if self.user_message_count:
                    self.user_message_counter[message['author']] += 1
                if not self.quiet:
                    print('{timestamp} {author}: {body}'.format(**message))

    def finish(self):
        if self.user_message_count:
            for user, count in sorted(self.user_message_counter.items(),
                                      key=lambda x: x[1]):
                print('{} - {} messages'.format(user, count))


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
    number = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('thread',
                        help='the id of the conversation to be downloaded')
    parser.add_argument('-g', '--group', action='store_true',
                        help='download a group conversation')
    number.add_argument('--number', '-n', type=check_negative,
                        metavar='N',
                        help='the (approximate) number of messages to perform actions on')
    number.add_argument('--all',
                        action='store_true',
                        help='perform actions on all messages')
    parser.add_argument('--offset', type=check_negative, default=0,
                        help='number of most recent messages to skip downloading')
    parser.add_argument('--file', '-f',
                        help='file to save messages to')
    parser.add_argument('--user-message-count', '--umc',
                        action='store_true',
                        help='count the number of messages each user has sent')
    parser.add_argument('--hard', action='store_true',
                        help='clamp number of downloaded messages to N.')
    parser.add_argument('--quiet', '-q',
                        action='store_true',
                        help='don\'t print messages to stdout')

    return parser.parse_args()

if __name__ == '__main__':
    main()
