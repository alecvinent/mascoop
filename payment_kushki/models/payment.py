# coding: utf-8

import logging
import requests
import json
import re
import pprint

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

# Force the API version to avoid breaking in case of update on kushki side
# cf https://kushki.com/docs/api#versioning
# changelog https://kushki.com/docs/upgrades#api-changelog



kushki_api_codes = {
    'K001':	'EL CUERPO DE LA PETICIÓN ES INVÁLIDO',
    'K002':	'HA OCURRIDO UN ERROR INESPERADO',
    'K003':	'TARJETA NO HABILITADA POR EL EMISOR',
    'K004':	'ID DE COMERCIO NO VÁLIDO',
    'K005':	'TOKEN EXPIRADO',
    'K006':	'MONTO NO ES IGUAL AL ESPERADO',
    'K007':	'ESTE RECIBO YA FUÉ PAGADO',
    'K008':	'ESTE RECIBO YA FUÉ CANCELADO',
    'K009':	'RECIBO EXPIRADO',
    'K010':	'TICKET NUMBER INVÁLIDO',
    'K011':	'CREDENCIALES INVÁLIDAS',
    'K012':	'ACCESO NO AUTORIZADO',
    'K013':	'ACCESO NO PERMITIDO',
    'K014':	'TOKEN INVÁLIDO'
}
kushki_error_code={
    '0000':'TRANSACCIÓN APROBADA',
    '0004':'INFORMACIÓN DE CUENTA NO VÁLIDA',
    '0005':'NÚMERO DE CUENTA NO VÁLIDO',
    '0006':'TRANSACCIÓN RECHAZADA',
    '0007':'CVC NO VÁLIDO',
    '0008':'NÚMERO DE PIN NO VALIDO',
    '0017':'TARJETA NO VÁLIDA',
    '0018':'TARJETA VENCIDA',
    '0019':'FONDOS INSUFICIENTES PARA REMBOLSOS',
    '0021':'TARJETA NO COMPATIBLE',
    '0022':'TIPO DE TARJETA NO COMPATIBLE POR MRC',
    '0023':'FECHA DE EXPIRACIÓN NO VÁLIDA',
    '0201':'ID DE COMERCIO NO VÁLIDO',
    '0202':'TIPO DE TRANSACCIÓN NO VÁLIDO',
    '0203':'MONTO DE TRANSACCIÓN NO VÁLIDO',
    '0205':'TIPO DE MONEDA NO VÁLIDA',
    '0207':'ID DE TRANSACCIÓN NO VÁLIDO',
    '0211':'SOLICITUD NO VÁLIDA',
    '0212':'INFORMACIÓN ENCRIPTADA NO VÁLIDA',
    '0215':'EL COMERCION NO TIENE PERMISO PARA PROCESAR UNA TRANSACCIÓN',
    '0216':'TRANSACCIÓN REEMBOLSADA',
    '0219':'EL MONTO ES ZERO',
    '0220':'MONTO DE LA TRANSACCIÓN ES DIFERENTE AL MONTO DE LA VENTA INICIAL',
    '0222':'TRANSACCIÓN NO ENCONTRADA',
    '0223':'TRANSACCIÓN NO SOPORTADA',
    '0225':'TIPO DE TRANSACCIÓN NO VÁLIDO',
    '0226':'PROCESADOR CC NO ASIGNADO',
    '0227':'PROCESADOR GC NO ASIGNADO',
    '0228':'PROCESADOR INALCANZABLE',
    '0229':'EL COMERCIO NO SOPORTA LA TRANSACCIÓN',
    '0231':'ANULACIÓN DE VENTA NO PERMITIDA',
    '0238':'TRANSACCÓN ANULADA',
    '0277':'IDICADOR DE IDIOMA NO VÁLIDO',
    '0297':'TICKET DE AURUSPAY NO VÁLIDO',
    '0322':'TRANSACCIÓN NO PERMITIDA',
    '0478':'SERVIDOR NO DISPONIBLE',
    '0577':'EL TOKEN DE LA TRANSACCIÓN NO ES VÁLIDO',
    '0578':'EL TOKEN DE LA TRANSACCIÓN HA EXPIRADO',
    '0579':'TRANSACCIÓN RECHAZADA',
    '0597':'NO HAY RESPUESTA DEL PROCESADOR',
    '0701':'EL TOKEN DE LA TRANSACCIÓN ES REQUERIDO',
    '0702':'EL MONTO DE LA TRANSACCIÓN NO ES VÁLIDO',
    '0703':'EL MONTO DE LA TRANSACCIÓN ES REQUERIDO',
    '0704':'EL NÚMERO DE TICKET DE LA TRANSACCIÓN NO ES VÁLIDO',
    '0705':'EL NÚMERO DE TICKET DE LA TRANSACCIÓN ES REQUERIDO',
    '0706':'LA CANTIDAD DE MESES ES REQUERIDA',
    '0707':'LA CANTIDAD DE MESES NO ES VÁLIDA',
    '0708':'LA TASA DE INTERÉS ES REQUERIDA',
    '0709':'LA TASA DE INTERÉS NO ES VÁLIDA',
    '0710':'EL COMERCIANTE NO HA SIDO ENCONTRADO',
    '0886':'EL CAMPO "REMEMBER_ME" ES OBLIGATORIO',
    '0887':'EL CAMPO "REMEMBER_ME" NO ES VÁLIDO',
    '0890':'DATOS NO ENCONTRADOS',
    '0891':'EL CAMPO "CARD_PRESENT" ES OBLIGATORIO',
    '0892':'EL CAMPO "CARD_PRESENT" NO ES VÁLIDO',
    '0893':'EL CAMPO "DEFERRED_PAYMENT" ES OBLIGATORIO',
    '0894':'EL CAMPO "DEFERRED_PAYMENT" NO ES VÁLIDO',
    '1000':'EL ID DE LA TARJETA ES REQUERIDA',
    '1001':'EL TOKEN DE LA TARJETA NO ES VÁLIDO',
    '1002':'EL NOMBRE DEL CONSUMIDOR ES REQUERIDO',
    '1003':'EL NOMBRE DEL CONSUMIDOR NO ES VÁLIDO',
    '1004':'EL APELLIDO DEL CONSUMIDOR ES REQUERIDO',
    '1005':'EL APELLIDO DEL CONSUMIDOR NO ES VÁLIDO',
    '1006':'NOMBRE DEL PLAN ES REQUERIDO',
    '1007':'NOMBRE DEL PLAN NO ES VÁLIDO',
    '1008':'FECHA DE INICIO ES REQUERIDA',
    '1009':'FECHA DE INICIO NO ES VÁLIDA',
    '1010':'EL CAMPO "SCHEDULE FLAG" ES REQUERIDO',
    '1011':'EL CAMPO "SCHEDULE FLAG" NO ES VÁLIDO',
    '1012':'EL TIPO DE HORARIO ES REQUERIDO',
    '1013':'EL TIPO DE HORARIO NO ES VÁLIDO',
    '1014':'EL TIPO DE AJUSTE NO ES VÁLIDO',
    '1015':'LA FECHA DE AJUSTE NO ES VÁLIDA',
    '1016':'EL MONTO DE AJUSTE NO ES VÁLIDO',
    '1017':'LOS PERIODOS DE AJUSTE NO SON VÁLIDOS',
    '1018':'NO ES POSIBLE AGREGAR SUBSCRIPCIÓN',
    '1019':'TOKEN DE SUBSCRIPCIÓN NO ENCONTRADO',
    '1020':'ERROR EN LA CREACIÓN DE LA SUBSCRIPCIÓN',
    '1021':'EL ID DE SUBSCRIPCIÓN ES REQUERIDO',
    '1022':'EL ID DE SUBSCRIPCIÓN NO ES VÁLIDO',
    '1023':'EL CAMPO "PLANID" NO ES VALIDO',
    '1024':'LA FECHA DE FINALIDAD NO ES VÁLIDA',
    '1025':'DIA DEL MES NO ES VÁLIDO',
    '1026':'ERROR AL ELIMINAR LA SUBSCRIPCIÓN',
    '1027':'ID DE SUBSCRIPCIÓN NO ENCONTRADO',
    '1028':'ERROR AL ACTUALIZAR LA SUBSCRIPCIÓN',
    '1029':'TOKEN DE SUBSCRIPCIÓN EXPIRADO',
    '1030':'EL CAMPO "LIST COUNT" NO ES VÁLIDO',
    '1031':'LA FECHA DE FINALIDAD ES REQUERIDA',
    '1032':'NO HAY SUSCRIPCIONES PARA ID COMERCIANTE Y LISTA COUNT',
    '1033':'AJUSTE NO VÁLIDO: MONTO SUBTOTALIVA',
    '1034':'AJUSTE NO VÁLIDO: MONTO IVA',
    '1035':'AJUSTE NO VÁLIDO: MONTO SUBTOTALIVA0',
    '1036':'AJUSTE NO VÁLIDO: MONTO ICE'
}

