# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.oauth_provider import exceptions

from odoo import _


class RestApiException(exceptions.OauthApiException):
    pass
