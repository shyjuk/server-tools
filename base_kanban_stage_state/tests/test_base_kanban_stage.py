# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestBaseKanbanStage(TransactionCase):

    def test_get_states(self):
        """It should return a list of stages"""
        test_stage = self.env['base.kanban.stage']
        self.assertIsIsntance(
            test_stage._get_states(),
            list,
        )
