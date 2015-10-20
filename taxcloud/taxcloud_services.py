import logging
import traceback
import suds
import datetime
from suds.client import Client, WebFault
from decimal import Decimal, ROUND_UP

log = logging.getLogger(__name__)


class TaxCloudBaseClient(object):
    """
    parent class. use suds to consume wsdl file.
    """

    def __init__(self, config):
        """
        set config, client, and wsdl objects
        """
        self.config = config
        self.client = Client('file:%s' % self.config.wsdl_path)
        self._errors = []
        self._set_wsdl_objects()

    def _request(self):
        """
        abstract method
        """
        raise NotImplemented

    def _parse(self):
        """
        abstract method
        """
        raise NotImplemented

    def _set_wsdl_objects(self):
        """
        abstract method
        """
        raise NotImplemented

    def request(self):
        """
        this will call on child object
        """
        try:
            self.response = self._request()
            self._parse()
            # if we get error messages, let's set it to _errors
            if hasattr(self.response, 'Messages') and \
                    hasattr(self.response.Messages, 'ResponseMessage'):
                for m in self.response.Messages.ResponseMessage:
                    if hasattr(m, 'Message'):
                        self._errors.append(str(m.Message))
        except WebFault:
            log.error(traceback.format_exc())
            raise

    @property
    def error_messages(self):
        return self._errors


class Ping(TaxCloudBaseClient):
    """
    check if api_login_id/api_key is valid.
    """

    def __init__(self, config):
        self._config = config
        super(Ping, self).__init__(self._config)

    def _set_wsdl_objects(self):
        pass

    def _request(self):
        """
        do not call this directly. call request() instead
        """
        response = self.client.service.Ping(
            apiLoginID=self._config.api_login_id,
            apiKey=self.config.api_key)
        return response

    def _parse(self):
        pass


class Lookup(TaxCloudBaseClient):
    """
    lookup sales tax
    """

    def __init__(self,
                 config,
                 customer_id,
                 cart_items,
                 destination,
                 origin,
                 cart_id=None,
                 is_delivered=0):
        """
        cart_id is not required but if we dont pass, taxcloud will generate one
        """
        self._config = config
        self._customer_id = customer_id
        self._cart_id = cart_id
        self._cart_items = cart_items
        self._destination = destination
        self._origin = origin
        self._is_delivered = is_delivered
        self._tax = None
        super(Lookup, self).__init__(self._config)

    @property
    def tax(self):
        return self._tax

    @property
    def cart_id(self):
        return self._cart_id

    def _request(self):
        kwargs = {
            'apiLoginID': self._config.api_login_id,
            'apiKey': self._config.api_key,
            'customerID': self._customer_id,
            'cartItems': self.cartitems,
            'origin': self.origin_addr,
            'destination': self.destination_addr,
            'deliveredBySeller': self._is_delivered}

        # if we have a cart_id, let's set it otherwise
        # taxcloud will generate one for us.
        if self.cart_id:
            kwargs['cartID'] = self.cart_id

        response = self.client.service.Lookup(**kwargs)
        return response

    def _parse(self):
        if hasattr(self.response, 'CartID'):
            self._cart_id = self.response.CartID
        if self.response and \
                hasattr(self.response, 'CartItemsResponse') and \
                hasattr(self.response.CartItemsResponse, 'CartItemResponse'):
            res_items = self.response.CartItemsResponse.CartItemResponse
            tax = Decimal('0.00')
            for res_item in res_items:
                tax += Decimal(str(res_item.TaxAmount))
            self._tax = tax.quantize(Decimal('.01'), rounding=ROUND_UP)


    def _set_wsdl_objects(self):
        self.origin_addr = self.client.factory.create('Address')
        self.origin_addr.Address1 = self._origin.address1
        self.origin_addr.Address2 = self._origin.address2
        self.origin_addr.City = self._origin.city
        self.origin_addr.State = self._origin.state
        self.origin_addr.Zip5 = self._origin.zip_code

        self.destination_addr = self.client.factory.create('Address')
        self.destination_addr.Address1 = self._destination.address1
        self.destination_addr.Address2 = self._destination.address2
        self.destination_addr.City = self._destination.city
        self.destination_addr.State = self._destination.state
        self.destination_addr.Zip5 = self._destination.zip_code
        self.cartitems = self.client.factory.create('ArrayOfCartItem')
        cart_item_index = 0
        for item in self._cart_items:
            if item.tic:
                cartitem = self.client.factory.create('CartItem')
                cartitem.TIC = item.tic
                cartitem.ItemID = item.item_id
                cartitem.Price = item.price
                cartitem.Qty = item.qty
                cartitem.Index = cart_item_index
                cart_item_index = cart_item_index + 1
                self.cartitems.CartItem.append(cartitem)


class AuthorizedWithCapture(TaxCloudBaseClient):
    """
    call this after customer make a purchase.
    """
    def __init__(self,
                 config,
                 customer_id,
                 cart_id,
                 order_id,
                 date_authorized=None,
                 date_captured=None):
        self._config = config
        self._customer_id = customer_id
        self._cart_id = cart_id
        self._order_id = order_id
        if not date_authorized:
            date_authorized = datetime.datetime.strftime(
                datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
        if not date_captured:
            date_captured = datetime.datetime.strftime(
                datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
        self._date_authorized = date_authorized
        self._date_captured = date_captured
        super(AuthorizedWithCapture,
              self).__init__(self._config)

    def _set_wsdl_objects(self):
        pass

    def _parse(self):
        pass

    def _request(self):
        kwargs = {
            'apiLoginID': self._config.api_login_id,
            'apiKey': self._config.api_key,
            'customerID': self._customer_id,
            'cartID': self._cart_id,
            'orderID': self._order_id,
            'dateAuthorized': self._date_authorized,
            'dateCaptured': self._date_captured}
        response = self.client.service.AuthorizedWithCapture(**kwargs)
        return response


class Returned(TaxCloudBaseClient):
    """
    if customer returned the items, we need to call this
    """
    def __init__(self, config, order_id, cart_items, returned_date=None):
        self._config = config
        self._order_id = order_id
        self._cart_items = cart_items
        if not returned_date:
            returned_date = datetime.datetime.strftime(
                datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%SZ")
        self._returned_date = returned_date

        super(Returned, self).__init__(self._config)

    def _parse(self):
        pass

    def _request(self):
        kwargs = {
            'apiLoginID': self._config.api_login_id,
            'apiKey': self._config.api_key,
            'orderID': self._order_id,
            'cartItems': self.cart_items,
            'returnedDate': self._returned_date
        }
        response = self.client.service.Returned(**kwargs)
        return response

    def _set_wsdl_objects(self):
        self.cart_items = self.client.factory.create('ArrayOfCartItem')
        cart_item_index = 0
        for item in self._cart_items:
            if item.tic:
                cart_item = self.client.factory.create('CartItem')
                cart_item.TIC = item.tic
                cart_item.ItemID = item.item_id
                cart_item.Price = item.price
                cart_item.Qty = item.qty
                cart_item.Index = cart_item_index
                cart_item_index = cart_item_index + 1
                self.cart_items.CartItem.append(cart_item)
