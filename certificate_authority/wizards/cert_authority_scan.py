# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CertAuthorityScan(models.TransientModel):
    """ It scans a host and displays the results. """

    _name = 'cert.authority.scan'
    _description = 'Cert Authority Scan'

    cert_authority_id = fields.Many2one(
        string='Cert Authority',
        comodel_name='cert.authority',
        required=True,
        readonly=True,
    )
    host_id = fields.Many2one(
        string='Host',
        comodel_name='cert.host',
        required=True,
        help='The host to scan.'
    )
    ip = fields.Char(
        string='IP',
        help='IP Address to override DNS lookup of host.',
    )
    state = fields.Selection([
        ('New', 'Not Scanned'),
        ('Good', 'Good'),
        ('Warning', 'Warning'),
        ('Bad', 'Bad'),
        ('Skipped', 'Skipped'),
    ],
        default='New',
        readonly=True,
        required=True,
    )
    error = fields.Text()
    results = fields.Text()

    @api.multi
    def action_scan(self):
        self.ensure_one()
        results = self.cert_authority_id.scan(
            self.host_id, self.ip,
        )
        self.write({
            'state': results['grade'],
            'error': results['error'],
            'results': results['output'],
        })
        return True
