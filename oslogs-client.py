#!/usr/bin/env python
import json
import sys
import os
import traceback

import pika


HOSTNAME = os.uname()[1]


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='192.168.37.100'))
    channel = connection.channel()

    channel.queue_declare(queue='oslogs')

    msg = {'host': HOSTNAME, 'path': sys.argv[1], 'msg': sys.argv[2]}
    msg = json.dumps(msg)

    channel.basic_publish(exchange='',
                          routing_key='oslogs',
                          body=msg)
    print " [x] Sent msg %s" % msg
    connection.close()


if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        traceback.format_exc(err)
