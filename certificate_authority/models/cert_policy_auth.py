# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from odoo.addons.tools import generate_random_password


class CertPolicyAuth(models.Model):
    """ It provides a CA Signature Auth Policy """

    _name = 'cert.policy.auth'
    _description = 'Cert Auth Policy'

    name = fields.Char(
        required=True,
    )
    key = fields.Char(
        required=True,
        default=lambda s: s._default_key(),
    )
    key_type = fields.Selection([
        ('standard', 'Standard'),
    ],
        default='standard',
        required=True,
    )
    api_object = fields.Binary(
        compute="_compute_api_object",
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique.'),
        ('key_uniq', 'UNIQUE(key)', 'Key must be unique.'),
    ]

    @api.model
    def _default_key(self):
        passwd = generate_random_password()
        return passwd.encode('hex')[:16]

    @api.multi
    def _compute_api_object(self):
        """ It computes the keys required for the JSON request """
        for record in self:
            record.api_object = self.cfssl.PolicyAuth({
                'name': record.name,
                'key': record.key,
                'key_type': record.key_type,
            })
