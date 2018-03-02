import sys
import pkgutil

from Core.Post import Post

sys.modules['Post'] = Post

# Imports each extractor module in the Extractor package.  This makes it possible to dynamically search each
# BaseExtractor subclass during operation.
path = pkgutil.extend_path(__path__, __name__)
print('__path__: %s\npath: %s\n__name__: %s' % (__path__, path, __name__))
for importer, name, ispkg in pkgutil.walk_packages(path=path, prefix=__name__ + '.'):
    __import__(name)
