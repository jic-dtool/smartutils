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
        relpath = dataset.item_properties(identifier)['relpath']

        if is_file_extension_in_list(relpath, ['fq', 'fq.gz', 'fastq.gz']):
            abspath = dataset.item_content_abspath(identifier)
            metadata = extract_metadata_from_fastq_file(abspath)
            illumina_metadata_overlay[identifier] = metadata
        else:
            illumina_metadata_overlay[identifier] = None

    dataset.put_overlay(
        "illumina_metadata",
        illumina_metadata_overlay
    )


def find_paired_read(dataset, identifier):

    illumina_metadata = dataset.get_overlay('illumina_metadata')

    specific_metadata = illumina_metadata[identifier]

    del specific_metadata['read']

    matched_identifiers = []

    # Find all items in the dataset where the illumina metadata matches except
    # for the read tag
    for candidate_id in dataset.identifiers:
        candidate_metadata = illumina_metadata[candidate_id]
        if candidate_metadata is not None:
            if all(
                (candidate_metadata[k] == v)
                for k, v, in specific_metadata.items()
            ):
                matched_identifiers.append(candidate_id)

    # This should be exactly two items
    assert len(matched_identifiers) == 2

    matched_identifiers.remove(identifier)

    return matched_identifiers[0]


def create_read1_overlay(dataset):
    """Create an overlay that is True where the read is read 1 of a pair."""

    illumina_metadata = dataset.get_overlay('illumina_metadata')

    def is_read1(identifier):
        try:
            return illumina_metadata[identifier]['read'] == 1
        except TypeError:
            return False

    read1_overlay = {i: is_read1(i) for i in dataset.identifiers}

    dataset.put_overlay('is_read1', read1_overlay)


def create_pair_id_overlay(dataset):

    illumina_metadata = dataset.get_overlay('illumina_metadata')

    pair_id = {}

    for read1_id, value in illumina_metadata.items():
        if value:
            read2_id = find_paired_read(dataset, read1_id)
            pair_id[read1_id] = read2_id
            pair_id[read2_id] = read1_id

    for i in dataset.identifiers:
        if i not in pair_id:
            pair_id[i] = None

    dataset.put_overlay('pair_id', pair_id)



@click.command()
@dataset_uri_argument
def cli(dataset_uri):

    dataset = DataSet.from_uri(dataset_uri)

    create_illumina_metadata_overlay(dataset)
    create_read1_overlay(dataset)
    create_pair_id_overlay(dataset)

if __name__ == '__main__':
    cli()
