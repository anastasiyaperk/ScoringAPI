import unittest
from unittest.mock import patch

import pymemcache
from store import MemcacheClient


class TestStore(unittest.TestCase):
    def test_retry_cache_set(self):
        with patch.object(pymemcache.client.base.Client, "set", side_effect=ConnectionRefusedError) as _set:
            memcl = MemcacheClient()
            with self.assertRaises(expected_exception=ConnectionRefusedError):
                try:
                    memcl.cache_set("test_key", "test_value")
                except ConnectionRefusedError:
                    self.assertEqual(3, _set.call_count)
                    raise

    def test_not_retry_cache_set(self):
        with patch.object(pymemcache.client.base.Client, "set", side_effect=TimeoutError) as _set:
            memcl = MemcacheClient()
            with self.assertRaises(expected_exception=TimeoutError):
                try:
                    memcl.cache_set('test_key', 'test_value')
                except TimeoutError:
                    self.assertEqual(1, _set.call_count)
                    raise

    def test_retry_cache_get(self):
        with patch.object(pymemcache.client.base.Client, "get", side_effect=ConnectionRefusedError) as _get:
            memcl = MemcacheClient()
            with self.assertRaises(expected_exception=ConnectionRefusedError):
                try:
                    memcl.cache_get('test_key')
                except ConnectionRefusedError:
                    self.assertEqual(3, _get.call_count)
                    raise

    def test_not_retry_cache_get(self):
        with patch.object(pymemcache.client.base.Client, "get", side_effect=TimeoutError) as _get:
            memcl = MemcacheClient()
            with self.assertRaises(expected_exception=TimeoutError):
                try:
                    memcl.cache_get('test_key')
                except TimeoutError:
                    self.assertEqual(1, _get.call_count)
                    raise

    def test_retry_get(self):
        with patch.object(pymemcache.client.base.Client, "get", side_effect=ConnectionRefusedError) as _get:
            memcl = MemcacheClient()
            with self.assertRaises(expected_exception=ConnectionRefusedError):
                try:
                    memcl.get('test_key')
                except ConnectionRefusedError:
                    self.assertEqual(3, _get.call_count)
                    raise

    def test_not_retry_get(self):
        with patch.object(pymemcache.client.base.Client, "get", side_effect=TimeoutError) as _get:
            memcl = MemcacheClient()
            with self.assertRaises(expected_exception=TimeoutError):
                try:
                    memcl.get('test_key')
                except TimeoutError:
                    self.assertEqual(1, _get.call_count)
                    raise


if __name__ == "__main__":
    unittest.main()
