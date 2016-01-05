# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from datetime import datetime
from openerp import models, fields, api


class waybill(models.Model):

    """"""

    _inherit = 'logistic.waybill'
    _order = 'date desc'

    @api.one
    @api.depends('date_finish', 'date_start')
    def _get_days_range(self):
        if self.date_finish and self.date_start:
            date_start = datetime.strptime(
                self.date_start, '%Y-%m-%d  %H:%M:%S')
            date_finish = datetime.strptime(
                self.date_finish, '%Y-%m-%d  %H:%M:%S')
            self.days_range = (date_finish - date_start).days
        else:
            self.days_range = 0

    @api.one
    @api.depends(
        'travel_ids',
        'travel_ids.price',
        'waybill_expense_ids',
        'waybill_expense_ids.price_subtotal'
    )
    def _get_total(self):
        total_price = 0
        total_cost = 0
        if self.travel_ids:
            for travel in self.travel_ids:
                total_price = total_price + travel.price
        if self.waybill_expense_ids:
            for expense in self.waybill_expense_ids:
                total_cost = total_cost + expense.price_subtotal
        net = total_price - total_cost
        net_avg = 0
        if total_cost != 0:
            net_avg = ((total_price / total_cost) - 1) * 100

        self.total_price = total_price
        self.total_cost = total_cost
        self.net_avg = net_avg
        self.net = net

    @api.one
    @api.depends(
        'distancia_resumen',
        'total_price',
        'total_cost')
    def _get_price_cost_km(self):
        if self.distancia_resumen != 0:
            self.price_km = self.total_price / self.distancia_resumen
            self.cost_km = self.total_cost / self.distancia_resumen
            self.net_km = self.price_km - self.cost_km
        else:
            self.price_km = 0
            self.cost_km = 0
            self.net_km = 0

    @api.one
    @api.depends('initial_odometer_id', 'final_odometer_id')
    def _get_distancia_resumen(self):
        if self.initial_odometer and self.final_odometer:
	     distancia_resumen = self.final_odometer_id.value - self.initial_odometer_id.value
	     self.distancia_resumen = distancia_resumen

    @api.one
    @api.depends('initial_liters')
    def _get_inicio(self):
        if self.initial_liters:
	     litros_iniciales = self.initial_liters
	     self.litros_iniciales = litros_iniciales

    @api.one
    @api.depends('final_liters')
    def _get_final(self):
        if self.final_liters:
	     litros_finales = self.final_liters
	     self.litros_finales = litros_finales


    @api.one
    @api.depends(
        'distancia_resumen',
        'litros_iniciales',
        'litros_finales',
        'waybill_expense_ids.product_id.is_fuel',
        'waybill_expense_ids.product_uom_qty')
    def _get_nafta_data(self):
        litros_cargados = sum(self.mapped('waybill_expense_ids').filtered(
            lambda x: x.product_id.is_fuel).mapped('product_uom_qty'))
        litros_consumidos = self.litros_iniciales + \
            litros_cargados - self.litros_finales
        if self.distancia_resumen != 0:
            consumo = self.litros_consumidos / self.distancia_resumen
        else:
            consumo = 0
        self.litros_cargados = litros_cargados
        self.litros_consumidos = litros_consumidos
        self.consumo = consumo

    @api.one
    @api.depends(
        'consumed_liters')
    def _get_con(self):
        if self.consumed_liters: 
		consumido = self.consumed_liters
		self.consumido = consumido

    @api.one
    @api.depends(
        'consumed_liters',
	'distancia_resumen')
    def _get_nafta_consumida(self):
        if self.consumed_liters and self.distancia_resumen: 
		nafta_consumida= self.consumed_liters / self.distancia_resumen
		self.nafta_consumida = nafta_consumida



    distancia_resumen = fields.Float(
        compute='_get_distancia_resumen',
        string='Distancia',
        store=True,
        )
    litros_cargados = fields.Float(
        compute='_get_nafta_data',
        string='Litros Cargados',
        store=True,
        )
    litros_consumidos = fields.Float(
        compute='_get_nafta_data',
        string='Litros Consumidos',
        store=True,
        )
    nafta_consumida = fields.Float(
        compute='_get_nafta_consumida',
        string='Consumido (l/km)',
        store=True,
	group_operator="avg"
        )
    consumido = fields.Float(
        compute='_get_con',
        string='Consumido',
        store=True,
        )
    litros_iniciales = fields.Float(
        compute='_get_inicio',
        string='Litros Iniciales',
        store=True,
        )
    litros_finales = fields.Float(
        compute='_get_final',
        string='Litros Finales',
        store=True,
        )
    consumo = fields.Float(
        compute='_get_nafta_data',
        string='Consumo',
        store=True,
        )
    days_range = fields.Integer(
        compute='_get_days_range',
        string='Days Range'
        )
    total_price = fields.Float(
        compute='_get_total',
        string='Total Price',
        store=True)
    conumption = fields.Float(
        group_operator="avg"
        )
    total_cost = fields.Float(
        compute='_get_total',
        string='Total Cost',
        store=True
        )
    net = fields.Float(
        compute='_get_total',
        string='Net',
        store=True
        )
    net_avg = fields.Float(
        compute='_get_total',
        string='Net %',
        store=True,
        group_operator="avg"
        )
    price_km = fields.Float(
        compute='_get_price_cost_km',
        string='Price per km',
        store=True,
        group_operator="avg"
        )
    cost_km = fields.Float(
        compute='_get_price_cost_km',
        tring='Cost per km',
        store=True,
        group_operator="avg"
        )
    net_km = fields.Float(
        compute='_get_price_cost_km',
        string='Net per km',
        store=True,
        group_operator="avg"
        )
