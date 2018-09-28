# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#

from odoo import api, fields, models
from odoo.tools.translate import _, html_translate
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError

# class EventMailRegistrationEgal(models.Model):
#     inherit = 'event.mail.registration'
#     _name = 'event.mail.registration'
#     _description = 'Registration Mail Scheduler'
#
#
# @api.one
# def execute(self):
#     if self.registration_id.state in ['open', 'done'] and not self.mail_sent:
#         if self.registration_id.event_ticket_id:
#             self.scheduler_id.template_id.send_mail(self.registration_id.id)
#         self.write({'mail_sent': True})


class TrackTheme(models.Model):
    _name = "event.track.theme"
    _description = 'Track Theme'
    _order = 'name'
    name = fields.Char('Nombre')
    group_id = fields.Many2one('res.groups', 'Grupo')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tema ya existe !"),
    ]

class TrackType(models.Model):
    _name = "event.track.type"
    _description = 'Track Type'
    _order = 'name'
    name = fields.Char('Tipo')
    description=fields.Char( 'Descripción')
    is_poster = fields.Boolean( string='Es Poster', default=False)
    is_table =  fields.Boolean( string='Es mesa redonda', default=False)
    duration = fields.Float(string="Duracion estimada", default=1)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type de ponencia ya existe !"),
    ]

class TrackTag(models.Model):
    _name = "event.track.tag"
    _inherit = "event.track.tag"
    _description = 'Track Tag'
    _order = 'name'

    theme_id = fields.Many2one('event.track.theme', 'Theme')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
class TrackParticipant(models.Model):
    _name = "event.track.participant"
    _description = 'Track Round Table'
    _order = 'partner_id'
    partner_id = fields.Many2one('res.partner', 'Participante', mandatory=True)
    partner_track_id = fields.Many2one('event.track', 'Ponencia')
    track_id = fields.Many2one('event.track')


class Track(models.Model):
    _name = "event.track"
    _inherit =  "event.track"
    _description = 'Event Track'

    @api.model
    def _get_default_duration(self):
        return self.env['event.track.type'].search([], limit=1).duration

    @api.depends('theme_tag','final_tag_id')
    def depends_theme_tag(self):
        if self.final_tag_id.theme_id:
            self.theme_tag=self.final_tag_id.theme_id

    @api.onchange('theme_tag','user_id')
    def filter_theme_tag(self):
        users = self._get_users_from_group(self.theme_tag.group_id.id)
        if len(users):
            self.user_id = users[0]
        domain = [('theme_id.id','=',self.theme_tag.id)]
        self.final_tag_id = None
        return {'domain': {'final_tag_id': domain}}

    @api.onchange('final_tag_id')
    def onchange_final_tag_id(self):
        if not self.final_tag_id or not self.final_tag_id :
            return
        if not self.theme_tag:
            raise ValidationError("Debe seleccionar el eje temático primero")
 #       if self.final_tag_id.theme_id.id != self.theme_tag.id:
 #           self.final_tag_id=None
 #           raise ValidationError("Debe coincidr con el eje temático")



    tag_ids = fields.Many2many('event.track.tag', string='Tags Posibles')
    theme_tag=fields.Many2one('event.track.theme','Eje temático',required=True)
    final_tag_id =  fields.Many2one('event.track.tag', 'Tag Seleccionado', required=True)
    # ,domain = "[('theme_id.id','=',theme_tag.id),]")

    duration = fields.Float('Duración', default=_get_default_duration, readonly= [('stage_id.id', '==', 1)])
    location_id = fields.Many2one('event.track.location', 'Ubicación', readonly= [('stage_id.id', '==', 1)])
    date = fields.Datetime('Fecha programada', readonly= [('stage_id.id', '==', 1)])
    image = fields.Binary('Foto', related='partner_id.image_medium', store=True, attachment=True)
    adjunto = fields.Binary(string="Poster propuesto",  store= True, attachment= True)
    file_name = fields.Char(string="File Name")
    type_id = fields.Many2one('event.track.type', 'Tipo de Propuesta', required=True,
                              help='Consulte Modalidad para ver detalles y requerimientos')
    is_table = fields.Boolean('Es Mesa Redonda', default=False,invisible=True)
    is_moderator = fields.Boolean('Quiere ser moderador?', default=False)
    country_id =  fields.Many2one('res.country', 'País', required=True,
                                 help = 'Nacionalidad ')
    product_id = fields.Many2one('product.product', 'Tipo de ponente', required=True,
                                 domain=[('name', 'like','Pon')],
                                 help = 'Una vez aceptada la propuesta, recibirá su confirmación y forma de pago ')
    partners_ids = fields.One2many(
        string="Integrantes de la Mesa",
        comodel_name="event.track.participant",
        inverse_name="track_id",
        help="Los integrantes de la mesa deben ser usuarios registrados",
    )
    resumen = fields.Text('Resumen',size=3500, default='No más de 500 palabras.', required=True)
    partner_id_name = fields.Char('Documento de Identidad')
    partner_company_name = fields.Char('Institución')
    @api.one
    @api.constrains('resumen')
    def _constrains_resumen(self):
        for r in self:
            if len(r.resumen.split()) > 500 :
                raise ValidationError('El texto tiene más de 500 palabras')
    @api.onchange('type_id')
    def _onchange_type_id(self):
        if self.type_id:
            self.duration = self.type_id.duration
            self.is_table = self.type_id.is_table
