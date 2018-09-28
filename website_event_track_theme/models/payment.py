from odoo import fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class EventEventPayment(models.Model):
    _inherit = 'account.payment'
    _name ='account.payment'
    reported = fields.Boolean('Reported', default=False)

    def yesterday_payments(self):
        fsep = '|'
        lines=''
        fname='EGAL FACT_'+datetime.now().strftime('%Y-%m-%d')+'.txt'

        payments = self.env['account.payment'].search(
            [('reported', '=', False),
             ('payment_type','=','inbound'),])
        if not payments:
            return
        error_list=''
        for p in payments:
            try:
                line = 'TE1' + fsep
                line += p.partner_id.name.encode('ASCII', 'ignore').upper().decode("utf-8")[:35] + fsep
                line += p.partner_id.id_numbers.name[:20] + fsep
                line += 'C05' + fsep
                line += 'DR1' + fsep
                line += p.partner_id.street[:30] + fsep
                line += p.partner_id.country_id.alpha3 + fsep
                line += p.partner_id.email[:35] + fsep
                lh1 = 'H' + fsep
                lh1 += p.partner_id.id_numbers.name[:20] + fsep
                lh1 += p.partner_id.id_numbers.name[:20] + fsep
                lh1 += 'PAGOS VARIOS' + fsep
                lh1 += '{:.2f}'.format(p.amount) + fsep
                lh1 += '0.00' + fsep
                lh1 += p.payment_date[:4] + p.payment_date[5:][:2] + p.payment_date[8:][:2]
                lh2 = 'L' + fsep
                lh2 += p.partner_id.id_numbers.name[:20] + fsep
                lh2 += '1'+ fsep
                lh2 += 'EGAL' + fsep
                lh2 += '{:.2f}'.format(p.amount) + fsep
                lh2 += '41020201' + fsep
                lh2 += 'IN123' + fsep
                lh2 += '163041' + fsep
                lh2 += 'O14163' + fsep
                lh2+= ' ' + fsep
                lh2 += ' ' + fsep
                lh2 += '002' + fsep
                lh2 += 'C' + fsep
                lines+=line+'\n'+lh1+'\n'+lh2+'\n'
                p.write({'reported':True})
            except:
                _logger.error('Datos incompletos. Ver  pago: '+p.payment_transaction_id.display_name )
                error_list+='Datos incompletos. Ver  pago: '+p.payment_transaction_id.display_name
                continue
        contacts = self.env['res.partner'].search([('parent_id.id', '=', 40), ('function', '=', 'Finanzas')])
        attachments = [(fname,lines)]
        body="Ver archivo adjunto ("+fname+')'
        subject=fname
        for c in contacts:
            c.message_post(body=body,
                           subject=subject, message_type='notification',
                           subtype='mail.mt_comment',
                           attachments=attachments)
        if error_list != '':
            contacts = self.env['res.partner'].search([('id', '=', 7)])
            attachments = [(fname,lines)]
            body="Ver archivo adjunto ("+fname+')'
            subject=fname
            for c in contacts:
                c.message_post(body=error_list,
                               subject='Datos incompletos en Facturas', message_type='notification',
                               subtype='mail.mt_comment',
                               attachments=attachments)
