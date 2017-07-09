# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import http

from ..exceptions import RestApiException

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.oauth_provider.controllers.oauth_mixin import OauthMixin
except ImportError:
    _logger.warning('The `oauth_provider` module is not present in your '
                    'addons directory.')


class RestApiController(OauthMixin):

    API_VERSION = '1.0'

    @http.route(
        '/web_rest/%s/<string:model>/' % API_VERSION,
        type='json',
        auth='none',
        methods=['GET', 'POST'],
    )
    def rest_search(self, access_token, model, domain=None, *a, **kw):
        """ Return allowed information from all records, with optional query.

        Args:
            access_token (str): OAuth2 access token to utilize for the
                operation.
            model (str): Name of model to operate on.
            domain (list, optional): Domain to apply to the search, in the
                standard Odoo format. This will be appended to the scope's
                pre-existing filter.
        """
        token = self._validate_token(access_token)
        self._validate_model(model)
        data = token.get_data(model, domain=domain)
        return data

    @http.route(
        '/web_rest/%s/<string:model>/<int:rec_id>' % API_VERSION,
        type='json',
        auth='none',
        methods=['GET'],
    )
    def rest_read(self, access_token, model, record_ids, *a, **kw):
        """ Return allowed information from specific records.

        Args:
            access_token (str): OAuth2 access token to utilize for the
                operation.
            model (str): Name of model to operate on.
            record_ids (int or list of ints): ID of record(s) to get.
        """
        token = self._validate_token(access_token)
        self._validate_model(model)
        data = token.get_data(model, rec_id)
        return data

    @http.route(
        '/web_rest/%s/<string:model>/' % API_VERSION,
        type='json',
        auth='none',
        methods=['POST'],
    )
    def rest_create(self, access_token, model, vals, *args, **kwargs):
        """ Create and return new record. """
        token = self._validate_token(access_token)
        self._validate_model(model)
        record = token.create_record(model, vals)
        return record.read()

    @http.route('/oauth2/data',
                type='json',
                auth='none',
                methods=['PUT'],
                )
    def data_write(self, access_token, model, record_ids, vals,
                   *args, **kwargs):
        if isinstance(record_ids, int):
            record_ids = [record_ids]
        token = self._validate_token(access_token)
        self._validate_model(model)
        record = token.write_record(model, record_ids, vals)
        return record.read()

    @http.route('/oauth2/data',
                type='json',
                auth='none',
                methods=['DELETE'],
                )
    def data_delete(self, access_token, model, record_ids, *args, **kwargs):
        if isinstance(record_ids, int):
            record_ids = [record_ids]
        token = self._validate_token(access_token)
        self._validate_model(model)
        token.delete_record(model, record_ids)
        return True
