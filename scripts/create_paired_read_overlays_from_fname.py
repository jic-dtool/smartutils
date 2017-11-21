import os

import click

from dtool_cli.cli import dataset_uri_argument
from dtoolcore import DataSet


def is_file_extension_in_list(filename, extension_list):
    for extension in extension_list:
        if filename.endswith(extension):
            return True

    return False


def test_identifier_and_read_from_relpath():
    assert identifier_and_read_from_relpath("ERR188234_chrX_1.fastq.gz") == ("ERR188234_chrX", 1)  # NOQA
    assert identifier_and_read_from_relpath("ERR188234_chrX_2.fastq.gz") == ("ERR188234_chrX", 2)  # NOQA
    assert identifier_and_read_from_relpath("ERR188234_chrX_1.fq.gz") == ("ERR188234_chrX", 1)  # NOQA
    assert identifier_and_read_from_relpath("ERR188234_chrX_2.fq.gz") == ("ERR188234_chrX", 2)  # NOQA

    assert identifier_and_read_from_relpath("ERR188234_chrX_1.fastq") == ("ERR188234_chrX", 1)  # NOQA
    assert identifier_and_read_from_relpath("ERR188234_chrX_2.fastq") == ("ERR188234_chrX", 2)  # NOQA
    assert identifier_and_read_from_relpath("ERR188234_chrX_1.fq") == ("ERR188234_chrX", 1)  # NOQA
    assert identifier_and_read_from_relpath("ERR188234_chrX_2.fq") == ("ERR188234_chrX", 2)  # NOQA

    assert identifier_and_read_from_relpath("tmp/ERR188234_chrX_1.fastq.gz") == ("ERR188234_chrX", 1)  # NOQA


def identifier_and_read_from_relpath(relpath):
    fname = os.path.basename(relpath)  # ERR188234_chrX_2.fq.gz
    name = fname.split(".")[0]  # ERR188234_chrX_2
    name_parts = name.split("_")  # ERR188234, chrX, 2
    return "_".join(name_parts[:-1]), int(name_parts[-1])


def create_read1_overlay(dataset):

    read1_overlay = {}

    for i in dataset.identifiers:
        relpath = dataset.item_properties(i)['relpath']

        if not is_file_extension_in_list(
            relpath,
            ['fq', 'fq.gz', 'fastq', 'fastq.gz']
        ):
            continue

        identifier, read = identifier_and_read_from_relpath(relpath)
        if read == 1:
            read1_overlay[i] = True

    for i in dataset.identifiers:
        if i not in read1_overlay:
            read1_overlay[i] = False

    dataset.put_overlay('is_read1', read1_overlay)


def create_pair_id_overlay(dataset):

    data = {}
    for i in dataset.identifiers:
        relpath = dataset.item_properties(i)['relpath']

        if not is_file_extension_in_list(
            relpath,
            ['fq', 'fq.gz', 'fastq', 'fastq.gz']
        ):
            continue

        identifier, read = identifier_and_read_from_relpath(relpath)

        item = data.get(identifier, {})
        item[read] = i

        data[identifier] = item

    pair_id = {}
    for item in data.values():
        one, two = item.values()
        pair_id[one] = two
        pair_id[two] = one

    for i in dataset.identifiers:
        if i not in pair_id:
            pair_id[i] = None

    dataset.put_overlay('pair_id', pair_id)


@click.command()
@dataset_uri_argument
def cli(dataset_uri):

    dataset = DataSet.from_uri(dataset_uri)
    create_read1_overlay(dataset)
    create_pair_id_overlay(dataset)


if __name__ == '__main__':
    cli()
