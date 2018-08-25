# Copyright 2012-2014 eNovance <licensing@enovance.com>
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

import sys
from oslo_config import cfg
from oslo_log import log


def prepare_service(argv=None, config_file=None, conf=None):
    if argv is None:
        argv = sys.argv

    if conf is None:
        log.register_options(cfg.CONF)
        conf = cfg.ConfigOpts()

    log_level = cfg.CONF.default_log_levels
    log.set_defaults(default_log_levels=log_level)
    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='caesar', default_config_files=config_file)
    log.setup(cfg.CONF, 'caesar')
    return conf
