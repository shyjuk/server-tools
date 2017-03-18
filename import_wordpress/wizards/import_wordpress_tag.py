# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)



class ImportWordpressTag(models.TransientModel):

    _inherit = 'import.wordpress.abstract'
    _name = 'import.wordpress.tag'
    _description = 'Import Wordpress Tag'

    term_id = fields.Integer(
        related='wordpress_ref',
    )
    name = fields.Char(
        required=True,
    )
    description = fields.Text()
    odoo_id = fields.Many2one(
        string='Blog Tag',
        comodel_name='blog.tag',
    )

    @api.model
    def do_import(self, wordpress_ref, wizard):
        super(ImportWordpressTag, self).do_import(wordpress_ref, wizard)
        with wizard.get_api() as api:
            tag = api.call(
                self.wizard_id.methods.taxonomies.GetTerm(
                    'post_tag', wordpress_ref,
                ),
            )
        struct = {
            'wordpress_ref': tag.id,
        }
        struct.update(tag.struct)
        record = self.create(struct)
        record.to_odoo()
        return record

    @api.multi
    def import_map(self):
        self.ensure_one()
        return {
            'name': self.name,
            'website_meta_description': self.description,
        }

    @api.multi
    def to_odoo(self):
        for record in self:
            if not record.odoo_id:
                tag = self.env['blog.tag'].search([
                    ('name', '=', record.name),
                ])
                if len(tag):
                    tag.update(record.import_map())
                else:
                    tag = self.env['blog.tag'].create(
                        record.import_map(),
                    )
                record.odoo_id = tag.id
            else:
                record.odoo_id.update(
                    record.import_map(),
                )
