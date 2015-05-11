from easydict import EasyDict
from lib.items_selector import ItemsSelector
from lib.elastic_action import ElasticAction
from collections import defaultdict
import logging
import sys
import elasticsearch
import json

logger = logging.getLogger(__name__)


class SearchRunner(ElasticAction):

    def __init__(self, config=None):
        super(SearchRunner, self).__init__(config=config)
        self._iselector = None


    @property
    def iselector(self):
        """
        Used to fetch indices/snapshots and apply filter to them.
        """
        if not self._iselector:
            self._iselector = ItemsSelector(self.client, **self.config)
        return self._iselector


    def run(self, **kwargs):
        action = kwargs.pop('action')
        self.config = EasyDict(kwargs)
        # support full interface for curator iselector
        self.config['dry_run'] = False
        self.set_up_logging()

        if action.endswith('.q'):
            self.simple_search()
        else:
            self.full_search()


    def simple_search(self):
        """Perform URI-based request search.
        """
        accepted_params = ('q','df', 'default_operator', 'from', 'size')
        # FIX TIMEOUT, can get it since it's built in for st2 actions
        kwargs = {k:self.config[k] for k in accepted_params if self.config[k]}
        indices = ','.join(self.iselector.indices())

        try:
            result = self.client.search(index=indices, **kwargs)
        except elasticsearch.ElasticsearchException as e:
            logger.error(e.message)
            sys.exit(99)

        self._pp_exit(result)


    def full_search(self):
        """Perform search using Query DSL.
        """
        accepted_params = ('from', 'size')
        # FIX TIMEOUT, can get it since it's built in for st2 actions
        kwargs = {k:self.config[k] for k in accepted_params if self.config[k]}
        try:
            result = self.client.search(index=self.config.indices, 
                                        body=self.config.body, **kwargs)
        except elasticsearch.ElasticsearchException as e:
            logger.error(e.message)
            sys.exit(99)

        self._pp_exit(result)


    def _pp_exit(self, data):
        """Print Elastcsearch JSON response and exit.
        """
        kwargs = {}
        if self.config.pretty:
            kwargs = {'indent': 4}
        print json.dumps(data, **kwargs)

        if data['hits']['total'] > 0:
            sys.exit(0)
        else:
            sys.exit(1)
