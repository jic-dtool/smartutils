"""Determine work and load queue."""

import json

import click
import redis

from dtoolcore import DataSet


def identifiers_where_overlay_is_true(dataset, overlay_name):

    overlay = dataset.access_overlay(overlay_name)

    selected = [identifier
                for identifier in dataset.identifiers
                if overlay[identifier]]

    return selected


def make_task(input_uuid, identifier, output_uuid):
    task = {
        "tool_path": "/scripts/seedcellsize.py",
        "input_uuid": input_uuid,
        "identifier": identifier,
        "output_uuid": output_uuid,
    }

    return json.dumps(task)


@click.command()
@click.argument('input_uri')
@click.argument('output_uri')
@click.option('--redishost', envvar='REDISHOST', default='10.0.0.4')
def main(input_uri, output_uri, redishost):
    r = redis.StrictRedis(redishost, port=6379)

    dataset = DataSet.from_uri(input_uri)

    for i in dataset.identifiers:
        task = make_task(input_uri, i, output_uri)
        r.hmset('tasks', {i:  task})
        r.lpush('workqueue', i)


if __name__ == '__main__':
    main()
