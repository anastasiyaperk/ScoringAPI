import datetime
import unittest
from unittest.mock import patch

import api
from api import UNSET

from tests.utils import cases


class Fields(unittest.TestCase):
    class TestFields:
        x = None

    @cases([
        ({"required": True, "nullable": True}, "some_string"),
        ({"required": True, "nullable": False}, "some_string"),
        ])
    def test_ok_base_field(self, init_vars: dict, value):
        with patch.object(self.TestFields, "x", api.BaseField(name="x", **init_vars)):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(value, fields.x, (init_vars, value))

    @cases([
        ({"required": True, "nullable": True}, UNSET()),
        ({"required": True, "nullable": False}, UNSET()),
        ({"required": True, "nullable": False}, None),
        ({"required": False, "nullable": False}, None),
        ])
    def test_invalid_base_field(self, init_vars: dict, value):
        with patch.object(self.TestFields, "x", api.BaseField(name="x", **init_vars)):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value

    @cases(["some_string", "", " "])
    def test_ok_char_field(self, value):
        with patch.object(self.TestFields, "x", api.CharField(name="x")):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(value, fields.x, value)

    @cases([1, 1., {}, []])
    def test_invalid_char_field(self, value):
        with patch.object(self.TestFields, "x", api.CharField(name="x")):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value

    @cases([{}, {"some_key": "some_string"}])
    def test_ok_arguments_field(self, value):
        with patch.object(self.TestFields, "x", api.ArgumentsField(name="x")):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(value, fields.x, value)

    @cases([1, 1., "some_string", "", " ", []])
    def test_invalid_arguments_field(self, value):
        with patch.object(self.TestFields, "x", api.ArgumentsField(name="x")):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value

    @cases(["test@mail.com", "no-reply@otus.ru"])
    def test_ok_email_field(self, value):
        with patch.object(self.TestFields, "x", api.EmailField(name="x")):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(value, fields.x, value)

    @cases([1, 1., "some_string", "", " ", [], {}, "no-reply#otus.ru"])
    def test_invalid_email_field(self, value):
        with patch.object(self.TestFields, "x", api.EmailField(name="x")):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value

    @cases(["79123565900", 79123565900])
    def test_ok_phone_field(self, value):
        with patch.object(self.TestFields, "x", api.PhoneField(name="x")):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(value, fields.x, value)

    @cases([1, 1., "some_string", "", " ", [], {}, "89123565900", 89123565900, "891235659009", 891235659009])
    def test_invalid_phone_field(self, value):
        with patch.object(self.TestFields, "x", api.PhoneField(name="x")):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value

    @cases(["18.05.1995"])
    def test_ok_date_field(self, value):
        with patch.object(self.TestFields, "x", api.DateField(name="x")):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(datetime.datetime.strptime(value, '%d.%m.%Y'), fields.x, value)

    @cases([1, 1., "some_string", "", " ", [], {}, "05.18.1995", "1995.05.18", "1995.18.05", "05.18.95"])
    def test_invalid_date_field(self, value):
        with patch.object(self.TestFields, "x", api.DateField(name="x")):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value

    @cases(["18.05.1995"])
    def test_ok_birthday_field(self, value):
        with patch.object(self.TestFields, "x", api.BirthDayField(name="x")):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(datetime.datetime.strptime(value, '%d.%m.%Y'), fields.x, value)

    @cases([1, 1., "some_string", "", " ", [], {}, "18.05.1952"])
    def test_invalid_birthday_field(self, value):
        with patch.object(self.TestFields, "x", api.BirthDayField(name="x")):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value

    @cases([0, 1, 2])
    def test_ok_gender_field(self, value):
        with patch.object(self.TestFields, "x", api.GenderField(name="x")):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(value, fields.x, value)

    @cases(["some_string", "", " ", [], {}, -1, 1., 3])
    def test_invalid_gender_field(self, value):
        with patch.object(self.TestFields, "x", api.GenderField(name="x")):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value

    @cases([[1], [1, 2, 3]])
    def test_ok_client_ids_field(self, value):
        with patch.object(self.TestFields, "x", api.ClientIDsField(name="x")):
            fields = self.TestFields()
            fields.x = value
            self.assertEqual(value, fields.x, value)

    @cases([1, 1., "some_string", "", " ", {}, [], [1.], ["some_string"], [[1]]])
    def test_invalid_client_ids_field(self, value):
        with patch.object(self.TestFields, "x", api.ClientIDsField(name="x")):
            fields = self.TestFields()
            with self.assertRaises(ValueError):
                fields.x = value


