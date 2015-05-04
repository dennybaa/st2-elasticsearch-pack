from easydict import EasyDict
from lib.curator_action import CuratorAction
from lib.index_selection import *
import lib.utils as utils
import logging

import sys
import yaml

logger = logging.getLogger(__name__)


class CuratorRunner(CuratorAction):

    def run(self, **kwargs):
        parts = kwargs.pop('action').split('.')
        kwargs['command'] = parts[0]
        kwargs['command_on'] = parts[1:][0] if parts[1:] else parts[0]
        self.config = EasyDict(kwargs)
        self.client = utils.get_client(**kwargs)

        self.set_up_logging()
        self.override_timeout()
        self.do_command()
