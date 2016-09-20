# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields


class DockerContainer(models.Model):
    _name = 'docker.container'
    _description = 'Docker Container'

    server_id = fields.Many2one(
        string='Server',
        comodel_name='docker.server',
        readonly=True,
        related='build_id.server_id',
    )
    build_id = fields.Many2one(
        string='Build',
        comodel_name='docker.build',
    )
    image_id = fields.Many2one(
        string='Image',
        comodel_name='docker.image',
        required=True,
    )
    mount_ids = fields.Many2many(
        string='Mounts',
        comodel_name='docker.mount',
    )
    name = fields.Char(
        help='Container ID',
    )
    names = fields.Serialized(
        help='Canonical Names',
    )
    command = fields.Text()
    date_created = fields.Float()
    status = fields.Char()
    host_config = fields.Serialized()
    
