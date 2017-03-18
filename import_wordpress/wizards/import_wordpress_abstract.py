# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ImportWordpressAbstract(models.AbstractModel):

    _name = 'import.wordpress.abstract'
    _description = 'Import Wordpress Abstract'

    wordpress_ref = fields.Integer(
        required=True,
    )
    wizard_id = fields.Many2one(
        comodel_name='import.wordpress.wizard',
        required=True,
        default=lambda s: s.env.context.get('wp_wizard_id', False),
    )

    _sql_constraints = [
        ('wordpress_ref_unique', 'UNIQUE(wordpress_ref)',
         'This Wordpress ID has already been imported.'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('id'):
            vals['wordpress_ref'] = vals['id']
            del vals['id']
        return super(ImportWordpressAbstract, self).create(vals)

    @api.model
    def do_import(self, wordpress_ref, wizard):
        return

    @api.model
    def get_by_id(self, wordpress_ref, wizard=False):
        """ It returns the object from the provided wordpress ID. """
        res = self.search([('wordpress_ref', '=', wordpress_ref)])
        if wizard and not len(res):
            res = self.do_import(wordpress_ref, wizard)
        return res
