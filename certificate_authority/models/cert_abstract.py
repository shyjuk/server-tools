# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CertAbstract(models.AbstractModel):
    """ It provides attributes and methods related to all cert files. """

    _name = 'cert.abstract'
    _description = 'Cert Abstract'

    name = fields.Char(
        required=True,
        help='SHA-1 Sum of Cert',
    )
    description = fields.Char()
    mime_sub_type = fields.Selection(
        selection=lambda s: s._get_mime_sub_types(),
        deault='x-pkcs12',
    )
    mime_type = fields.Char(
        readonly=True,
        computed='_compute_mime_type',
    )
    attachment_id = fields.Many2one(
        string='Key',
        comodel_name='ir.attachment',
        context="""{
            'default_type': 'binary',
            'default_res_model': _name,
            'default_res_field': 'attachment_id',
            'default_res_id': id,
            'default_name': name,
            'default_description': description,
            'default_mime_type': mime_type,
        }""",
    )
    data = fields.Binary(
        related='attachment_id.datas',
    )
    request_id = fields.Many2one(
        string='CSR',
        comodel_name='cert.request',
    )

    @api.model
    def _get_mime_sub_types(self):
        return [
            ('pkcs8', 'PKCS-8'),
            ('pkcs10', 'PKCS-10'),
            ('x-pkcs12', 'PKCS-12'),
            ('x-pem-file', 'PEM'),
            ('pkcs7-mime', 'PKCS-7 MIME'),
            ('x-x509-ca-cert', 'X.509 CA'),
            ('x-x509-user-cert', 'X.509 User'),
        ]

    @api.multi
    def _compute_mime_type(self):
        for record in self:
            record.mime_type = 'application/%s' % record.mime_sub_type
