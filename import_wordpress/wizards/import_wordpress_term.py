# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)



class ImportWordpressTerm(models.AbstractModel):

    _inherit = 'import.wordpress.abstract'
    _name = 'import.wordpress.term'
    _description = 'Import Wordpress Term'

    _term_name = None
    _term_model = None

    term_id = fields.Integer(
        related='wordpress_ref',
    )
    name = fields.Char(
        required=True,
    )
    slug = fields.Char(
        required=True,
    )
    description = fields.Text()
    odoo_id = fields.Many2one(
        string='Blog Term',
        comodel_name='blog.term',
    )

    @api.model
    def do_import(self, wordpress_ref, wizard):
        super(ImportWordpressTerm, self).do_import(wordpress_ref, wizard)
        with wizard.get_api() as api:
            term = api.call(
                self.wizard_id.methods.taxonomies.GetTerm(
                    self._term_name, wordpress_ref,
                ),
            )
        struct = {
            'wordpress_ref': term.id,
        }
        struct.update(term.struct)
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
        Terms = self.env[self._term_model]
        for record in self:
            if not record.odoo_id:
                term = Terms.search([
                    ('name', '=', record.name),
                ])
                if len(term):
                    term.update(record.import_map())
                else:
                    term = Terms.create(
                        record.import_map(),
                    )
                record.odoo_id = term.id
            else:
                record.odoo_id.update(
                    record.import_map(),
                )
