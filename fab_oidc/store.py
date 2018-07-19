from werkzeug.contrib.cache import BaseCache
from collections import UserDict


class WerkzeugCacheBackedCredentialStore(UserDict):

    def __init__(self, cache):
        self.cache = cache # type: BaseCache

    def __setitem__(self, key, value):
        return self.cache.set(key, value)

    def __getitem__(self, key):
        return self.cache.get(key)

    def __contains__(self, key):
        return self.cache.has(key)

    def __repr__(self):
        return 'WerkzeugCache: {}'.format(str(self.cache.__class__))
