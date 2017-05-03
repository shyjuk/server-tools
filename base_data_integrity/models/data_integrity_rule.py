# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.base.res.res_request import referenceable_models


class DataIntegrityRule(models.Model):

    _name = 'data.integrity.rule'
    _description = 'Data Integrity Rule'

    model_id = fields.Many2one(
        string='Target Model',
        comodel_name='ir.model',
        required=True,
    )
    model_name = fields.Char(
        related='model_id.model',
    )

