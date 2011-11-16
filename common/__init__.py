import marshal as cPickle
from ConfigParser import ConfigParser
from hashlib import sha1
import os, sys
import string

def readFile(filename):
  try:
    fp = open(filename)
    try:
      return fp.read()
    finally:
      fp.close()
  except IOError:
    print('Error reading %s: %s' % (filename, sys.exc_info()[1]))
    return None

class DxrConfig(object):
  def __init__(self, config, tree=None):
    self._tree = tree
    self._loadOptions(config, 'DXR')
    self.templates = os.path.abspath(config.get('DXR', 'templates'))
    if config.has_option('DXR', 'dxrroot'):
      self.dxrroot = os.path.abspath(config.get('DXR', 'dxrroot'))
    else:
      self.dxrroot = None

    self.wwwdir = os.path.abspath(config.get('Web', 'wwwdir'))
    self.virtroot = os.path.abspath(config.get('Web', 'virtroot'))
    if self.virtroot.endswith('/'):
      self.virtroot = self.virtroot[:-1]
    self.hosturl = config.get('Web', 'hosturl')
    if not self.hosturl.endswith('/'):
      self.hosturl += '/'

    if tree is None:
      self.trees = []
      for section in config.sections():
        if section == 'DXR' or section == 'Web':
          continue
        self.trees.append(DxrConfig(config, section))
    else:
      self.tree = self._tree
      self._loadOptions(config, tree)
      if not 'dbdir' in self.__dict__:
        # Build the dbdir from [wwwdir]/tree
        self.dbdir = os.path.join(self.wwwdir, tree + '-current', '.dxr_xref')
      self.isdblive = self.dbdir.startswith(self.wwwdir)

  def _loadOptions(self, config, section):
      for opt in config.options(section):
        self.__dict__[opt] = config.get(section, opt)
        if opt.endswith('dir'):
          self.__dict__[opt] = os.path.abspath(self.__dict__[opt])

  def getTemplateFile(self, name):
    tmpl = readFile(os.path.join(self.templates, name))
    tmpl = string.Template(tmpl).safe_substitute(**self.__dict__)
    return tmpl

  def getFileList(self):
    """ Returns an iterator of (relative, absolute) paths for the tree. """
    exclusions = self.__dict__.get("exclusions", ".hg\n.git\nCVS\n.svn\n.bzr\n.deps\n.libs")
    exclusions = exclusions.split()
    for root, dirs, files in os.walk(self.sourcedir, True):
      # Get the relative path to the source dir
      relpath = os.path.relpath(root, self.sourcedir)
      if relpath == '.':
        relpath = ''
      for f in files:
        # XXX: cxx-clang hack
        if f.endswith(".csv"): continue
        relfname = os.path.join(relpath, f)
        if any([f == ex for ex in exclusions]):
          continue
        yield (relfname, os.path.join(self.sourcedir, relfname))
      for ex in exclusions:
        if ex in dirs:
          dirs.remove(ex)

def load_config(path):
  config = ConfigParser()
  config.read(path)

  return DxrConfig(config)

__all__ = ['load_config', 'readFile']
