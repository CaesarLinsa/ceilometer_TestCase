#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from oslo_config import cfg
from oslo_log import log

from pecan import hooks
from caesarlinsa import storage
LOG = log.getLogger(__name__)


class ConfigHook(hooks.PecanHook):
    """Attach the configuration object to the request.

    That allows controllers to get it.
    """

    @staticmethod
    def before(state):
        state.request.cfg = cfg.CONF


class DBHook(hooks.PecanHook):

    def __init__(self):
        self.storage_connection = DBHook.get_connection('metering')
        self.event_storage_connection = DBHook.get_connection('event')
        self.alarm_storage_connection = DBHook.get_connection('alarm')

        if (not self.storage_connection and
                not self.event_storage_connection and
                not self.alarm_storage_connection):
            raise Exception("Api failed to start. Failed to connect to "
                            "databases, purpose:  %s" %
                            ', '.join(['metering', 'event', 'alarm']))

    def before(self, state):
        state.request.storage_conn = self.storage_connection
        state.request.event_storage_conn = self.event_storage_connection
        state.request.alarm_storage_conn = self.alarm_storage_connection

    @staticmethod
    def get_connection(purpose):
        try:
            return storage.get_connection_from_config(cfg.CONF, purpose)
        except Exception as err:
            params = {"purpose": purpose, "err": err}
            LOG.exception("Failed to connect to db, purpose %s" % params)


class TranslationHook(hooks.PecanHook):

    def after(self, state):
        # After a request has been done, we need to see if
        # ClientSideError has added an error onto the response.
        # If it has we need to get it info the thread-safe WSGI
        # environ to be used by the ParsableErrorMiddleware.
        if hasattr(state.response, 'translatable_error'):
            state.request.environ['translatable_error'] = (
                state.response.translatable_error)