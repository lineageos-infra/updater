#!/usr/bin/env python3

class AppException(Exception):
    status_code = 400

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def to_dict(self):
        return {'message': self.message}


class DeviceNotFoundException(AppException):
    status_code = 404


class UpstreamApiException(AppException):
    status_code = 502


class InvalidValueException(AppException):
    status_code = 400
