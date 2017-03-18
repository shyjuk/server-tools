# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ImportWordpressUser(models.TransientModel):

    _inherit = 'import.wordpress.abstract'
    _name = 'import.wordpress.user'
    _description = 'Import Wordpress User'

    bio = fields.Html()
    email = fields.Char(
        required=True,
    )
    first_name = fields.Char(
        required=True,
    )
    last_name = fields.Char(
        required=True,
    )
    roles = fields.Serialized(
        required=True,
    )
    url = fields.Char(
        required=True,
    )
    username = fields.Char(
        required=True,
    )
    odoo_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
    )

    @api.model
    def do_import(self, wordpress_ref, wizard):
        super(ImportWordpressUser, self).do_import(wordpress_ref, wizard)
        with wizard.get_api() as api:
            user = api.call(
                self.wizard_id.methods.users.GetUser(wordpress_ref),
            )
        struct = {
            'wordpress_ref': user.id,
        }
        struct.update(user.struct)
        record = self.create(struct)
        record.to_odoo()
        return record

    @api.multi
    def import_map(self):
        self.ensure_one()
        return {
            'name': '%s %s' % (self.first_name, self.last_name),
            'email': self.email,
            'login': self.username,
            'website_short_description': self.bio,
            'website_description': self.bio,
            'website': self.url,
        }

    @api.multi
    def to_odoo(self):
        for record in self:
            if not record.odoo_id:
                user = self.env['res.users'].search([
                    ('email', '=', record.email),
                ])
                if user:
                    user.update(record.import_map())
                else:
                    user = self.env['res.users'].create(
                        record.import_map(),
                    )
                record.odoo_id = user.id
            else:
                record.odoo_id.update(
                    record.import_map(),
                )
