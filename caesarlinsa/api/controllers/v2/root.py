import pecan
from pecan import rest

from caesarlinsa.api.controllers.v2 import meters


class V2Controller(rest.RestController):

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind == 'meters':
            return meters.MetersController(), remainder
