# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValiadtionError


class BaseKanbanStage(models.Model):
    _inherit = 'base.kanban.stage'

    state = fields.Selection(
        lambda self: self._get_states(),
    )
    is_default_state = fields.Boolean()

    @api.model
    def _get_states(self):
        return [
            ('draft', 'New'),
            ('open', 'In Progress'),
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
            ('exception', 'Exception'),
        ]

    @api.multi
    @api.constrains('is_default_state')
