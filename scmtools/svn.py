import pysvn
import re

from reviewboard.scmtools.core import \
    SCMException, FileNotFoundException, SCMTool, HEAD, PRE_CREATION

class SVNTool(SCMTool):
    def __init__(self, repository):
        self.repopath = repository.path
        if self.repopath[-1] == '/':
            self.repopath = self.repopath[:-1]

        SCMTool.__init__(self, repository)
        self.client = pysvn.Client()
        if repository.username:
            self.client.set_default_username(repository.username)
        if repository.password:
            self.client.set_default_password(repository.password)

        self.uses_atomic_revisions = True


    def get_file(self, path, revision=HEAD):
        if not path:
            raise FileNotFoundException(path, revision)

        try:
            return self.client.cat(self.__normalize_path(path),
                                   self.__normalize_revision(revision))
        except pysvn.ClientError, e:
            raise FileNotFoundException(path, revision, str(e))


    def parse_diff_revision(self, file_str, revision_str):
        if revision_str == "(working copy)":
            return file_str, HEAD

        m = re.match("^(\(([^\)]+)\)\s)?\(revision (\d+)\)$", revision_str)
        if not m:
            raise SCMException("Unable to parse diff revision header '%s'" %
                               revision_str)

        relocated_file = m.group(2)
        revision = m.group(3)

        if revision == "0":
            revision = PRE_CREATION

        if relocated_file:
            if not relocated_file.startswith("..."):
                raise SCMException("Unable to parse SVN relocated path '%s'" %
                                   relocated_file)

            file_str = "%s/%s" % (relocated_file[4:], file_str)

        return file_str, revision


    def get_filenames_in_revision(self, revision):
        r = self.__normalize_revision(revision)
        logs = self.client.log(self.repopath, r, r, True)

        if len(logs) == 0:
            return []
        elif len(logs) == 1:
            return [f['path'] for f in logs[0]['changed_paths']]
        else:
            assert False

    def __normalize_revision(self, revision):
        if revision == HEAD:
            r = pysvn.Revision(pysvn.opt_revision_kind.head)
        elif revision == PRE_CREATION:
            raise FileNotFoundException('', revision)
        else:
            r = pysvn.Revision(pysvn.opt_revision_kind.number, str(revision))

        return r

    def __normalize_path(self, path):
        if path.startswith(self.repopath):
            return path
        elif path[0] == '/':
            return self.repopath + path
        else:
            return self.repopath + "/" + path

    def get_fields(self):
        return ['basedir', 'diff_path']
