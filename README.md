# python-taxcloud

TaxCloud handles every aspect of sales tax management, from collection to filing.  <http://taxcloud.net>

## Setup

.. code:: bash
    pip install -r requirements.txt


## Setup Config

.. code:: python
    taxcloud_config = TaxCloudConfig(api_login_id='your_tax_cloud_api_login_id', api_key='your_tax_cloud_api_key')

## Basic Usage

.. code:: python
    from taxcloud.address import Address
    from taxcloud.cart_item import CartItem
    from taxcloud import taxcloud_services

    cart_item = CartItem(tic=00000, item_id='item_id', price=10.00, qty=1)
    cart_items = [cart_item]
    destination = Address(address1='address1', address2='address2', city='city', state='state', zip_code='zip_code')
    origin = Address(address1='address1', address2='address2', city='city', state='state', zip_code='zip_code')

    lookup = taxcloud_services.Lookup(config=taxcloud_config,
                                      customer_id='customer_id',
                                      cart_items=cart_items,
                                      destination=destination,
                                      origin=origin)
    lookup.request()
    lookup.tax

    auth_capture = taxcloud_services.AuthorizedWithCapture(config=self.taxcloud_config,
                                                           customer_id='customer_id',
                                                           cart_id='cart_id',
                                                           order_id='order_id')
    auth_capture.request()


## Running Tests

.. code:: bash
    inv tests