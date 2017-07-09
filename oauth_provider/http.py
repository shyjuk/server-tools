# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import functools
import json

from odoo import http


VERSION = "1.0"


old_handle_exception = http.JsonRequest._handle_exception
old_json_response = http.JsonRequest._json_response


def _handle_exception(self, exception):
    """ Override the original method to handle Werkzeug exceptions.

    Args:
        exception (Exception): Exception object that is being thrown.

    Returns:
        BaseResponse: JSON Response.
    """

    # For some reason a try/except here still raised...
    code = getattr(exception, 'code', None)
    if code is None:
        return old_handle_exception(
            self, exception,
        )

    error = {
        'data': http.serialize_exception(exception),
        'code': code,
    }

    try:
        error['message'] = exception.message
    except AttributeError:
        error['message'] = 'Internal Server Error'

    return self._json_response(error=error)

def _json_response(self, result=None, error=None, jsonrpc=True,
                   headers=None):
    """ Returns a JSON response to the OAuth client.

    If `jsonrpc` is set to `True`, this method will provide default Odoo
    functionality.

    If `jsonrp` is set to `False`, this method will return a JSON response
    that is more appropriate for non RPC ingestion. The response will be
    provided under a proper HTTP status code, and will be in the following
    format::

        {
            "version": str,
            "status_code": int,
            "result": dict,
            "error": dict,
        }

    Args:
        result (mixed, optional): User's requested data.
        error (dict, optional): Serialized error data (from
            `_handle_exception`).
        jsonrpc (bool, optional): Set to False in order to respond without
            JSON-RPC, and instead send a simple JSON response.
        headers (dict, optional): Mapping of headers to apply to the
            request. If the `Content-Type` header is not defined,
             `application/json` will automatically be added.

    Returns:
        Response: Werkzeug response object based on the input.
    """

    if jsonrpc and not self.env.context.get('oauth_api'):
        return old_json_response(
            self, result, error,
        )

    if headers is None:
        headers = {}

    response = {
        'version': VERSION,
        'result': result,
        'error': error,
    }

    try:
        response['status_code'] = error['code']
    except (TypeError, KeyError):
        response['status_code'] = 200

    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'

    body = json.dumps(response)
    headers['Content-Length'] = len(body)

    return http.Response(
        body, status=response['status_code'], headers=headers,
    )


# http.JsonRequest._json_response = _json_response
http.JsonRequest._handle_exception = _handle_exception
