# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools
import werkzeug.wrappers

from odoo import http


def _oauth_route(route, **kw):
    routing = kw.copy()

    def decorator(f):
        if route:
            if isinstance(route, list):
                routes = route
            else:
                routes = [route]
            routing['routes'] = routes

        @functools.wraps(f)
        def response_wrap(*args, **kw):
            response = f(*args, **kw)
            return response

        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap

    return decorator


def route(route=None, **kw):
    """ Route method allowing for OAuth request type handling. """
    try:
        if routing['type'] == 'oauth':
            return _oauth_route(route, **kw)
    except KeyError:
        pass
    return http.route(route, **kw)


class OauthRequest(http.JsonRequest):
    """ Request handler for Oauth JSON API.

    Successful Response::

        {
            "version": "1.0",
            "status": 200,
            "result": { "key1": "val1", ... },
            "error": None,
        }

    Error Response::

        {
            "version": "1.0",
            "status": 500,
            "result": None,
            "error": {
                "code": 500,
                "message": "Canonical error message",
                "data": {
                    "debug": "Traceback (most recent call last)...",
                    "exception_type": "exception_code",
                    "message": "Canonical error message"<
                    "name": "werkzeug.exceptions.NotFound",
                    "arguments": [],
                },
            }
        }
    """

    VERSION = "1.0"
    _request_type = 'oauth'

    @classmethod
    def _json_response(cls, result=None, error=None, headers=None):
        """ Returns a JSON response to the OAuth client.

        Args:
            result (mixed, optional): User's requested data.
            error (dict, optional): Serialized error data (from
                `_handle_exception`).
            headers (dict, optional): Mapping of headers to apply to the
                request. If the `Content-Type` header is not defined,
                 `application/json` will automatically be added.

        Returns:
            BaseResponse: Werkzeug response object based on the input.
        """

        if headers is None:
            headers = {}

        response = {
            'version': cls.VERSION,
            'result': result,
            'error': error,
        }

        try:
            response['status'] = error['code']
        except (TypeError, KeyError):
            response['status'] = 200

        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        body = json.dumps(response)
        headers['Content-Length'] = len(body)

        return werkzeug.wrappers.BaseResponse(
            body, status=status, headers=headers,
        )

    @classmethod
    def _handle_exception(cls, exception):
        """Called within an except block to allow converting exceptions
           to arbitrary responses. Anything returned (except None) will
           be used as response."""
        error = {
            'data': serialize_exception(exception),
        }

        try:
            error['code'] = exception.code
        except AttributeError:
            error['code'] = 500

        try:
            error['message'] = exception.message
        except AttributeError:
            error['message'] = 'Internal Server Error'

        return cls._json_response(error=error)
