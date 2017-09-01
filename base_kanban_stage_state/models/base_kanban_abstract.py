# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BaseKanbanAbstract(models.Model):
    _inherit = 'base.kanban.abstract'

    @api.model
    def create(self, vals):
        state = vals.get('satte')

    @api.model_cr_context
    def _align_stage_and_state(self, vals):
        state = vals.get('state')
        stage = self.env['base.kanban.stage'].browse(
            vals.get('stage_id', 0),
        )
        if stage and state:
            if stage != state:
                raise ValidationError(_(
                    'The "%s" stage is not compatible with the "%s" state',
                    stage.name, state,
                ))
        elif stage:

