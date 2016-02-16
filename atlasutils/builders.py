import os
from pbr import git

class IBuilder():
    def get_tag(self):
        raise NotImplemented

    def pre_build_hook(self):
        raise NotImplemented


class GitBuilder(IBuilder):
    def __init__(self, git_repo=None):
        self.git_repo = git_repo if git_repo else os.getcwd()
        self.git_dir = os.path.join(self.git_repo, '.git')

    def get_tag(self):
        describe = git._run_git_command(['describe', '--always'], self.git_dir)
        return describe

    def pre_build_hook(self):
        git.write_git_changelog(self.git_dir, self.git_repo)