payload={}

class PaymentAcquirerkushki(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('kushki', 'kushki')])
    kushki_image_url = fields.Char(
        "Checkout Image URL", groups='base.group_user',
        help="A relative or absolute URL pointing to a square image of your "
             "brand or product. As defined in your kushki profile. See: "
             "https://docs.kushkipagos.com")
    test_url = fields.Char(required_if_provider='kushki', groups='base.group_user')
    test_private_key = fields.Char(required_if_provider='kushki', groups='base.group_user')
    test_public_key = fields.Char(required_if_provider='kushki', groups='base.group_user')
    prod_url = fields.Char(required_if_provider='kushki', groups='base.group_user')
    prod_private_key = fields.Char(required_if_provider='kushki', groups='base.group_user')
    prod_public_key = fields.Char(required_if_provider='kushki', groups='base.group_user')

    @api.multi
    def kushki_form_generate_values(self, tx_values):
        self.ensure_one()
        kushki_tx_values = dict(tx_values)
        temp_kushki_tx_values = {
            'company': self.company_id.name,
            'amount': tx_values['amount'],  # Mandatory
            'currency': tx_values['currency'].name,  # Mandatory anyway
            'currency_id': tx_values['currency'].id,  # same here
            'address_line1': tx_values.get('partner_address'),  # Any info of the partner is not mandatory
            'address_city': tx_values.get('partner_city'),
            'address_country': tx_values.get('partner_country') and tx_values.get('partner_country').name or '',
            'email': tx_values.get('partner_email'),
            'address_zip': tx_values.get('partner_zip'),
            'name': tx_values.get('partner_name'),
            'phone': tx_values.get('partner_phone'),
        }

        temp_kushki_tx_values['returndata'] = kushki_tx_values.pop('return_url', '')
        kushki_tx_values.update(temp_kushki_tx_values)
        return kushki_tx_values

    @api.model
    def _get_kushki_api_url(self):
        if self.environment == 'test':
            api_url = self.test_url
            key_pub = self.test_public_key
            key_priv = self.test_private_key
        else:
            api_url= self.prod_url
            key_pub = self.prod_public_key
            key_priv = self.prod_private_key
        return{'url': api_url, 'pub': key_pub, 'priv': key_priv }

    @api.model
    def kushki_s2s_form_process(self, data):
        payment_token = self.env['payment.token'].sudo().create({
            'number': data['cc_number'],
            'name': data['cc_holder_name'],
            'expiryMonth': data['cc_expiry'][:2],
            'expiryYear': data['cc_expiry'][-2:],
            'cvv': data['cvc'],
            'acquirer_id': int(data['acquirer_id']),
            'partner_id': int(data['partner_id']),
            'acquirer_ref': '99999',
        })
        return payment_token

    @api.multi
    def kushki_s2s_form_validate(self, data):
        self.ensure_one()

        # mandatory fields
        for field_name in ["cc_number", "cvc", "cc_holder_name", "cc_expiry", "cc_brand"]:
            if not data.get(field_name):
                return False
        return True

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(PaymentAcquirerkushki, self)._get_feature_support()
        res['tokenize'].append('kushki')
 #       res['authorize'].append('kushki')
        return res


