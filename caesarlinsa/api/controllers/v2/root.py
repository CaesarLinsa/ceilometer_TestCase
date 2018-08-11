import pecan
from pecan import rest

from caesarlinsa.api.controllers.v2 import meters


class V2Controller(rest.RestController):

    @pecan.expose()
    def _lookup(self, kind, *remainder):
        if kind in ['meters', 'resources', 'samples']:
            if kind == 'meters' and pecan.request.method == 'POST':
                return meters.MetersController(), remainder

