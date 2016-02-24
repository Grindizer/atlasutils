#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Here go you application specific code.
import registries
from builders import GitBuilder

def publish_ecr(source, name, region, tag, force):

    builder = GitBuilder(source)
    registry = registries.ECRRegistry(builder, region)
    registry.publish(source, name, tag, create_repo=force)

    return "{0}/{1}:{2}".format(registry.get_registry_name(),
                                name,
                                builder.get_tag())