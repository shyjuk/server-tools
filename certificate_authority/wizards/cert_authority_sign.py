# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CertAuthoritySign(models.TransientModel):
    """ It signs a Cert Request. """

    _name = 'cert.authority.sign'
    _description = 'Cert Authority Sign'

    cert_authority_id = fields.Many2one(
        string='Cert Authority',
        comodel_name='cert.authority',
        required=True,
        readonly=True,
    )
    cert_request_id = fields.Many2one(
        string='Cert Request',
        comodel_name='cert.request',
        required=True,
    )
    host_ids = fields.Many2many(
        string='Hosts',
        comodel_name='cert.host',
        help='Hosts to use as overrides for the CSR.',
    )
    subject = fields.Char(
        help='Subject to use as override for the CSR.',
    )
    serial_sequence = fields.Char(
        help='Prefix for the generated cert\'s serial number.',
    )
    cert_id = fields.Many2one(
        string='Signed Cert',
        comodel_name='cert.x509',
    )

    @api.multi
    def action_sign(self):
        self.ensure_one()
        self.write({
            'cert_id': self.cert_authority_id.sign(
                cert_request=self.cert_request_id,
                hosts=self.host_ids,
                subject=self.subject,
                serial_sequence=self.serial_sequence,
            )
        })
        return True
