import datetime
import json
import unittest
from unittest.mock import patch

from store import MemcacheClient
from tests.utils import cases
from scoring import get_score, get_interests


class TestScoring(unittest.TestCase):
    @cases([
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532",
          "birthday": datetime.datetime.strptime("12.05.1995", '%d.%m.%Y'), "gender": 2}, 5.0),
        ({"first_name": "Lewis", "last_name": "Hamilton"}, 0.5),
        ({"email": "no-reply@otus.ru", "phone": "79034852532"}, 3.0),
        ({"birthday": datetime.datetime.strptime("12.05.1995", '%d.%m.%Y'), "gender": 2}, 1.5),
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru"}, 2.0),
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532"}, 3.5),
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532",
         "birthday": datetime.datetime.strptime("12.05.1995", '%d.%m.%Y')}, 3.5),
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532",
         "birthday": datetime.datetime.strptime("12.05.1995", '%d.%m.%Y'), "gender": 2}, 5),
        ({}, 0)
        ])
    def test_get_score_with_unavailable_store(self, score_vars, expected_result):
        with patch.object(MemcacheClient, "cache_get", side_effect=[ConnectionRefusedError, TimeoutError]) as cache_get:
            with patch.object(MemcacheClient, "cache_set",
                              side_effect=[ConnectionRefusedError, TimeoutError]) as cache_set:
                store = MemcacheClient()
                self.assertEqual(expected_result, get_score(store, **score_vars))
                self.assertEqual(expected_result, get_score(store, **score_vars))

                self.assertEqual(2, cache_get.call_count)
                self.assertEqual(2, cache_set.call_count)

    @cases([
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532",
          "birthday": datetime.datetime.strptime("12.05.1995", '%d.%m.%Y'), "gender": 2}, 5.0),
        ({"first_name": "Lewis", "last_name": "Hamilton"}, 0.5),
        ({"email": "no-reply@otus.ru", "phone": "79034852532"}, 3.0),
        ({"birthday": datetime.datetime.strptime("12.05.1995", '%d.%m.%Y'), "gender": 2}, 1.5),
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru"}, 2.0),
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532"}, 3.5),
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532",
         "birthday": datetime.datetime.strptime("12.05.1995", '%d.%m.%Y')}, 3.5),
        ({"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532",
         "birthday": datetime.datetime.strptime("12.05.1995", '%d.%m.%Y'), "gender": 2}, 5),
        ])
    def test_get_score_with_available_store(self, score_vars, expected_result):
        with patch.object(MemcacheClient, "cache_get", side_effect=[None, expected_result]) as cache_get:
            with patch.object(MemcacheClient, "cache_set", return_value=True) as cache_set:
                store = MemcacheClient()
                self.assertEqual(expected_result, get_score(store, **score_vars))
                self.assertEqual(expected_result, get_score(store, **score_vars))

                self.assertEqual(2, cache_get.call_count)
                self.assertEqual(1, cache_set.call_count)

    @cases([1, ])
    def test_get_interests_with_unavailable_store(self, cid):
        with patch.object(MemcacheClient, "get", side_effect=[ConnectionRefusedError, TimeoutError]) as get:
            store = MemcacheClient()
            with self.assertRaises(expected_exception=ConnectionRefusedError):
                get_interests(store, cid)

            with self.assertRaises(expected_exception=TimeoutError):
                get_interests(store, cid)

            self.assertEqual(2, get.call_count)

    @cases([(1, json.dumps(["tox", "otus", "Lewis"]), ["tox", "otus", "Lewis"]),
            (2, None, [])])
    def test_get_interests_with_available_store(self, cid, return_interests, expected_result):
        with patch.object(MemcacheClient, "get", return_value=return_interests):
            store = MemcacheClient()
            self.assertEqual(expected_result, get_interests(store, cid))


if __name__ == "__main__":
    unittest.main()
