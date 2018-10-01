# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api, _
from time import strftime, strptime
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError

class hr_family_item(Model):
    _name = 'hr.family.item'
    _description = 'Members Familiy'
    _order = 'name desc, age desc'


    @api.depends('age','birth')
    def _compute_age(self):
        for r in self:
            if not r.birth:
                return
        today_date = datetime.now()
        birth_date = datetime.strptime(r.birth, '%Y-%m-%d')
        delta = today_date - birth_date
        r.age = int(delta.days / 365)

    @api.onchange('birth')
    def onchange_birth(self):
        for r in self:
            if br.birth:
                today_date = datetime.now()
                birth_date = datetime.strptime(r.birth, '%Y-%m-%d')
            if birth_date >= today_date:
                raise ValidationError(_('Date of birth can not be higher than the actual date'))

    _RELATION = [('hb_wife', 'Wife/Husband'), ('son', 'Son'),
                 ('father', 'Father'), ('mother', 'Mother'),
                 ('uncle', 'Uncle'), ('brother', 'Brother'),
                 ('nephew', 'Nephew'), ('ulibre', 'Free Union'),
                 ('entenado', 'Other')]
    _TIPOID = [('id','ID'),('passport','Passport')]

    _columns = {
        'name' : fields.char('Name', size=50, required=True),
        'sex' : fields.selection([('h', 'Male'), ('m', 'Female')], 'Sex'),
        'age': fields.function(_compute_age, method=True, string="Age", store=True, type="integer"),
        'birth' : fields.date('Date of birth', required=True),
        'relationship' : fields.selection(_RELATION, 'Relationship'),
        'disabled' : fields.boolean('Discapacitado?', help="Marque este campo si la carga familiar es discapacitado, tenga en cuenta que un carga familiar que sea mayor de edad pero con discapacidad se toma en cuenta para el cálculo de utilidades"),
        'disabled_type': fields.char('Disabled Type',size=64),
        'disabled_percent': fields.integer('Disabled Percent'),
        'disabled_id': fields.char('CONADIS ID',size=10,help="CONNADIS identification code."),
        'employee_id' : fields.many2one('hr.employee', 'Employee'),
        'type_id' : fields.selection(_TIPOID, "Type ID"),
        'identification_id': fields.char(_('Identification Number'), size=13, help=_('Identificator or Unique Register')),
        'tutela': fields.boolean('Tutela?', help="Marque este campo si la carga familiar está bajo tutela, tenga en cuenta que un carga familiar bajo tutela se toma en cuenta para el cálculo de utilidades"),
        }

    _defaults = {
        'age' : 0,
        }

hr_family_item()

class hr_employee(osv.osv):
    _inherit = 'hr.employee'

    def _compute_utilities_charges(self, cr, uid, ids, field_name, arg, context):
        for employee in self.browse(cr, uid, ids):
            aux = 0
            for family in employee.family_item_ids:
                if family.relationship == 'hb_wife':
                    aux += 1
                if family.age < 18:
                    aux += 1
                if family.tutela or family.disabled:
                    aux += 1
        return {employee.id:aux}

    _columns = {
        'family_item_ids': fields.one2many('hr.family.item', 'employee_id', "Familiy Members"),
        'utilities_charges': fields.function(_compute_utilities_charges, method=True, string="Utilities Charges",
                                       store=False, type="integer"),
        'disabled': fields.boolean('Disabled?',help="Check this if the employee has any kind of limitation to do some activities, caused by some physics or mental disability."),
        'disabled_type': fields.char('Disabled Type',size=64),
        'disabled_percent': fields.integer('Disabled Percent'),
        'disabled_id': fields.char('CONADIS ID',size=10,help="CONNADIS identification code."),

        }

    _defaults = {
        'utilities_charges': 0,
        'active':True,
        }
