class Address(object):
    def __init__(self,
                 address1,
                 city,
                 state,
                 zip_code,
                 address2=''):
        self._address1 = address1
        self._city = city
        self._state = state
        self._zip_code = zip_code
        self._address2 = address2

    @property
    def address1(self):
        return self._address1

    @property
    def address2(self):
        return self._address2

    @property
    def city(self):
        return self._city

    @property
    def state(self):
        return self._state

    @property
    def zip_code(self):
        return self._zip_code
