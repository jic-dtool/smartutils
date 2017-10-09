"""Check analysis progress."""

import click

from dtoolcore import DataSet, ProtoDataSet


@click.command()
@click.argument('input_uri')
@click.argument('output_uri')
def main(input_uri, output_uri):

    input_dataset = DataSet.from_uri(input_uri)
    output_dataset = ProtoDataSet.from_uri(output_uri)

    identifiers_to_process = set(input_dataset.identifiers)

    from_identifiers = []
    for handle in output_dataset._storage_broker.iter_item_handles():
        metadata = output_dataset._storage_broker.get_item_metadata(handle)
        from_identifiers.append(metadata["from"])

    unique_from_identifiers = set(from_identifiers)

    print(unique_from_identifiers)

    print("To process:")

    print(identifiers_to_process - unique_from_identifiers)



if __name__ == '__main__':
    main()
