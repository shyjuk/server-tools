# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models

from ..api import API


class ConfigCertServer(models.Model, API):
    """ It provides data handling for cert server configs. """

    _name = 'config.cert.server'
    _inherit = 'config.cert.abstract'
    _description = 'Config Cert Server'

    @api.multi
    def _compute_api_object(self):
        """ It computes the keys required for the JSON request. """
        for record in self:
            super(ConfigCertServer, record)._compute_api_object()
            record.api_object = self.cfssl.ConfigServer(
                sign_policy_default=record.api_object.sign_policy,
                sign_policies_add=record.api_object.sign_policies,
                auth_policies=record.api_object.auth_policies,
            )
