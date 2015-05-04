from easydict import EasyDict
from lib.curator_action import CuratorAction
from lib.api_wrapper import APIWrapper
import logging

import sys
import yaml

logger = logging.getLogger(__name__)


class CuratorRunner(CuratorAction):

    def run(self, **kwargs):
        self.action = kwargs.pop('action')
        self.config = EasyDict(kwargs)
        self.api = APIWrapper(**self.config)

        self.set_up_logging()
        self.override_timeout()
        self.do_command()
