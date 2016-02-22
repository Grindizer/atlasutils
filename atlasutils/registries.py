
from botocore.session import get_session
from base64 import b64decode
from docker import client, errors
from docker.utils import kwargs_from_env
import sys
from utils import log_push, log_build

def log(*arg, **kw):
    return


class IRegistry():
    """ Based interface fot registry plugin. """
    builder = "IBuilder object."

    def get_registry_name(self):
        raise NotImplemented

    def login(self):
        raise NotImplemented

    def build(self, repo_dir, repo_name, forced_tag=None):
        raise NotImplemented

    def publish(self, repo_dir, name, tag):
        raise NotImplemented

# TODO: factorize common registry work in super class: log outputing included.
class ECRRegistry(IRegistry):
    def __init__(self, builder, region):
        self.builder = builder
        self.region = region
        self.docker_client = get_docker_client()

    def _get_registry_info(self):
        ecr_client = get_session().create_client('ecr', self.region)
        result = ecr_client.get_authorization_token()
        auth = result['authorizationData'][0]
        auth_token = b64decode(auth['authorizationToken']).decode()
        username, password = auth_token.split(':')
        return username, password, 'none', auth['proxyEndpoint']

    def get_registry_name(self):
        _, _, _, endpoint = self._get_registry_info()
        if endpoint.startswith('https://'):
            return endpoint[8:]
        elif endpoint.startswith('http://'):
            return endpoint[7:]
        else:
            return endpoint

    def login(self):
        credentials = self._get_registry_info()
        reg = credentials[3]
        try:
            result = self.docker_client.login(*credentials, reauth=True)
        except (errors.APIError, errors.DockerException) as e:
            log("Login to registry '{0}' failed:".format(reg), fg='red')
            log(repr(e), fg='red')
            sys.exit(1)
        else:
            log("Login to registry '{0}': {1}".format(reg, result['Status']), fg='green')

    def build(self, repo_dir, repo_name, tag=None):
        name = ":".join([repo_name, tag])
        log("Running pre_build_hook ...")
        self.builder.pre_build_hook()

        log("Running build for '{0}'".format(name))
        result = self.docker_client.build(repo_dir, name, quiet=False, forcerm=True, stream=True, decode=True)
        image_id = log_build(result, log)

        return image_id

    def publish(self, repo_dir, repo_name, forced_tag=None, create_repo=False):
        tag = forced_tag if forced_tag else self.builder.get_tag()
        log("Tag value: {0}".format(tag))

        image_id = self.build(repo_dir, repo_name, tag)
        if not image_id:
            return

        full_name = '/'.join([self.get_registry_name(), repo_name])
        self.docker_client.tag(image_id, full_name, tag, True)

        self.login()
        if create_repo:
            # TODO: add ability to create the repo on ecr if we have the right.
            pass

        log('Pushing images {0}:{1}'.format(full_name, tag))
        result = self.docker_client.push(full_name, tag, stream=True)
        log_push(result, log)


def get_docker_client():
    kwargs = kwargs_from_env()
    kwargs['tls'].assert_hostname = False
    return client.Client(**kwargs)

def get_logger():
    return lambda x: x