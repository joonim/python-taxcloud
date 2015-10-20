import decimal
import random
import string
import unittest
from faker import Faker
from flexmock import flexmock
from taxcloud.address import Address
from taxcloud.cart_item import CartItem
from taxcloud.config import TaxCloudConfig


class TaxcloudTest(unittest.TestCase):
    def setUp(self):
        super(TaxcloudTest, self).setUp()
        self._fake = Faker()
        self._factory = TestFactory(self._fake)

class TestFactory(object):
    SAMPLE_TICS = (00000, 10010, 20150, 20070, 20110, 31000, 52260, 91051, 90114)

    def __init__(self, faker):
        self._fake = faker

    def create_config(self):
        return TaxCloudConfig(api_login_id='......', api_key='.............')

    def create_ping_response(self):
        return flexmock(ResponseType='OK')

    def create_lookup_response(self):
        items = []
        for i in xrange(1, 4):
            items.append(flexmock(CartItemIndex=i, TaxAmount=float(random.randrange(200))/100))
        CartItemResponse = flexmock(CartItemResponse=items)
        return flexmock(CartID=random.randint(1000000, 100000000), CartItemsResponse=CartItemResponse)

    def create_errors_response(self):
        messages = []
        for i in xrange(2):
            messages.append(flexmock(ResponseType='Error', Message="Error code: %s" % random.randint(100, 1000) ))
        ResponseMessage = flexmock(ResponseMessage=messages)
        return flexmock(Messages=ResponseMessage)


    def create_address(self, address1, city, state, zip_code, address2=''):
        return Address(address1=address1, address2=address2, city=city, state=state, zip_code=zip_code)

    def sample_address(self, size):
        result = []
        for i in xrange(size):
            result.append(self.create_address(address1=self._fake.street_address(), city=self._fake.city(),
                                              state=self._fake.state(), zip_code=self._fake.zipcode()))
        return result

    def sample_cart_items(self, size):
        result = []
        for i in xrange(size):
            tic = random.choice(self.SAMPLE_TICS)
            item_id = "%s%s" % (random.choice(string.uppercase), random.randint(100000, 1000000))
            price = decimal.Decimal(random.randrange(10000)) / 100
            qty = random.randint(1, 3)

            result.append(CartItem(tic=tic, item_id=item_id, price=price, qty=qty))
        return result
