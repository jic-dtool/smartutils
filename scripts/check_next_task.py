import os
import json
import time
import shlex
import socket
import subprocess

import click
import redis

from fluent import sender

hostname = socket.gethostname()

def show_task(task):

    command = ['python'] + shlex.split(task["tool_path"])
    command += ['-d', task["input_uuid"]]
    command += ['-i', task["identifier"]]
    command += ['-o', task["output_uuid"]]

    #logger.emit(hostname, 'Running: {}'.format(' '.join(command)))
    print(' '.join(command))

@click.command()
@click.option('--redis-host', envvar='REDIS_HOST')
def main(redis_host):

    r = redis.StrictRedis(host=redis_host, port=6379)

    wq_len = r.llen('workqueue')
    print("{} items on work queue.".format(wq_len))

    wq_tail = r.lrange('workqueue', -1, -1)[0]

    task = r.hget('tasks', wq_tail)

    show_task(json.loads(task))


if __name__ == '__main__':
    main()
