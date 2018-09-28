# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MCDepartment(models.Model):
    _name = "hr.department"
    _description = "HR Department"
    _inherit = ['mail.thread']
    _order = "name"
    _rec_name = 'mc_complete_name'

    @api.depends('name', 'parent_id.complete_name')
      def _compute_complete_name(self):
          for department in self:
          if department.name:
            department.complete_name = department.name
