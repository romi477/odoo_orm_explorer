# -*- coding: utf-8 -*-

from odoo import models, fields


class OrmQuery(models.Model):
    _name = 'orm.query'
    _order = 'id desc'
    _description = 'Odoo ORM Query'
    
    search_query = fields.Char(
        string='Search Query',
        readonly=True,
    )
    sql_text = fields.Text(
        string='SQL',
        readonly=True,
    )
    fetch_result = fields.Char(
        string='Result',
        readonly=True,
    )
