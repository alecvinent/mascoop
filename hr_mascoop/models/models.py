# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MCDepartment(models.Model):
    _name = "hr.department"
    _inherit = 'hr.department'

    @api.depends('name', 'complete_name')
    def _compute_complete_name(self):
        for department in self:
            if department.name:
                department.complete_name = department.name
