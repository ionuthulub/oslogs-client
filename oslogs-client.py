#!/usr/bin/env python
import json
import re
import os
import time
import traceback

import pika


HOSTNAME = os.uname()[1]
QUEUE = ROUTING_KEY = 'oslogs'

try:
    fin = open('oslogs-client.conf', 'r')
    AMQP_HOST = re.search('AMQP_HOST=(.*)', fin.read()).group(1).strip()
    print 'AMQP_HOST found in config: "%s"' % AMQP_HOST
except Exception, err:
    print 'AMQP_HOST not found in config. Using "127.0.0.1"'
    AMQP_HOST = '127.0.0.1'

CONNECTION = pika.BlockingConnection(pika.ConnectionParameters(
    host=AMQP_HOST))
CHANNEL = CONNECTION.channel()
CHANNEL.queue_declare(queue=QUEUE)


def main():
    with open('logs.txt', 'r') as fin:
        log_paths = [l.strip() for l in fin.readlines()]
    logs = []
    for log_path in log_paths:
        try:
            logs.append(open(log_path, 'r'))
            logs[-1].seek(0, 2)
        except Exception, err:
            print 'Failed to open "%s"; error "%s"' % (log_path, err)
    if not logs:
        print 'No logs found. Exiting...'
        return
    try:
        while True:
            for log in logs:
                line = log.readline()
                if line:
                    log_path = log.name
                    send_update(log_path, line)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print 'Exiting...'
        CONNECTION.close()
        return


def send_update(path, msg):
    update = {'host': HOSTNAME, 'path': path, 'msg': msg}
    update = json.dumps(update)
    CHANNEL.basic_publish(exchange='', routing_key=ROUTING_KEY, body=update)
    print 'Sent "%s"' % update


if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        traceback.format_exc(err)