#   onchange stage_d
#   Valida grupo de usuario y tema
#  Registro y orden de venta generados por un cron
    #
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if not self.stage_id.id:
            return
        for r in self:

            g= r.env['event.track.theme'].search(
                 [('id', '=', r.theme_tag.id)])
            if not g:
                return
            g_id = g[0].group_id.id

            if not (
                     r.env.user.id in  r._get_users_from_group(g_id)
                         or r.env.user.id == 1):
                raise ValidationError('No esta autorizado a cambiar el estado de esta propuesta')

    def process_stage(self):
        this_run=0
        for r in self.search(
        [('stage_id.sequence','in',[2,3,4]),]
        ):
            if not r.product_id:
                continue
            if this_run > 50:
                return

            previuos_amount=0
            x= r.env['event.registration'].search(
                [( 'attendee_partner_id.id', '=',r.partner_id.id)])
            if x and not x[0].event_ticket_id:
                continue
            if x and not x[0].state == 'open':
                continue

            if x :
                previuos_amount=x[0].event_ticket_id.price
            try:
                if not r.partner_id.id_numbers:
                    p_id= r.partner_id_name
                    if not p_id:
                        p_id='00000%d' %(r.partner_id.id)
                        self.write(
                            {'r.partner_id_name': p_id} )

                    r.partner_id.write({
                    'id_numbers': [
                    (0,0, {'category_id': 1, 'name': p_id})]})

                order=r.env['sale.order'].create({
                'partner_id': r.partner_id.id,
                'pricelist_id': 1,
   #             'user_id': r.event_id.user_id.id,               # r.user_id.id,
                'date_order': r.write_date,
                'client_order_ref': r.product_id.partner_ref,
                'company_id': r.user_id.company_id.id,
                'payment_term_id':1,
                    'team_id':2,
                })

                order_line=r.env['sale.order.line'].create(
                {   'product_id': r.product_id.id,
                    'name': r.product_id.name,
                    'order_id': order.id,
                    'product_uom' : r.product_id.uom_id.id,
                    'product_uom_qty':1,
                    'customer_lead':1,
                    })
                order_line.product_id_change()
                if previuos_amount:
                    order_line.write(
                        {'price_unit': order_line.price_unit-previuos_amount})




                # Calling an onchange method to update the record
                # r.env['event.event.ticket'].search([('event_id','=',r.event_id.id)])[0]
                # # pero no estan los ponentes
                register=r.env['event.registration'].create(
                { 'origin':r.product_id.name,
                      'event_id':r.event_id.id,
                      'company_id': r.user_id.company_id.id,
                      'partner_id': r.partner_id.id,
                      'state':'open',
                      'email': r.partner_id.email,
                      'phone':r.partner_id.phone,
                      'name': r.partner_id.name,
                   #   'event_ticket_id':r.product_id.id,
                      'sale_order_id':order.id ,
                      'sale_order_line_id':order_line.id ,
                      'attendee_partner_id':r.partner_id.id,
                      'date_open':r.write_date,
                  })
                order.action_confirm()
             #   order.action_quotation_send()
                for i in order.action_invoice_create():
                    invoice=r.env['account.invoice'].search([('id', '=', i)])
                    invoice.action_invoice_open()
     #               invoice.action_invoice_sent()
                    if previuos_amount:
                        mtemp = r.env['mail.template'].search([('name', '=', 'FACTURA_AJUSTE')])
                    else:
                        mtemp=r.env['mail.template'].search([('name', '=', 'PROPUESTA_ACEPTADA')])
                    if mtemp:
                        mtemp[0].send_mail(r.id)
                this_run+=1



            except Exception as e:
                pass
        return


#    @api.multi
    def _get_users_from_group(self,g_id):
        if not g_id:
            return [1]
        users_ids = []
        sql_query = """select uid from res_groups_users_rel where gid = %s"""
        params = (g_id,)
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.fetchall()
        for users_id in results:
            users_ids.append(users_id[0])
        return users_ids

    @api.multi
    def write(self, vals):
#        if self.product_id.id in (14,15)  and self.type_id.id!=2:
 #           raise ValidationError('ERROR: No coincide tipo de ponencia y tipo de ponente, corrija por favor')

        res = super(Track, self).write(vals)
        if vals.get('user_id'):
            self.message_subscribe([vals['user_id']])
        return res

    @api.multi
    def create(self,vals):
        users = []
        n = self.env['event.event'].search(
            [('id', '=', vals.get('event_id'))]).tracks_limit
        x =  self.env['event.track'].search_count(
                [('user_id', '=', self.env.user.id)])
        if  x > n:
           raise ValidationError('ERROR No puede enviar más propuestas. Ya propuso %d. Máximo %d por persona. '%(x,n))
        if len(vals.get('resumen').split()) > 500:
            raise ValidationError('ERROR: Resúmen tiene más de 500 palabras, corrija por favor')


        if 'stage_id' in vals and 'kanban_state' not in vals:
            vals['kanban_state'] = 'normal'
#        if vals.get('product_id') in (14, 15) and vals.get('type_id') != 2:
#            raise ValidationError('ERROR: No coincide tipo de ponencia y tipo de ponente, corrija por favor')

        if not vals.get('partner_id'):
            vals['partner_id']=self.env.user.partner_id.id

        vals['partner_email']=self.env.user.partner_id.email
        vals['partner_name'] = self.env.user.partner_id.name

        if vals.get('theme_tag'):
            ftag=vals.get('theme_tag')
            gid=self.env['event.track.theme'].search(
                [('id', '=', ftag)])[0].group_id.id

            users= self. _get_users_from_group(gid)
        if len(users):
            vals['user_id'] = users[0]

        res=super(Track, self).create(vals)
        return res
        # self.message_subscribe_users(user_ids = [self.env.user])
        # if len(users):
        #    self.message_subscribe_users(user_ids=users)
