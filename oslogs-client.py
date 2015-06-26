#!/usr/bin/env python
import json
import os
import traceback

import pika


HOSTNAME = os.uname()[1]
QUEUE = ROUTING_KEY = 'oslogs'

CONNECTION = pika.BlockingConnection(pika.ConnectionParameters(
    host='192.168.37.100'))
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
                print 'reading line'
                line = log.readline()
                if line:
                    log_path = log.name
                    send_update(log_path, line)
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
