class TaxCloudConfig(object):
    """
    Required TaxCloud api ID/Key to access their SOAP API
    """

    def __init__(self,
                 api_login_id,
                 api_key,
                 wsdl_version='1.0',
                 wsdl_path='wsdl/taxcloud_1.0.wsdl'):
        self._api_login_id = api_login_id
        self._api_key = api_key
        self._wsdl_version = wsdl_version
        self._wsdl_path = wsdl_path

    @property
    def api_login_id(self):
        return self._api_login_id

    @property
    def api_key(self):
        return self._api_key

    @property
    def wsdl_version(self):
        return self._wsdl_version

    @property
    def wsdl_path(self):
        return self._wsdl_path
