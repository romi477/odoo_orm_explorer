# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__file__)


class OrmQueryWizard(models.TransientModel):
    _name = 'orm.query.wizard'
    _description = 'Odoo ORM Query Wizard'

    domain_expr = fields.Char(
        string='Domain',
        required=True,
    )
    full_query = fields.Char(
        string='Search Query',
        readonly=True,
    )
    fetch_result = fields.Char(
        string='Result',
        readonly=True,
    )
    sql_text = fields.Text(
        string='SQL',
        readonly=True,
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
        domain=[
            ('transient', '=', False),
        ],
    )
    model = fields.Char(
        string='Name',
        related='model_id.model',
    )
    offset = fields.Integer(
        string='Offset (int)',
    )
    limit = fields.Integer(
        string='Limit (int)',
    )
    order = fields.Char(
        string='Order (str)',
    )
    count = fields.Boolean(
        string='Count',
    )

    @property
    def _model(self):
        return self.env[self.model]

    @api.onchange('model_id')
    def _check_model_type(self):
        if self.model_id and self._model._abstract:
            return {'warning':
                {
                    'title': 'Abstract model detected!',
                    'message': 'Current type of model not supported!',
                },
            }

    def raise_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'ORM Search Query Tool',
            'res_model': 'orm.query.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _compile_search_query(self):
        vals = {
            'model': self.model,
            'query': self.domain_expr,
            'offset': self.offset or 0,
            'limit': self.limit or None,
            'order': self.order or None,
            'count': self.count,
        }
        return "env['%(model)s'].search(%(query)s, " \
               "offset=%(offset)s, limit=%(limit)s, order=%(order)s, count=%(count)s)" % vals

    def save_sql(self):
        vals = {
            'search_query': self.full_query,
            'sql_text': self.sql_text,
            'fetch_result': self.fetch_result,
        }
        self.env['orm.query'].create(vals)
        return self.raise_form()

    def execute_orm_search(self):
        """ Through the standard logic of model._search() method
        """
        offset = self.offset or 0
        limit = self.limit or None
        order = self.order or None
        _model = self._model

        if _model._abstract:
            raise ValidationError(_(
                'Current type of model not supported! '
                '"%s" is abstract model!' % (self.model,)
            ))

        try:
            args = eval(self.domain_expr)
        except Exception as ex:
            _logger.debug(ex)
            raise ValidationError(_(
                'Got "expression" fault during domain evaluation!'
            ))

        if expression.is_false(_model, args):
            raise ValidationError(_(
                'Got "expression" fault during domain parsing!'
            ))

        query = _model._where_calc(args)
        _model._apply_ir_rules(query, 'read')
        order_by = _model._generate_order_by(order, query)
        from_clause, where_clause, where_clause_params = query.get_sql()
        where_str = where_clause and (' WHERE %s' % where_clause) or ''

        if self.count:
            query_str = 'SELECT count(1) FROM ' + from_clause + where_str
            self._cr.execute(query_str, where_clause_params)
            res_id = self._cr.fetchone()
            fetch_result = res_id[0]
        else:
            limit_str = limit and ' limit %d' % limit or ''
            offset_str = offset and ' offset %d' % offset or ''
            _format = from_clause + where_str + order_by + limit_str + offset_str
            query_str = 'SELECT "%s".id FROM ' % _model._table + _format

            self._cr.execute(query_str, where_clause_params)
            result = self._cr.fetchall()
            res_ids = [rec[0] for rec in result]
            fetch_result = str(_model.browse(res_ids))

        self.write({
            'full_query': self._compile_search_query(),
            'sql_text': self._cr._obj.query.decode(),
            'fetch_result': fetch_result,
        })

        return self.raise_form()
