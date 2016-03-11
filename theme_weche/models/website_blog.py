# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class weche_Blog(models.Model):
    _inherit = 'blog.blog'

    show_author = fields.Boolean(
        default=False,
        string=u"Відображати автора цього блогу")
