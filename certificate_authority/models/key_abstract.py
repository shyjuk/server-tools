# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class KeyAbstract(models.AbstractModel):
    """ It provides attributes and methods related to all keys. """

    _name = 'key.abstract'
    _description = 'Key Abstract'

    strength = fields.Integer(
        default=4096,
    )
    algorithm = fields.Selection(
        default='rsa',
        selection=lambda s: s._get_algorithms(),
    )
    is_private = fields.Boolean()
    active = fields.Boolean(
        default=True,
    )
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
    def _get_algorithms(self):
        return [
            ('rsa', 'RSA'),
            ('ecdsa', 'ECDSA'),
        ]

    @api.model
    def _get_mime_sub_types(self):
        return self.env['cert.abstract']._get_mime_sub_types()

    @api.multi
    def _compute_mime_type(self):
        for record in self:
            record.mime_type = 'application/%s' % record.mime_sub_type
