# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import http, fields
from odoo.addons.web.controllers.main import ensure_db

from ..http import route
from ..exceptions import OauthApiException, OauthInvalidTokenException
from .oauth2_mixin import OauthMixin

_logger = logging.getLogger(__name__)


class OauthApiController(OauthMixin):

    def _get_model(self, model_name):
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

    def _get_token(self, access_token):
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

    @route('/oauth2/data',
           type='oauth',
           auth='none',
           methods=['GET'],
           )
    def data_get(self, access_token=None, model=None, *args, **kwargs):
        """ Return allowed information about the requested model.

        Args:
            access_token (str): OAuth2 access token to utilize for the
                operation.
            model (str): Name of model to operate on.
            domain (list, optional): Domain to apply to the search, in the
                standard Odoo format. This only applies if there is not
                already a filter on the token scope. Otherwise, the scope
                will take precedence.
        """
        token = self._get_token(access_token)
        model = self._get_model(model)
        data = token.get_data_for_model(
            model,
            domain=kwargs.get('domain', []),
        )
        return self._json_response(data=data)

    @route('/oauth2/data',
           type='oauth',
           auth='none',
           csrf=False,
           methods=['POST'],
           )
    def data_post(self, access_token=None, model=None, record_ids=None,
                  *args, **kwargs):
        """ Update the records  """
        token = self._get_token(access_token)
        model = self._get_model(model)
        raise OauthInvalidTokenException()