class PaymentTransactionkushki(models.Model):
    _inherit = 'payment.transaction'

    def _create_kushki_charge(self, acquirer_ref=None, tokenid=None, email=None):
        valapi = self.acquirer_id._get_kushki_api_url()
        api_url_token = '%s/tokens' % (valapi['url'])
        api_url_charge = '%s/charges' % (valapi['url'])
        headers = {'Public-Merchant-Id': valapi['pub'], 'content-type': 'application/json'}

        global payload
        payload['totalAmount']=self.amount

        data_string = json.dumps(payload)
        token = requests.request("POST", api_url_token, data=data_string, headers=headers)
        if token.ok :
            mtd = "6"
            result = re.sub('[^0-9]', '0', self.partner_id.id_numbers.name)
            mtd += result.ljust(10, '0')[:10]
            mtd += '01'
            mtd += self.partner_id.name.encode('ASCII', 'ignore').upper().decode("utf-8").ljust(30, ' ')[:30]
            mtd += self.partner_id.id_numbers.name.ljust(10, ' ')[:10]
            mtd += '{:.2f}'.format(self.amount).rjust(12, '0')[:12]
            mtd += '000000000.00'
            mtd += '000000000.00'
            mtd += '{:.2f}'.format(self.amount).rjust(12, '0')[:12]
            mtd += 'C'
            mtd += '00'
            mtd += '00000000'
            mtd += '000'
            cd = datetime.strptime(create_date, '%d/%m/%Y %H:%M:%S')
            mtd += cd.strftime('%Y%m%d%H%M%S')

            charge = {
                 "token": token.text[10:-2],
                 "amount": {
                  "subtotalIva": 0,
                  "subtotalIva0": self.amount,
                  "ice": 0,
                  "iva": 0,
                  "currency": "USD"
                 },
                 "months": 0,
                "metadata":mtd
                }

            data_charge = json.dumps(charge)
            headers = {'Private-Merchant-Id': valapi['priv'],'content-type': 'application/json'}
            r = requests.request("POST", api_url_charge, data=data_charge, headers=headers)
        return token


    @api.multi
    def kushki_s2s_do_transaction(self, **kwargs):
        self.ensure_one()
        result = self._create_kushki_charge(acquirer_ref=self.payment_token_id.acquirer_ref)
        return self._kushki_s2s_validate_tree(result)


    def _create_kushki_refund(self):
        api_url_refund = 'https://%s/refunds' % (self.acquirer_id._get_kushki_api_url())

        refund_params = {
            'charge': self.acquirer_reference,
            'amount': int(self.amount*100), # by default, kushki refund the full amount (we don't really need to specify the value)
            'metadata[reference]': self.reference,
        }

        r = requests.post(api_url_refund,
                            auth=(self.acquirer_id.kushki_secret_key, ''),
                            params=refund_params,
                            headers=kushki_HEADERS)
        return r.json()

    @api.multi
    def kushki_s2s_do_refund(self, **kwargs):
        self.ensure_one()
        self.state = 'refunding'
        result = self._create_kushki_refund()
        return self._kushki_s2s_validate_tree(result)

    @api.model
    def _kushki_form_get_tx_from_data(self, data):
        """ Given a data dict coming from kushki, verify it and find the related
        transaction record. """
        reference = data.get('metadata', {}).get('reference')
        if not reference:
            kushki_error = data.get('error', {}).get('message', '')
            _logger.error('kushki: invalid reply received from kushki API, looks like '
                          'the transaction failed. (error: %s)', kushki_error  or 'n/a')
            error_msg = _("We're sorry to report that the transaction has failed.")
            if kushki_error:
                error_msg += " " + (_("kushki gave us the following info about the problem: '%s'") %
                                    kushki_error)
            error_msg += " " + _("Perhaps the problem can be solved by double-checking your "
                                 "credit card details, or contacting your bank?")
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference)])
        if not tx:
            error_msg = (_('kushki: no order found for reference %s') % reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = (_('kushki: %s orders found for reference %s') % (len(tx), reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx[0]

    @api.multi
    def _kushki_s2s_validate_tree(self, tree):
        self.ensure_one()
        if self.state not in ('draft', 'pending', 'refunding'):
            _logger.info('kushki: trying to validate an already validated tx (ref %s)', self.reference)
            return True


        if tree.ok :
            new_state = 'refunded' if self.state == 'refunding' else 'done'
            self.write({
                'state': new_state,
                'date_validate': fields.datetime.now(),
                'acquirer_reference': tree.text[10:-2],
            })
            self.execute_callback()
            if self.payment_token_id:
                self.payment_token_id.verified = True
            return True
        else:
            error = tree.reason
            _logger.warn(error)
            self.sudo().write({
                'state': 'error',
                'state_message': error,
                'acquirer_reference': tree.get('id'),
                'date_validate': fields.datetime.now(),
            })
            return False

    @api.multi
    def _kushki_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        reference = data['metadata']['reference']
        if reference != self.reference:
            invalid_parameters.append(('Reference', reference, self.reference))
        return invalid_parameters

    @api.multi
    def _kushki_form_validate(self,  data):
        return self._kushki_s2s_validate_tree(data)


class PaymentTokenkushki(models.Model):
    _inherit = 'payment.token'


    @api.model
    def kushki_create(self, values):
        token = values.get('kushki_token')
        description = None
        payment_acquirer = self.env['payment.acquirer'].browse(values.get('acquirer_id'))
        # when asking to create a token on kushki servers
        valapi = payment_acquirer._get_kushki_api_url()
        api_url_token = 'https://%s/tokens' % (valapi['url'])
        headers = {'Public-Merchant-Id': valapi['pub'], 'content-type': 'application/json'}

        global payload
        payload = {"card": {
            "name": values['name'],
            "number": values['number'].replace(' ', ''),
            "expiryMonth":str(values['expiryMonth'][:2]),
            "expiryYear": str(values['expiryYear'][-2:]),
            "cvv": values['cvv']
        },
            "totalAmount": 10.0, ## get self.amount,
            "currency": "USD",
            "isDeferred": False
        }


        description = values['name']

        res = self._kushki_create_customer('mitoken', description, payment_acquirer.id)

#         pop credit card info to info sent to create
        for field_name in ["number", "cvv", "name", "expiryMonth", "expiryYear"]:
             values.pop(field_name, None)
        return res

    def _kushki_create_customer(self, token, description=None, acquirer_id=None):
 #       if token.get('error'):
 #           _logger.error('payment.token.kushki_create_customer: Token error:\n%s', pprint.pformat(token['error']))
 #           raise Exception(token['error']['message'])

 #       if token['object'] != 'token':
 #           _logger.error('payment.token.kushki_create_customer: Cannot create a customer for object type "%s"',
 #                         token.get('object'))
 #           raise Exception('We are unable to process your credit card information.')

  #      if token['type'] != 'card':
  #          _logger.error('payment.token.kushki_create_customer: Cannot create a customer for token type "%s"',
  #                        token.get('type'))
  #          raise Exception('We are unable to process your credit card information.')

  #      values = {
  #          'acquirer_ref': customer['id'],
  #          'name': 'XXXXXXXXXXXX%s - %s' % (token['card']['last4'], customer_params["description"])
  #      }

        global payload

        values = {
            'acquirer_ref': 'xx',
            'name': 'XXXXXXXXXXXX%s - %s' % (payload['card']['number'][-4:], payload['card']['name'])
        }

        return values

