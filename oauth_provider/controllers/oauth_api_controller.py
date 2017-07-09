# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import http, fields
from odoo.addons.web.controllers.main import ensure_db

from ..exceptions import OauthApiException, OauthInvalidTokenException
from .oauth_mixin import OauthMixin

_logger = logging.getLogger(__name__)


class OauthApiController(OauthMixin):

    def _validate_model(self, model_name):
        """ Validate the access token & return a usable model.

        Args:
            model_name (str): Name of model to find.

        Returns:
            IrModel: Usable model object that matched model_name.

        Raises:
            OauthApiException: If the model is not found.
        """
        ensure_db()
        model_obj = http.request.env['ir.model'].search([
            ('model', '=', model_name),
        ])
        if not model_obj:
            raise OauthApiException('Model Not Found')
        return model_obj

    def _validate_token(self, access_token):
        """ Find the access token & return it if valid.

        Args:
            access_token (str): Access token that should be validated.

        Returns:
            OAuthProviderToken: Token record, if valid.

        Raises:
            OauthInvalidTokenException: When the token is invalid or expired.
        """
        ensure_db()
        token = self._get_access_token(access_token)
        if not token:
            raise OauthInvalidTokenException()
        return token

    @http.route('/oauth2/data',
                type='json',
                auth='none',
                methods=['GET'],
                )
    def data_read(self, access_token, model, *args, **kwargs):
        """ Return allowed information about the requested model.

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
        data = token.get_data(
            model,
            domain=kwargs.get('domain', []),
        )
        return data

    @http.route('/oauth2/data',
                type='json',
                auth='none',
                csrf=False,
                methods=['POST'],
                )
    def data_create(self, access_token, model, vals, *args, **kwargs):
        """ Create and return new record. """
        token = self._validate_token(access_token)
        self._validate_model(model)
        record = token.create_record(model, vals)
        return record.read()

    @http.route('/oauth2/data',
                type='json',
                auth='none',
                csrf=False,
                method=['PUT'],
                )
    def data_write(self, access_token, model, record_ids, vals,
                   *args, **kwargs):
        token = self._validate_token(access_token)
        self._validate_model(model)
        record = token.write_record(model, record_ids, vals)
        return record.read()

    @http.route('/oauth2/data',
                type='json',
                auth='none',
                csrf=False,
                method=['DELETE'],
                )
    def data_delete(self, access_token, model, record_ids, *args, **kwargs):
        token = self._validate_token(access_token)
        self._validate_model(model)
        token.delete_record(model, record_ids)
        return True
