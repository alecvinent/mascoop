from odoo import fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    tracks_limit = fields.Integer(string="Tracks per participant",
                                    default=False)
    
