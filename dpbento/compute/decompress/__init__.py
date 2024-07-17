from os.path import dirname, basename, isfile, join
import glob
from importlib import import_module

# Allow import of all modules in this directory
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
print('debug: compute.decompress has these modules:', __all__)
# dynamically import all modules in this directory
for mod in __all__:
    print('importing compute.decompress.' + mod + '...')
    import_module('compute.decompress' + '.' + mod)