class RequestFields(unittest.TestCase):
    @cases([
        {"first_name": "Lewis", "last_name": "Hamilton"},
        {"email": "no-reply@otus.ru", "phone": "79034852532"},
        {"birthday": "12.05.1995", "gender": 2},
        {"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru"},
        {"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532"},
        {"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532",
         "birthday": "12.05.1995"
         },
        {"first_name": "Lewis", "last_name": "Hamilton", "email": "no-reply@otus.ru", "phone": "79034852532",
         "birthday": "12.05.1995", "gender": 2
         },
        ])
    def test_ok_online_score_field(self, init_vars: dict):
        fields = api.OnlineScoreRequest(**init_vars)
        self.assertEqual(init_vars.get("first_name"), fields.first_name, init_vars)
        self.assertEqual(init_vars.get("last_name"), fields.last_name, init_vars)
        self.assertEqual(init_vars.get("email"), fields.email, init_vars)
        self.assertEqual(init_vars.get("phone"), fields.phone, init_vars)
        self.assertEqual(init_vars.get("gender"), fields.gender, init_vars)
        date = init_vars.get("birthday")
        self.assertEqual(datetime.datetime.strptime(date, '%d.%m.%Y') if date else None, fields.birthday, init_vars)

    @cases([
        {"first_name": "Lewis"},
        {"last_name": "Hamilton"},
        {"email": "no-reply@otus.ru"},
        {"phone": "79034852532"},
        {"birthday": "12.05.1995"},
        {"gender": 2},
        {"first_name": "Lewis", "email": "no-reply@otus.ru"},
        {"first_name": "Lewis", "phone": "79034852532"},
        {"first_name": "Lewis", "birthday": "12.05.1995"},
        {"first_name": "Lewis", "gender": 2},
        {"last_name": "Hamilton", "email": "no-reply@otus.ru"},
        {"last_name": "Hamilton", "phone": "79034852532"},
        {"last_name": "Hamilton", "birthday": "12.05.1995"},
        {"last_name": "Hamilton", "gender": 2},
        {"email": "no-reply@otus.ru", "birthday": "12.05.1995"},
        {"email": "no-reply@otus.ru", "gender": 2},
        {"phone": "79034852532", "birthday": "12.05.1995"},
        {"phone": "79034852532", "gender": 2},
        {"first_name": "Lewis", "email": "no-reply@otus.ru", "birthday": "12.05.1995"},
        {"first_name": "Lewis", "phone": "79034852532", "birthday": "12.05.1995"},
        {"first_name": "Lewis", "email": "no-reply@otus.ru", "gender": 2},
        {"first_name": "Lewis", "phone": "79034852532", "gender": 2},
        {"last_name": "Hamilton", "email": "no-reply@otus.ru", "birthday": "12.05.1995"},
        {"last_name": "Hamilton", "phone": "79034852532", "birthday": "12.05.1995"},
        {"last_name": "Hamilton", "email": "no-reply@otus.ru", "gender": 2},
        {"last_name": "Hamilton", "phone": "79034852532", "gender": 2},
        ])
    def test_invalid_online_score_field(self, init_vars: dict):
        with self.assertRaises(ValueError):
            api.OnlineScoreRequest(**init_vars)

    @cases([
        {"account": "an&perk", "login": "a&p", "token": "85939565bfusj455932fjks84", "arguments": {}, "method": "test"},
        {"login": "a&p", "token": "85939565bfusj455932fjks84", "arguments": {}, "method": "test"},
        {"account": None, "login": None, "token": None, "arguments": None, "method": "test"},
        ])
    def test_ok_method_field(self, init_vars: dict):
        fields = api.MethodRequest(**init_vars)
        self.assertEqual(init_vars.get("account"), fields.account, init_vars)
        self.assertEqual(init_vars.get("login"), fields.login, init_vars)
        self.assertEqual(init_vars.get("token"), fields.token, init_vars)
        self.assertEqual(init_vars.get("arguments"), fields.arguments, init_vars)
        self.assertEqual(init_vars.get("method"), fields.method, init_vars)

    @cases([
        {"account": "an&perk", "token": "85939565bfusj455932fjks84", "arguments": {}, "method": "test"},
        {"account": "an&perk", "login": "a&p", "arguments": {}, "method": "test"},
        {"account": "an&perk", "login": "a&p", "token": "85939565bfusj455932fjks84", "method": "test"},
        {"account": "an&perk", "login": "a&p", "token": "85939565bfusj455932fjks84", "arguments": {}},
        {"account": "an&perk", "login": "a&p", "token": "85939565bfusj455932fjks84", "arguments": {}, "method": None},
        ])
    def test_invalid_method_field(self, init_vars: dict):
        with self.assertRaises(ValueError):
            api.MethodRequest(**init_vars)

    @cases([
        {"client_ids": [1, 2]},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [1, 2], "date": None},
        ])
    def test_ok_clients_interests_field(self, init_vars: dict):
        fields = api.ClientsInterestsRequest(**init_vars)
        self.assertEqual(init_vars.get("client_ids"), fields.client_ids, init_vars)
        date = init_vars.get("date")
        self.assertEqual(datetime.datetime.strptime(date, '%d.%m.%Y') if date else None, fields.date, init_vars)

    @cases([
        {},
        {"date": "19.07.2017"},
        {"client_ids": None, "date": "19.07.2017"},
        ])
    def test_invalid_clients_interests_field(self, init_vars: dict):
        with self.assertRaises(ValueError):
            api.ClientsInterestsRequest(**init_vars)


if __name__ == "__main__":
    unittest.main()
