# -*- coding: utf-8 -*-
from odoo import http

# class HrMascoop(http.Controller):
#     @http.route('/hr_mascoop/hr_mascoop/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_mascoop/hr_mascoop/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_mascoop.listing', {
#             'root': '/hr_mascoop/hr_mascoop',
#             'objects': http.request.env['hr_mascoop.hr_mascoop'].search([]),
#         })

#     @http.route('/hr_mascoop/hr_mascoop/objects/<model("hr_mascoop.hr_mascoop"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_mascoop.object', {
#             'object': obj
#         })