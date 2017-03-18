# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import requests

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ImportWordpressAttachment(models.TransientModel):

    _name = 'import.wordpress.attachment'
    _description = 'Import Wordpress Attachment'
    _inherits = {'ir.attachment': 'attachment_id'}

    external_uri = fields.Text(
        required=True,
    )
    attachment_id = fields.Many2one(
        string='Attachment',
        comodel_name='ir.attachment',
        required=True,
        ondelete='cascade',
    )
    wordpress_post_id = fields.Many2one(
        string='Wordpress Post',
        comodel_name='import.wordpress.post',
        required=True,
    )

    @api.model
    def create(self, vals):
        vals = self._get_vals(vals)
        return super(ImportWordpressAttachment, self).create(vals)

    @api.multi
    def update(self, vals):
        for record in self:
            if not vals.get('wordpress_post_id'):
                vals['wordpress_post_id'] = record.wordpress_post_id.id
            vals = self._get_vals(vals)
            return super(ImportWordpressAttachment, record).update(vals)

    @api.model_cr_context
    def get_remote_content(self, vals):
        if vals.get('external_uri'):
            response = requests.get(vals['external_uri'])
            if response.status_code != 200:
                raise ValidationError(_(
                    'Could not get remote image.',
                ))
            return response.content.encode('base64')

    @api.model_cr_context
    def _get_file_name(self, uri):
        return uri.rsplit('/', 1)[1]

    @api.model_cr_context
    def _get_vals(self, vals):
        wordpress_post = self.env['import.wordpress.post'].browse(
            vals['wordpress_post_id'],
        )
        blog_post = wordpress_post.odoo_id
        vals.update({
            'datas': self.get_remote_content(vals),
            'datas_fname': self._get_file_name(vals['external_uri']),
            'res_id': blog_post.id,
            'res_model': blog_post._name,
            'public': True,
        })
        return vals
