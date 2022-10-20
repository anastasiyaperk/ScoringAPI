#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List
from weakref import WeakKeyDictionary
from scoring import get_score, get_interests

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
NoneType = type(None)


class UNSET:
    def __bool__(self):
        return False


class BaseField:
    def __init__(self, name: str, required: bool = False, nullable: bool = False):
        self.name = name
        self.required = required
        self.nullable = nullable

        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        if not self.nullable and value is None:
            raise ValueError(f"field '{self.name}' can not be nullable")
        elif self.required and isinstance(value, UNSET):
            raise ValueError(f"field '{self.name}' is required")

        self.data[instance] = value if not isinstance(value, UNSET) else None


class CharField(BaseField):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        if not isinstance(self.data[instance], (str, NoneType)):
            raise ValueError(f"field '{self.name}' must be string")


class ArgumentsField(BaseField):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        if not isinstance(self.data[instance], (dict, NoneType)):
            raise ValueError(f"field '{self.name}' must be dict")


class EmailField(CharField):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        value = self.data[instance]
        if not isinstance(value, NoneType) and not (isinstance(value, str) and value.find("@") != -1):
            raise ValueError(f"field '{self.name}' must be string with '@'")


class PhoneField(BaseField):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        value = self.data[instance]
        if not isinstance(value, NoneType) and not (len(str(value)) == 11 and str(value).startswith('7')):
            raise ValueError(f"field '{self.name}' must be string or integer, starts with '7' and have a length of 11")


class DateField(BaseField):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        if not isinstance(self.data[instance], NoneType):
            try:
                self.data[instance] = datetime.datetime.strptime(value, '%d.%m.%Y')
            except (ValueError, TypeError):
                raise ValueError(f"field '{self.name}' must be date with DD.MM.YYYY format")


class BirthDayField(DateField):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        value = self.data[instance]
        if not isinstance(value, NoneType) and (datetime.datetime.now() - value).days / 365.25 > 70:
            raise ValueError(f"field '{self.name}' must be a date that has passed no more than 70 years")


class GenderField(BaseField):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        value = self.data[instance]
        if not isinstance(value, NoneType) and value not in [0, 1, 2]:
            raise ValueError(f"field '{self.name}' must be integer with value 0, 1 or 2")


class ClientIDsField(BaseField):
    def __set__(self, instance, value):
        super().__set__(instance, value)
        if not isinstance(value, NoneType):
            if not isinstance(value, list) or not value or not (all([isinstance(item, int) for item in value])):
                raise ValueError(f"field '{self.name}' must be list with integers")


class ClientsInterestsRequest:
    client_ids = ClientIDsField(name="client_ids", required=True)
    date = DateField(name="date", required=False, nullable=True)

    def __init__(self, client_ids: List[int] = UNSET(), date: str = UNSET()):
        self.client_ids = client_ids
        self.date = date


class OnlineScoreRequest:
    first_name = CharField(name="first_name", required=False, nullable=True)
    last_name = CharField(name="last_name", required=False, nullable=True)
    email = EmailField(name="email", required=False, nullable=True)
    phone = PhoneField(name="phone", required=False, nullable=True)
    birthday = BirthDayField(name="birthday", required=False, nullable=True)
    gender = GenderField(name="gender", required=False, nullable=True)

    def __init__(self, first_name: str = UNSET(), last_name: str = UNSET(), email: str = UNSET(),
                 phone: str = UNSET(), birthday: str = UNSET(), gender: str = UNSET()):
        if not (max(map(bool, [phone and email, first_name and last_name, gender and birthday]))):
            raise ValueError("Must be at least one pair of 'phone-email', 'first_name-last_name' or 'gender-birthday'")
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.birthday = birthday
        self.gender = gender

    def to_dict(self, exclude_none: bool = False):
        args_ = {'first_name': self.first_name, 'last_name': self.last_name, 'email': self.email, 'phone': self.phone,
                 'birthday': self.birthday, 'gender': self.gender}
        if exclude_none:
            args_ = {item: value for item, value in args_.items() if value is not None}
        return args_


class MethodRequest:
    account = CharField(name="account", required=False, nullable=True)
    login = CharField(name="login", required=True, nullable=True)
    token = CharField(name="token", required=True, nullable=True)
    arguments = ArgumentsField(name="arguments", required=True, nullable=True)
    method = CharField(name="method", required=True, nullable=False)

    def __init__(self, login: str = UNSET(), token: str = UNSET(), arguments: dict = UNSET(), method: str = UNSET(),
                 account: str = UNSET()):
        self.account = account
        self.login = login
        self.token = token
        self.arguments = arguments
        self.method = method

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request: MethodRequest):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score(method_request: MethodRequest, ctx, store):
    arguments_ = OnlineScoreRequest(**method_request.arguments)

    ctx.update({'has': list(arguments_.to_dict(exclude_none=True))})

    if method_request.is_admin:
        return {"score": 42}, OK

    score = get_score(store=store,
                      phone=arguments_.phone,
                      email=arguments_.email,
                      birthday=arguments_.birthday,
                      gender=arguments_.gender,
                      first_name=arguments_.first_name,
                      last_name=arguments_.last_name)

    return {"score": score}, OK


def clients_interests(method_request: MethodRequest, ctx, store):
    arguments_ = ClientsInterestsRequest(**method_request.arguments)
    ctx.update({'nclients': len(arguments_.client_ids)})
    return {id_: get_interests(store, id_) for id_ in arguments_.client_ids}, OK


def method_handler(request, ctx, store):
    handler_functions = {
        "online_score": online_score,
        "clients_interests": clients_interests
    }

    body = request.get("body")
    if not body:
        return None, INVALID_REQUEST

    try:
        method_request = MethodRequest(**body)
    except ValueError as ex:
        return str(ex), INVALID_REQUEST

    if not check_auth(method_request):
        return None, FORBIDDEN

    try:
        response, code = handler_functions[method_request.method](method_request, ctx, store)
    except ValueError as ex:
        return str(ex), INVALID_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
