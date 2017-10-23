"""Create smaller sample from a dataset."""

import os
import gzip
import errno
import shutil
import tempfile
from contextlib import contextmanager

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import click
import dtoolcore

from dtool_cli.cli import (
    dataset_uri_argument,
    CONFIG_PATH
)


TMPDIR_PREFIX = os.path.expanduser(
    "~/tmp/tmp"
)


@contextmanager
def temp_working_dir():
    working_dir = tempfile.mkdtemp(prefix=TMPDIR_PREFIX)

    try:
        yield working_dir
    finally:
        shutil.rmtree(working_dir)


def mkdir_parents(path):
    """Create the given directory path.
    This includes all necessary parent directories. Does not raise an error if
    the directory already exists.
    :param path: path to create
    """

    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def is_file_extension_in_list(filename, extension_list):
    for extension in extension_list:
        if filename.endswith(extension):
            return True

    return False


def minify(input_file, output_file, n=4000):

    print('minify from {} to {}'.format(input_file, output_file))

    output_dir = os.path.dirname(output_file)
    mkdir_parents(output_dir)
    with gzip.open(input_file, 'rb') as ifh:
        with gzip.open(output_file, 'wb') as ofh:
            for x in range(n):
                ofh.write(ifh.readline())


@click.command()
@dataset_uri_argument
@click.argument('dest_location_uri')
@click.option('--n', default=4000)
def dminify(dataset_uri, dest_location_uri, n):

    parent_dataset = dtoolcore.DataSet.from_uri(dataset_uri)

    # Generate the destination URI.
    parsed_location_uri = urlparse(dest_location_uri)
    prefix = parsed_location_uri.path
    storage = parsed_location_uri.scheme
    if storage == "":
        storage = "file"

    dest_dataset_name = "{}_minified_{}".format(parent_dataset.name, n)
    admin_metadata = dtoolcore.generate_admin_metadata(dest_dataset_name)
    dest_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        prefix=prefix,
        storage=storage,
        config_path=CONFIG_PATH)
    try:
        dest_dataset.create()
    except dtoolcore.storagebroker.StorageBrokerOSError as err:
        raise click.UsageError(str(err))

    for identifier in parent_dataset.identifiers:
        entry = parent_dataset.item_properties(identifier)
        if is_file_extension_in_list(entry['relpath'], ['.fq', '.fq.gz']):
            input_file_path = parent_dataset.item_content_abspath(identifier)
            with temp_working_dir() as tmp:
                output_file_path = os.path.join(
                    tmp,
                    entry['relpath']
                )
            minify(input_file_path, output_file_path, n)

            dest_dataset.put_item(output_file_path, entry['relpath'])

    readme_content = parent_dataset.get_readme_content()
    readme_content += "\nminified_from_UUID: {}".format(parent_dataset.uuid)
    readme_content += "\nminified_from_URI: '{}'".format(parent_dataset.uri)

    dest_dataset.put_readme(readme_content)

    dest_dataset.freeze()

    click.secho("Created: {}".format(dest_dataset.uri))


if __name__ == '__main__':
    dminify()
