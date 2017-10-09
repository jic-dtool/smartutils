"""Varcan smart tool."""

import os

import click

from dtoolcore import DataSet


def create_useful_name_overlay(dataset, name_func):

    useful_name_overlay = {
        identifier: name_func(dataset, identifier)
        for identifier in dataset.identifiers
    }

    dataset.put_overlay("useful_name", useful_name_overlay)


def strip_final_ext(dataset, identifier):
    path = dataset.item_properties(identifier)['relpath']

    return path.rsplit('.', 1)[0]


@click.command()
@click.argument('uri')
def main(uri):

    dataset = DataSet.from_uri(uri)

    create_useful_name_overlay(dataset, strip_final_ext)


if __name__ == '__main__':
    main()
