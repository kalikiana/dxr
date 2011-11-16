import marshal as cPickle
import languages
import os
import sys
import imp

all_plugins = None
def get_active_plugins(tree=None, dxrsrc=None):
  """ Return all plugins that are used by the tree.
      If tree is None, then all usable plugins are returned. """
  global all_plugins
  if all_plugins is None:
    if dxrsrc is None and tree is not None:
      dxrsrc = tree.dxrroot
    all_plugins = load_plugins(dxrsrc)

  if tree is not None and 'plugins' in tree.__dict__:
    plugins = [x.strip() for x in tree.plugins.split(',')]
    pluglist = []
    for name in plugins:
      for plugin in all_plugins:
        if plugin.__name__ == name:
          pluglist.append(plugin)
          break
      else:
        print "Warning: plugin %s not found" % name
    return pluglist
  def plugin_filter(module):
    return module.can_use(tree)
  return filter(plugin_filter, all_plugins)

def load_plugins(dxrsrc=None):
  if dxrsrc is None:
    dxrsrc = os.path.realpath(os.path.dirname(sys.argv[0]))
  dirs = os.listdir(os.path.join(dxrsrc, 'indexer/xref-tools'))
  all_plugins = []
  for dirname in dirs:
    fullname = os.path.join(dxrsrc, 'indexer/xref-tools', dirname)
    try:
      m = imp.find_module('indexer', [fullname])
      module = imp.load_module('dxr.' + dirname, m[0], m[1], m[2])
      all_plugins.append(module)
    except:
      print "Unable to load plugin %s" % dirname
      print sys.exc_info()
      pass
  return all_plugins

def store_big_blob(tree, blob):
  htmlroot = os.path.join(tree.wwwdir, tree.tree + '-current')
  dbdir = os.path.join(htmlroot, '.dxr_xref')
  # Commented out code: serialize byfile stuff independently, to avoid memory
  # wastage on very very large systems.
  #byfile = {}
  #filelist = set()
  #for plug in blob:
  #  try:
  #    byfile[plug] = blob[plug].pop("byfile")
  #    filelist.update(byfile[plug].keys())
  #  except KeyError:
  #    pass
  f = open(os.path.join(dbdir, 'index_blob.dat'), 'wb')
  try:
    cPickle.dump((blob, languages.language_data), f, 2)
  finally:
    f.close()
  #for fname in filelist:
  #  datname = 'fileindex_%s.dat' % (sha1(fname).hexdigest())
  #  f = open(os.path.join(dbdir, datname), 'wb')
  #  fdir = dict((p, byfile[p][fname]) for p in byfile if fname in byfile[p])
  #  try:
  #    cPickle.dump(fdir, f, 2)
  #  finally:
  #    f.close()
  #for plug in byfile:
  #  blob[plug]["byfile"] = byfile[plug]

def load_big_blob(tree):
  htmlroot = os.path.join(tree.wwwdir, tree.tree + '-current')
  dbdir = os.path.join(htmlroot, '.dxr_xref')
  f = open(os.path.join(dbdir, 'index_blob.dat'), 'rb')
  try:
    big_blob, languages.language_data = cPickle.load(f)
    return big_blob
  finally:
    f.close()

__all__ = ['get_active_plugins', 'store_big_blob', 'load_big_blob']
