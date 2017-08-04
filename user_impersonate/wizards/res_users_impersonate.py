# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, exceptions, fields, http, models, _


class ResUsersImpersonate(models.TransientModel):

    _name = 'res.users.impersonate'

    to_user_id = fields.Many2one(
        string='Switch to User',
        comodel_name='res.users',
        required=True,
    )

    @api.multi
    def action_impersonate(self):
        self.ensure_one()
        import pdb; pdb.set_trace()
        if not self.env.user.has_group('base.group_erp_manager'):
            raise exceptions.AccessDenied()
        if self.env.uid != http.request.uid:
            raise exceptions.ValidationError(_(
                'You cannot impersonate while in sudo.',
            ))
        if self.env.user == self.to_user_id:
            raise exceptions.ValidationError(_(
                'You cannot impersonate yourself.',
            ))
        http.request.uid = self.to_user_id.id
        http.request.redirect_with_hash('/')
