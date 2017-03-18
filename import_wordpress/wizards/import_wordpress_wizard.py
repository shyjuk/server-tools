# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from contextlib import contextmanager

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from wordpress_xmlrpc import Client, methods
    # Explicit import to circumvent:
    # https://github.com/maxcutler/python-wordpress-xmlrpc/pull/109
    from wordpress_xmlrpc.methods import taxonomies
except ImportError:
    methods = None
    _logger.info('`python-wordpress-xmlrpc` library is not installed.')


class ImportWordpressWizard(models.TransientModel):

    _name = 'import.wordpress.wizard'
    _description = 'Import Wordpress Wizard'

    methods = methods

    name = fields.Char(
        required=True,
    )
    uri = fields.Char(
        required=True,
        help='URI to XML-RPC endpoint. See more in the WordPress docs - '
             'https://codex.wordpress.org/XML-RPC_Support',
    )
    username = fields.Char(
        required=True,
    )
    password = fields.Char(
        required=True,
    )
    blog_id = fields.Many2one(
        string='Blog',
        comodel_name='blog.blog',
        required=True,
    )

    @api.multi
    def check_connection(self):
        for record in self:
            with record.get_api():
                pass
        raise UserError(_(
            'Connection was successfully established to the WordPress '
            'server.',
        ))

    @api.multi
    def to_odoo(self):
        self.ensure_one()
        Post = self.env['import.wordpress.post'].with_context(
            wp_wizard_id=self.id,
        )
        with self.get_api() as api:
            post_ids = [
                p.id for p in api.call(self.methods.posts.GetPosts({
                    'number': 999999,
                }))
            ]
        _logger.debug('Post IDs %s', post_ids)
        for post_id in post_ids:
            Post.do_import(post_id, self)

    @api.multi
    @contextmanager
    def get_api(self):
        self.ensure_one()
        yield Client(self.uri, self.username, self.password)
