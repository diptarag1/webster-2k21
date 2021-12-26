from git import Repo as _Repo

from Repos.serverLocation import rw_dir


def get_bare_repo_by_name(owner, name):
    return _Repo(rw_dir + '/' + str(owner) + '/' + name + '.git')


def get_nonbare_repo_by_name(owner, name):
    return _Repo(rw_dir + '/' + str(owner) + '/' + name)