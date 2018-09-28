# -*- coding: utf-8 -*-
import unittest
import odoo
from odoo import fields
from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.tools import mute_logger


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class kushkiCommon(PaymentAcquirerCommon):

    def setUp(self):
        super(kushkiCommon, self).setUp()
        self.kushki = self.env.ref('payment.payment_acquirer_kushki')


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class kushkiTest(kushkiCommon):

    @unittest.skip("kushki test disabled: We do not want to overload kushki with runbot's requests")
    def test_10_kushki_s2s(self):
        self.assertEqual(self.kushki.environment, 'test', 'test without test environment')

        # Add kushki credentials
        self.kushki.write({
            'kushki_secret_key': 'sk_test_bldAlqh1U24L5HtRF9mBFpK7',
            'kushki_publishable_key': 'pk_test_0TKSyYSZS9AcS4keZ2cxQQCW',
        })

        # Create payment meethod for kushki
        payment_token = self.env['payment.token'].create({
            'acquirer_id': self.kushki.id,
            'partner_id': self.buyer_id,
            'cc_number': '4242424242424242',
            'cc_expiry': '02 / 26',
            'cc_brand': 'visa',
            'cvc': '111',
            'cc_holder_name': 'Johndoe',
        })

        # Create transaction
        tx = self.env['payment.transaction'].create({
            'reference': 'test_ref_%s' % fields.date.today(),
            'currency_id': self.currency_euro.id,
            'acquirer_id': self.kushki.id,
            'partner_id': self.buyer_id,
            'payment_token_id': payment_token.id,
            'type': 'server2server',
            'amount': 115.0
        })
        tx.kushki_s2s_do_transaction()

        # Check state
        self.assertEqual(tx.state, 'done', 'kushki: Transcation has been discarded.')

    @unittest.skip("kushki test disabled: We do not want to overload kushki with runbot's requests")
    def test_20_kushki_form_render(self):
        self.assertEqual(self.kushki.environment, 'test', 'test without test environment')

        # ----------------------------------------
        # Test: button direct rendering
        # ----------------------------------------
        form_values = {
            'amount': 320.0,
            'currency': 'EUR',
            'address_line1': 'Huge Street 2/543',
            'address_city': 'Sin City',
            'address_country': 'Belgium',
            'email': 'norbert.buyer@example.com',
            'address_zip': '1000',
            'name': 'Norbert Buyer',
            'phone': '0032 12 34 56 78'
        }

        # render the button
        res = self.kushki.render('SO404', 320.0, self.currency_euro.id, values=self.buyer_values)
        post_url = "https://checkout.kushki.com/checkout.js"
        email = "norbert.buyer@example.com"
        # check form result
        if "https://checkout.kushki.com/checkout.js" in res[0]:
            self.assertEqual(post_url, 'https://checkout.kushki.com/checkout.js', 'kushki: wrong form POST url')
        # Generated and received
        if email in res[0]:
            self.assertEqual(
                email, form_values.get('email'),
                'kushki: wrong value for input %s: received %s instead of %s' % (email, email, form_values.get('email'))
            )

    @unittest.skip("kushki test disabled: We do not want to overload kushki with runbot's requests")
    def test_30_kushki_form_management(self):
        self.assertEqual(self.kushki.environment, 'test', 'test without test environment')

        # typical data posted by kushki after client has successfully paid
        kushki_post_data = {
            u'amount': 4700,
            u'amount_refunded': 0,
            u'application_fee': None,
            u'balance_transaction': u'txn_172xfnGMfVJxozLwssrsQZyT',
            u'captured': True,
            u'created': 1446529775,
            u'currency': u'eur',
            u'customer': None,
            u'description': None,
            u'destination': None,
            u'dispute': None,
            u'failure_code': None,
            u'failure_message': None,
            u'fraud_details': {},
            u'id': u'ch_172xfnGMfVJxozLwEjSfpfxD',
            u'invoice': None,
            u'livemode': False,
            u'metadata': {u'reference': u'SO100'},
            u'object': u'charge',
            u'paid': True,
            u'receipt_email': None,
            u'receipt_number': None,
            u'refunded': False,
            u'refunds': {u'data': [],
                         u'has_more': False,
                         u'object': u'list',
                         u'total_count': 0,
                         u'url': u'/v1/charges/ch_172xfnGMfVJxozLwEjSfpfxD/refunds'},
            u'shipping': None,
            u'source': {u'address_city': None,
                        u'address_country': None,
                        u'address_line1': None,
                        u'address_line1_check': None,
                        u'address_line2': None,
                        u'address_state': None,
                        u'address_zip': None,
                        u'address_zip_check': None,
                        u'brand': u'Visa',
                        u'country': u'US',
                        u'customer': None,
                        u'cvc_check': u'pass',
                        u'dynamic_last4': None,
                        u'exp_month': 2,
                        u'exp_year': 2022,
                        u'fingerprint': u'9tJA9bUEuvEb3Ell',
                        u'funding': u'credit',
                        u'id': u'card_172xfjGMfVJxozLw1QO6gYNM',
                        u'last4': u'4242',
                        u'metadata': {},
                        u'name': u'norbert.buyer@example.com',
                        u'object': u'card',
                        u'tokenization_method': None},
            u'statement_descriptor': None,
            u'status': u'succeeded'}

        tx = self.env['payment.transaction'].create({
            'amount': 4700,
            'acquirer_id': self.kushki.id,
            'currency_id': self.currency_euro.id,
            'reference': 'SO100',
            'partner_name': 'Norbert Buyer',
            'partner_country_id': self.country_france.id})

        # validate it
        tx.form_feedback(kushki_post_data, 'kushki')
        self.assertEqual(tx.state, 'done', 'kushki: validation did not put tx into done state')
        self.assertEqual(tx.acquirer_reference, kushki_post_data.get('id'), 'kushki: validation did not update tx id')
        # reset tx
        tx.write({'state': 'draft', 'date_validate': False, 'acquirer_reference': False})
        # simulate an error
        kushki_post_data['status'] = 'error'
        kushki_post_data.update({u'error': {u'message': u"Your card's expiration year is invalid.", u'code': u'invalid_expiry_year', u'type': u'card_error', u'param': u'exp_year'}})
        with mute_logger('odoo.addons.payment_kushki.models.payment'):
            tx.form_feedback(kushki_post_data, 'kushki')
        # check state
        self.assertEqual(tx.state, 'error', 'Stipe: erroneous validation did not put tx into error state')
