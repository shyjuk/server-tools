# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import AccessDenied, ValidationError
from odoo.http import request
from odoo.tests.common import TransactionCase


class TestResUsersImpersonate(HttpCase):

    def setUp(self):
        super(TestResUsersImpersonate, self).setUp()
        self.demo_user = self.env.ref('base.user_demo')
        self.Wizard = self.env['res.users.impersonate']
        request.uid = self.env.uid

    def _return_a_user(self):
        return self.env['res.users'].create({
            'name': 'User',
            'login': 'user',
        })

    def test_action_impersonate_allowed(self):
        """It should update the request UID when allowed."""
        wizard = self.Wizard.create({'to_user_id': self.demo_user.id})
        wizard.action_impersonate()
        self.assertEqual(request.uid, self.demo_user.id)

    def test_action_impersonate_deny(self):
        """It should not update the request UID when denied, instead raise."""
        user = self._return_a_user()
        wizard = self.Wizard.create({'to_user_id': user.id})
        with self.assertRaises(AccessDenied):
            wizard.sudo(self.demo_user).action_impersonate()
        self.assertNotEqual(request.uid, user.id)

    def test_action_impersonate_self(self):
        """It should not allow impersonation to self."""
        wizard = self.Wizard.create({'to_user_id': request.uid})
        with self.assertRaises(ValidationError):
            wizard.action_impersonate()

    def test_action_impersonate_sudo(self):
        """It should not allow impersonation with misaligned request/env user.
        """
        user = self._return_a_user()
        wizard = self.Wizard.create({'to_user_id': user.id})
        request.uid = self.demo_user.id
        with self.assertRaises(ValidationError):
            wizard.action_impersonate()
