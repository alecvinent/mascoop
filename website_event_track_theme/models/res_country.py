from odoo import fields, models


class CountryEvent(models.Model):
    _inherit = 'res.country'
    _name='res.country'
    alpha3=fields.Char('Alpha3')
