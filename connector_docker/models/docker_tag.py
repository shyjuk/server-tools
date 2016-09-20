# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields


class DockerTag(models.Model):
    _name = 'docker.tag'
    _description = 'Docker Tag'

    name = fields.Char()
    image_ids = fields.Many2many(
        string='Images',
        comodel_name='docker.image',
    )
