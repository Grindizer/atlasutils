#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import click
import os
import registries
import atlasutils


@click.group()
def main():
    pass


@main.command()
@click.option('-s', '--source', required=True,
              default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
              help=u"Directory where the git source to publish is")
@click.option('-n', '--name', required=True, type=click.STRING, help=u"Name of the docker repository to publish to")
@click.option('-r', '--region', required=True, default='us-east-1',
                   help=u"ecr region name")
@click.option('-t', '--tag', required=False, default=None, help=u"tag")
@click.option('-f', '--force', required=True, default=False, help=u"Create the repository if it does not exist.")
def publish_ecr(source, name, region, tag, force):
    click.secho("/\\tlas <~> 'publish_ecr'", fg='green')
    # setup log function.
    registries.log = click.secho
    atlasutils.publish_ecr(source, name, region, tag, force)

if __name__ == '__main__':
    main()
