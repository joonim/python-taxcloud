class CartItem(object):
    def __init__(self, tic, item_id, price, qty):
        self._tic = tic
        self._item_id = item_id
        self._price = price
        self._qty = qty

    @property
    def tic(self):
        return self._tic

    @property
    def item_id(self):
        return self._item_id

    @property
    def price(self):
        return self._price

    @property
    def qty(self):
        return self._qty
