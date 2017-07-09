# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import werkzeug.wrappers

from odoo import http
from odoo.addons.web.controllers.main import ensure_db

#from ..http import _json_response


try:
    import oauthlib
    from oauthlib import oauth2
except ImportError:
    _logger.debug('Cannot `import oauthlib`.')


class OauthMixin(http.Controller):

    @classmethod
    def _get_access_token(cls, access_token):
        """ Verify access token and return record if valid.

        Args:
             access_token (str): OAuth2 access token to be validated.

        Returns:
            OauthProviderToken: Valid token record for use.
            NoneType: None if no matching token was found in the database.
            bool: False if the token was invalid.
        """
        token = http.request.env['oauth.provider.token'].search([
            ('token', '=', access_token),
        ])
        if not token:
            return None

        oauth2_server = token.client_id.get_oauth2_server()
        # Retrieve needed arguments for oauthlib methods
        uri, http_method, body, headers = cls._get_request_information()

        # Validate request information
        valid, oauthlib_request = oauth2_server.verify_request(
            uri, http_method=http_method, body=body, headers=headers,
        )

        if valid:
            return token

        return False

    @staticmethod
    def _get_request_information():
        """ Retrieve needed arguments for oauthlib methods.

        Returns:
            tuple: uri, http_method, body, headers
        """
        uri = http.request.httprequest.base_url
        http_method = http.request.httprequest.method
        body = oauthlib.common.urlencode(
            http.request.httprequest.values.items(),
        )
        headers = http.request.httprequest.headers

        return uri, http_method, body, headers

    @staticmethod
    def _json_response(data=None, status=200, headers=None):
        """ Returns a json response to the client.

        Args:
            data (mixed, optional): Response data to JSON encode.
            status (int, optional): HTTP status code to respond with.
            headers (dict, optional): Mapping of headers to apply to the request. If
                the `Content-Type` header is not defined, `application/json`
                will automatically be added.

        Returns:
            BaseResponse: Werkzeug response object based on the input.
        """
        return http.request._json_response(data)
