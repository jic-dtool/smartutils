"""Generate SLURM scripts."""

import click
from jinja2 import Environment

from dtoolcore import DataSet, ProtoDataSet


TEMPLATE = """#!/bin/bash

#SBATCH --partition={{ partition }}
#SBATCH --mem={{ jobmem }}

singularity exec /jic/software/testing/convertlif/0.1.0/convertlif \\
  python /scripts/convertlif.py \\
  -d {{ input_uri }} \\
  -o {{ output_uri }} \\
  -i {{ identifier }}
"""


def generate_scripts_for_identifier_list(
    input_uri,
    output_uri,
    identifier_list
):
    env = Environment(keep_trailing_newline=True)

    template = env.from_string(TEMPLATE)

    job_params = {
        'partition': 'rg-mh',
        'jobmem': '6000',
        'input_uri': input_uri,
        'output_uri': output_uri
    }

    for identifier in identifier_list:
        job = job_params.copy()
        job.update({'identifier': identifier})
        print(template.render(job))


@click.command()
@click.argument('input_uri')
@click.argument('output_uri')
def main(input_uri, output_uri):

    input_dataset = DataSet.from_uri(input_uri)

    all_identifiers = input_dataset.identifiers

    completed = set([u'a80388191422d76c73e4ac1daff30fe0ea896448', u'd09d393efe7ceaf9719ff5ddb1f7b725ed7f27cf', u'2401aa1b5d8cde9b79bcec72e270905d30b966fc', u'd662738e7476c866997f247ed910f6ebc741d52e'])

    to_process = set(all_identifiers) - completed

    generate_scripts_for_identifier_list(
        input_uri,
        output_uri,
        list(to_process)
    )


if __name__ == '__main__':
    main()
