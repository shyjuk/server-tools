# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import requests

from datetime import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
except ImportError:
    _logger.info('`bs4` (BeautifulSoup) library is not installed.')


class ImportWordpressPost(models.TransientModel):

    _inherit = 'import.wordpress.abstract'
    _name = 'import.wordpress.post'
    _description = 'Import Wordpress Post'

    post_date_gmt = fields.Datetime(
        required=True,
    )
    post_modified_gmt = fields.Datetime(
        required=True,
    )
    post_excerpt = fields.Text()
    guid = fields.Char(
        required=True,
    )
    link = fields.Char(
        required=True,
    )
    post_status = fields.Char(
        required=True,
    )
    post_title = fields.Char(
        required=True,
    )
    post_name = fields.Char(
        required=True,
    )
    post_title = fields.Char(
        required=True,
    )
    post_author = fields.Integer(
        required=True,
    )
    post_thumbnail = fields.Serialized(
        required=True,
    )
    custom_fields = fields.Serialized(
        required=True,
    )
    terms = fields.Serialized(
        required=True,
    )
    odoo_id = fields.Many2one(
        string='Blog Post',
        comodel_name='blog.post',
    )
    attachment_ids = fields.One2many(
        string='Attachments',
        comodel_name='import.wordpress.attachment',
        inverse_name='wordpress_post_id',
    )
    cover_image = fields.Binary()

    @api.multi
    def _compute_post_id(self):
        for record in self:
            record.post_id = record.wordpress_ref

    @api.multi
    def _inverse_post_id(self):
        for record in self:
            record.wordpress_ref = record.post_id

    @api.model
    def do_import(self, wordpress_ref, wizard):
        super(ImportWordpressPost, self).do_import(wordpress_ref, wizard)
        Attachment = self.env['import.wordpress.attachment']
        with wizard.get_api() as api:
            post = api.call(
                self.wizard_id.methods.posts.GetPost(wordpress_ref),
            )
        struct = {
            'wordpress_ref': post.id,
        }
        struct.update(post.struct)
        try:
            struct['cover_image'] = Attachment.get_remote_content({
                'external_uri': struct['post_thumbnail']['link'],
            })
            struct['post_thumbnail']['date_created_gmt'] = self.__from_iso(
                struct['post_thumbnail']['date_created_gmt'].value,
            )
        except (KeyError, TypeError):
            _logger.info('No cover image found for post %s' % post.id)
        for i in ['post_date_gmt', 'post_modified_gmt']:
            struct[i] = self.__from_iso(struct[i].value)
        _logger.debug(struct)
        record = self.create(struct)
        record.to_odoo()
        return record

    @api.multi
    def import_map(self):
        self.ensure_one()
        Tag = self.env['import.wordpress.tag']
        published = self.post_status == 'publish'
        tag_ids = []
        try:
            for i in self.terms['post_tag']:
                odoo_id = Tag.get_by_id(i, self.wizard_id).odoo_id.id
                if odoo_id:
                    tag_ids.append(odoo_id)
        except KeyError:
            pass
        author = self.env['import.wordpress.user'].get_by_id(
            self.post_author, self.wizard_id,
        )
        vals = {
            'post_date': self.post_date_gmt,
            'create_date': self.post_date_gmt,
            'write_date': self.post_modified_gmt,
            'published_date': published and self.post_date_gmt or False,
            'teaser_manual': self.post_excerpt and self.post_excerpt or False,
            'website_published': published,
            'name': self.post_title,
            'cover_image': self.cover_image,
            'tag_ids': [(6, 0, tag_ids)],
            'author_id': author.odoo_id.partner_id.id,
            'blog_id': self.wizard_id.blog_id.id,
            'website_meta_description': self._get_meta_description(),
            'website_focus_keyword': self._get_focus_keyword(),
        }
        return vals

    @api.multi
    def to_odoo(self):
        for record in self:
            if not record.odoo_id:
                post = self.env['blog.post'].create(
                    record.import_map(),
                )
                record.odoo_id = post.id
            else:
                record.odoo_id.update(
                    record.import_map(),
                )
            record.process_post()

    @api.multi
    def process_post(self):
        for record in self:
            record.ensure_one()
            response = requests.get(record.link)
            record.soup = BeautifulSoup(response.content)
            body = record.soup.select('div.post-content')[0]
            record._replace_images(body)
            record.odoo_id.write({
                'content': str(body),
            })

    @api.multi
    def _get_meta_description(self):
        return self._get_meta_description('_yoast_wpseo_metadesc')

    @api.multi
    def _get_focus_keyword(self):
        return self._get_meta_description('_yoast_wpseo_focuskw')

    @api.multi
    def __get_custom_field(self, field_name):
        self.ensure_one()
        for i in self.custom_fields:
            if i['key'] == field_name:
                return i

    @api.multi
    def _replace_images(self, soup):
        # Iterate other images and replace with locals
        for img in soup.find_all('img'):
            parent = img.parent
            if parent.name == 'p':
                container = img
                parent = img
            else:
                container = parent
            image = self.env['import.wordpress.attachment'].create({
                'name': img['title'],
                'description': img['title'],
                'external_uri': parent.get('href') or img['src'],
                'wordpress_post_id': self.id,
            })
            self.__replace_image(container, image)

    @api.model_cr_context
    def __replace_image(self, img_container, new_image):
        new_container = self.soup.new_tag(
            'div',
            **{'class': 'overlay-container overlay-visible'}
        )
        img = self.soup.new_tag(
            'img',
            src=new_image.website_url,
            alt=new_image.description or new_image.name,
        )
        a = self.soup.new_tag(
            'a',
            href=new_image.website_url,
            title=new_image.description or new_image.name,
            **{'class': 'popup-img overlay-link'}
        )
        i = self.soup.new_tag(
            'i',
            **{'class': 'icon-plus-1'}
        )
        a.append(i)
        new_container.append(img)
        new_container.append(a)
        img_container.replace_with(new_container)
        return new_container

    @api.model_cr_context
    def __from_iso(self, iso):
        return fields.Datetime.to_string(
            datetime.strptime(iso, '%Y%m%dT%H:%M:%S'),
        )
