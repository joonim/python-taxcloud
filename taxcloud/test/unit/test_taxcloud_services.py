import random
import unittest
from flexmock import flexmock
from taxcloud import taxcloud_services
from taxcloud.test.utils import TaxcloudTest


class PingTest(TaxcloudTest):
    def test_ping(self):
        ping = taxcloud_services.Ping(self._factory.create_config())
        flexmock(ping).should_receive('_request').and_return(self._factory.create_ping_response())
        ping.request()
        self.assertEqual(ping.response.ResponseType, 'OK')


class LookupTest(TaxcloudTest):
    def setUp(self):
        super(LookupTest, self).setUp()
        self.customer_id = random.randint(10000, 10000000)
        self.cart_id = random.randint(10000, 100000000)
        self.taxcloud_config = self._factory.create_config()

    def test_it_should_have_sale_taxes_and_cart_id(self):
        self.given_cart_items_and_addresses()
        lookup = self._create_lookup()
        flexmock(lookup).should_receive('_request').and_return(self._factory.create_lookup_response())
        lookup.request()
        self.assertIsNotNone(lookup.tax)
        self.assertIsNotNone(lookup.cart_id)
        self.assertEqual(len(lookup.error_messages), 0)

    def test_it_should_return_error_messages(self):
        self.given_invalid_cart_items_and_addresses()
        lookup = self._create_lookup()
        flexmock(lookup).should_receive('_request').and_return(self._factory.create_errors_response())
        lookup.request()
        self.assertIsNone(lookup.tax)
        self.assertGreater(len(lookup.error_messages), 0)

    def given_cart_items_and_addresses(self):
        self.cart_items = self._factory.sample_cart_items(3)
        sample_addresses = self._factory.sample_address(2)
        self.origin_address = sample_addresses[0]
        self.destination_address = sample_addresses[1]

    def given_invalid_cart_items_and_addresses(self):
        self.given_cart_items_and_addresses()

    def _create_lookup(self):
        return taxcloud_services.Lookup(self.taxcloud_config,
                                        customer_id=self.customer_id,
                                        cart_items=self.cart_items,
                                        destination=self.destination_address,
                                        origin=self.origin_address)

class AuthorizedWithCaptureTest(TaxcloudTest):
    def setUp(self):
        super(AuthorizedWithCaptureTest, self).setUp()
        self.customer_id = random.randint(10000, 10000000)
        self.cart_id = random.randint(10000, 100000000)
        self.order_id = random.randint(10000, 100000000)
        self.taxcloud_config = self._factory.create_config()

    def test_it_should_return_ok(self):
        authCapture = taxcloud_services.AuthorizedWithCapture(config=self.taxcloud_config,
                                                       customer_id=self.customer_id,
                                                       cart_id=self.cart_id,
                                                       order_id=self.order_id)
        flexmock(authCapture).should_receive('_request').and_return(self._factory.create_ping_response())
        authCapture.request()
        self.assertEqual(authCapture.response.ResponseType, 'OK')


class ReturnedTest(TaxcloudTest):
    def setUp(self):
        super(ReturnedTest, self).setUp()
        self.customer_id = random.randint(10000, 10000000)
        self.order_id = random.randint(10000, 100000000)
        self.taxcloud_config = self._factory.create_config()
        self.cart_items = self._factory.sample_cart_items(3)

    def test_it_should_return_ok(self):
        refunted = taxcloud_services.Returned(config=self.taxcloud_config, order_id=self.order_id, cart_items=self.cart_items)
        flexmock(refunted).should_receive('_request').and_return(self._factory.create_ping_response())
        refunted.request()
        self.assertEqual(refunted.response.ResponseType, 'OK')