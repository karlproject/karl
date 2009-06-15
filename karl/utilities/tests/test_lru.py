import unittest

class LRUCacheTests(unittest.TestCase):
    def _getTargetClass(self):
        from karl.utilities.lru import LRUCache
        return LRUCache

    def _makeOne(self, size):
        return self._getTargetClass()(size)

    def test_size_lessthan_1(self):
        self.assertRaises(ValueError, self._makeOne, 0)

    def test_it(self):
        cache = self._makeOne(3)
        self.assertEqual(cache.get('a'), None)
        cache['a'] = '1'
        pos, value = cache.data.get('a')
        self.assertEqual(cache.clock[pos]['ref'], True)
        self.assertEqual(cache.clock[pos]['key'], 'a')
        self.assertEqual(value, '1')
        self.assertEqual(cache.get('a'), '1')
        self.assertEqual(cache.hand, pos+1)
        pos, value = cache.data.get('a')
        self.assertEqual(cache.clock[pos]['ref'], True)
        self.assertEqual(cache.hand, pos+1)
        self.assertEqual(len(cache.data), 1)
        cache['b'] = '2'
        pos, value = cache.data.get('b')
        self.assertEqual(cache.clock[pos]['ref'], True)
        self.assertEqual(cache.clock[pos]['key'], 'b')
        self.assertEqual(len(cache.data), 2)
        cache['c'] = '3'
        pos, value = cache.data.get('c')
        self.assertEqual(cache.clock[pos]['ref'], True)
        self.assertEqual(cache.clock[pos]['key'], 'c')
        self.assertEqual(len(cache.data), 3)
        pos, value = cache.data.get('a')
        self.assertEqual(cache.clock[pos]['ref'], True)
        cache.get('a')
        cache['d'] = '4'
        self.assertEqual(len(cache.data), 3)
        self.assertEqual(cache.data.get('b'), None)
        cache['e'] =  '5'
        self.assertEqual(len(cache.data), 3)
        self.assertEqual(cache.data.get('c'), None)
        self.assertEqual(cache.get('d'), '4')
        self.assertEqual(cache.get('e'), '5')
        self.assertEqual(cache.get('a'), '1')
        self.assertEqual(cache.get('b'), None)
        self.assertEqual(cache.get('c'), None)
                         
   
