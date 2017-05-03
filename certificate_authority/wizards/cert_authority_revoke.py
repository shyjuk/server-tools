# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CertAuthorityRevoke(models.TransientModel):
    """ It revokes a Cert Request. """

    _name = 'cert.authority.revoke'
    _description = 'Cert Authority Revoke'

    cert_authority_id = fields.Many2one(
        string='Cert Authority',
        comodel_name='cert.authority',
        required=True,
        readonly=True,
    )
    cert_id = fields.Many2one(
        string='Signed Cert',
        comodel_name='cert.x509',
        required=True,
    )

    @api.multi
    def action_revoke(self):
        self.ensure_one()
        self.cert_authority_id.revoke(
            self.cert_id,
        )
        return True
