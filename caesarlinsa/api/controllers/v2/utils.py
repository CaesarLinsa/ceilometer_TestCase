#
# Copyright 2012 New Dream Network, LLC (DreamHost)
# Copyright 2013 IBM Corp.
# Copyright 2013 eNovance <licensing@enovance.com>
# Copyright Ericsson AB 2013. All rights reserved
# Copyright 2014 Hewlett-Packard Company
# Copyright 2015 Huawei Technologies Co., Ltd.
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

import copy
import datetime
import inspect

from oslo_log import log
from oslo_utils import timeutils
import pecan
import six
import wsme

from caesarlinsa.api.controllers.v2 import base
from caesarlinsa.api import rbac
from caesarlinsa import utils

LOG = log.getLogger(__name__)


def enforce_limit(limit):
    """Ensure limit is defined and is valid. if not, set a default."""
    if limit is None:
        limit = 2
        LOG.info('No limit value provided, result set will be'
                 ' limited to %(limit)d.', {'limit': limit})
    if not limit or limit <= 0:
        raise base.ClientSideError("Limit must be positive")
    return limit


def get_auth_project(on_behalf_of=None):
    auth_project = rbac.get_limited_to_project(pecan.request.headers)
    created_by = pecan.request.headers.get('X-Project-Id')
    is_admin = auth_project is None

    if is_admin and on_behalf_of != created_by:
        auth_project = on_behalf_of
    return auth_project


def sanitize_query(query, db_func, on_behalf_of=None):
    """Check the query.

    See if:
    1) the request is coming from admin - then allow full visibility
    2) non-admin - make sure that the query includes the requester's project.
    """
    q = copy.copy(query)
    proj_q = [i for i in q if i.field == 'project_id']
    valid_keys = inspect.getargspec(db_func)[0]
    if not proj_q and 'on_behalf_of' not in valid_keys:
        # The user is restricted, but they didn't specify a project
        # so add it for them.
        q.append(base.Query(field='project_id',
                            op='eq'))
    return q


def _validate_timestamp_fields(query, field_name, operator_list,
                               allow_timestamps):
    """Validates the timestamp related constraints in a query if there are any.

    :param query: query expression that may contain the timestamp fields
    :param field_name: timestamp name, which should be checked (timestamp,
        search_offset)
    :param operator_list: list of operators that are supported for that
        timestamp, which was specified in the parameter field_name
    :param allow_timestamps: defines whether the timestamp-based constraint is
        applicable to this query or not

    :returns: True, if there was a timestamp constraint, containing
        a timestamp field named as defined in field_name, in the query and it
        was allowed and syntactically correct.
    :returns: False, if there wasn't timestamp constraint, containing a
        timestamp field named as defined in field_name, in the query

    :raises InvalidInput: if an operator is unsupported for a given timestamp
        field
    :raises UnknownArgument: if the timestamp constraint is not allowed in
        the query
    """

    for item in query:
        if item.field == field_name:
            # If *timestamp* or *search_offset* field was specified in the
            # query, but timestamp is not supported on that resource, on
            # which the query was invoked, then raise an exception.
            if not allow_timestamps:
                raise wsme.exc.UnknownArgument(field_name,
                                               "not valid for " +
                                               "this resource")
            if item.op not in operator_list:
                raise wsme.exc.InvalidInput('op', item.op,
                                            'unimplemented operator for %s' %
                                            item.field)
            return True
    return False


def query_to_kwargs(query, db_func, internal_keys=None,
                    allow_timestamps=True):
    query = sanitize_query(query, db_func)
    translation = {'user_id': 'user',
                   'project_id': 'project',
                   'resource_id': 'resource'}
    stamp = {}
    metaquery = {}
    kwargs = {}
    for i in query:
        if i.field == 'timestamp':
            if i.op in ('lt', 'le'):
                stamp['end_timestamp'] = i.value
                stamp['end_timestamp_op'] = i.op
            elif i.op in ('gt', 'ge'):
                stamp['start_timestamp'] = i.value
                stamp['start_timestamp_op'] = i.op
        else:
            if i.op == 'eq':
                if i.field == 'search_offset':
                    stamp['search_offset'] = i.value
                elif i.field == 'enabled':
                    kwargs[i.field] = i._get_value_as_type('boolean')
                elif i.field.startswith('metadata.'):
                    metaquery[i.field] = i._get_value_as_type()
                elif i.field.startswith('resource_metadata.'):
                    metaquery[i.field[9:]] = i._get_value_as_type()
                else:
                    key = translation.get(i.field, i.field)
                    kwargs[key] = i.value

    if metaquery and 'metaquery' in inspect.getargspec(db_func)[0]:
        kwargs['metaquery'] = metaquery
    if stamp:
        kwargs.update(_get_query_timestamps(stamp))
    return kwargs


def _get_query_timestamps(args=None):
    """Return any optional timestamp information in the request.

    Determine the desired range, if any, from the GET arguments. Set
    up the query range using the specified offset.

    [query_start ... start_timestamp ... end_timestamp ... query_end]

    Returns a dictionary containing:

    start_timestamp: First timestamp to use for query
    start_timestamp_op: First timestamp operator to use for query
    end_timestamp: Final timestamp to use for query
    end_timestamp_op: Final timestamp operator to use for query
    """

    if args is None:
        return {}
    search_offset = int(args.get('search_offset', 0))

    def _parse_timestamp(timestamp):
        if not timestamp:
            return None
        try:
            iso_timestamp = timeutils.parse_isotime(timestamp)
            iso_timestamp = iso_timestamp.replace(tzinfo=None)
        except ValueError:
            raise wsme.exc.InvalidInput('timestamp', timestamp,
                                        'invalid timestamp format')
        return iso_timestamp

    start_timestamp = _parse_timestamp(args.get('start_timestamp'))
    end_timestamp = _parse_timestamp(args.get('end_timestamp'))
    start_timestamp = start_timestamp - datetime.timedelta(
        minutes=search_offset) if start_timestamp else None
    end_timestamp = end_timestamp + datetime.timedelta(
        minutes=search_offset) if end_timestamp else None
    return {'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp,
            'start_timestamp_op': args.get('start_timestamp_op'),
            'end_timestamp_op': args.get('end_timestamp_op')}


def flatten_metadata(metadata):
    """Return flattened resource metadata.

    Metadata is returned with flattened nested structures (except nested sets)
    and with all values converted to unicode strings.
    """
    if metadata:
        # After changing recursive_keypairs` output we need to keep
        # flattening output unchanged.
        # Example: recursive_keypairs({'a': {'b':{'c':'d'}}}, '.')
        # output before: a.b:c=d
        # output now: a.b.c=d
        # So to keep the first variant just replace all dots except the first
        return dict((k.replace('.', ':').replace(':', '.', 1),
                     six.text_type(v))
                    for k, v in utils.recursive_keypairs(metadata,
                                                         separator='.')
                    if type(v) is not set)
    return {}
