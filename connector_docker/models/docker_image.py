# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields


class DockerImage(models.Model):
    _name = 'docker.image'
    _description = 'Docker Image'

    server_id = fields.Many2one(
        string='Server',
        comodel_name='docker.server',
        readonly=True,
        related='build_id.server_id',
    )
    name = fields.Char(
        required=True,
    )
    parent_id = fields.Many2one(
        string='Parent',
        comodel_name='docker.image',
    )
    child_ids = fields.One2many(
        string='Children',
        comodel_name='docker.image',
        inverse_name='parent_id',
    )
    container_ids = fields.One2many(
        string='Containers',
        comodel_name='docker.container',
        inverse_name='image_id',
    )
    tag_ids = fields.Many2many(
        string='Tags',
        comodel_name='docker.tag',
    )
    date_created = fields.Float()
    size_virtual = fields.Float()
    size_actual = fields.Float()
