"""Module for working with Illumina FASTQ files."""

import os
import gzip

import click

from dtool_cli.cli import dataset_uri_argument
from dtoolcore import DataSet


def is_file_extension_in_list(filename, extension_list):
    for extension in extension_list:
        if filename.endswith(extension):
            return True

    return False


def parse_fastq_title_line(fastq_title_line):

    def illumina_bool(x):
        if x == "Y":
            return True
        if x == "N":
            return False
        raise(ValueError)

    component_names = [
        ("instrument", str),
        ("run_number", int),
        ("flowcell_id", str),
        ("lane", int),
        ("tile", int),
        ("x_pos", int),
        ("y_pos", int),
        ("read", int),
        ("is_filtered", illumina_bool),
        ("control_number", int),
        ("index_sequence", str)
    ]

    assert fastq_title_line[0] == '@'

    words = fastq_title_line[1:].split(" ")

    assert len(words) == 2

    components = words[0].split(":") + words[1].split(":")

    assert len(components) == len(component_names)

    # We were going through a functional phase
    return {
        name: cast_func(component)
        for (name, cast_func), component
        in zip(component_names, components)
    }


def extract_metadata_from_fastq_file_object(fh):

    first_line = fh.readline().strip()

    try:
        first_line = first_line.decode('utf-8')
    except AttributeError:
        pass

    return parse_fastq_title_line(first_line)


def extract_metadata_from_fastq_file(filename):

    try:
        with open(filename) as fh:
            metadata = extract_metadata_from_fastq_file_object(fh)
    except UnicodeDecodeError:
        with gzip.open(filename, 'rb') as fh:
            metadata = extract_metadata_from_fastq_file_object(fh)

    return metadata


def create_illumina_metadata_overlay(dataset):
    """Create overlay derived from Illumina FQ metadata, and write it to
    dataset."""

    illumina_metadata_overlay = {} # dataset.empty_overlay()

    for identifier in dataset.identifiers:
        abspath = dataset.item_content_abspath(identifier)

        if is_file_extension_in_list(abspath, ['fq', 'fq.gz']):
            metadata = extract_metadata_from_fastq_file(abspath)
            illumina_metadata_overlay[identifier] = metadata
        else:
            illumina_metadata_overlay[identifier] = None

    dataset.put_overlay(
        "illumina_metadata",
        illumina_metadata_overlay
    )


@click.command()
@dataset_uri_argument
def cli(dataset_uri):

    dataset = DataSet.from_uri(dataset_uri)

    create_illumina_metadata_overlay(dataset)


if __name__ == '__main__':
    cli()
