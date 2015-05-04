from curator.api.utils import *
from curator.api.filter import *
from items_filter import ItemsFilter
from easydict import EasyDict
from utils import get_client, compact_dict
import sys
import logging

logger = logging.getLogger(__name__)


class ItemsSelector(object):

    def __init__(self, client, **opts):
        self.opts = EasyDict(opts)
        self.client  = client
        self.ifilter = ItemsFilter().build(**opts)


    def _apply_filters(self, source_items, act_on):
        """Applies filters to a list of indices or snapshots.
        :param source_items:   List of indices or snapshots.
        :param act_on:  Specifies whether we act on indices or snapshots.
        """
        logger.debug("Full list of {0}: {1}".format(act_on, source_items))
        opts = self.opts
        
        if not source_items:
            print 'ERROR. No {0} found in Elasticsearch.'.format(act_on)
            sys.exit(1)
        else:
            working_list = source_items

        # Apply filters to the working list
        working_list = self.ifilter.apply(working_list, act_on=act_on)

        # Handle items added via index or snapshot parameter.
        mkey = 'index' if act_on == 'indices' else 'snapshot'
        manual_items = (opts.get(mkey, None) or '').split(',')
        if manual_items:
            working_list.extend((i for i in manual_items if i in source_items))

        if not working_list:
            print 'No {0} matched provided args: {1}'.format(act_on, opts)
            sys.exit(99)

        # Make a sorted, unique list of indices/snapshots
        return sorted(list(set(working_list)))


    def snapshots(self):
        """
        Get a list of snapshots to act on from the provided arguments.
        """
        if not self.opts.repository:
            print 'Missing required parameter: repository.'
            sys.exit(1)

        # Get a master-list of snapshots
        snapshots = get_snapshots(self.client, repository=opts.repository)
        return self._apply_filters(snapshots, act_on='snapshots')


    def indices(self):
        """
        Get a list of indices to act on from the provided arguments.
        """
        # Check if we have selection to operate
        if not any((self.opts.all_indices, self.opts.index, self.ifilter.filter_list)):
            print 'Error: At least one index filter parameter must be provided!'
            sys.exit(1)

        # Get a master-list of indices
        indices = get_indices(self.client)
        return self._apply_filters(indices, act_on='indices')


    def fetch(self, act_on):
        if act_on not in ['indices', 'snapshots']:
            raise ValueError('invalid argument: {0}'.format(act_on))

        if act_on == 'indices':
            return self.indices()
        else:
            return self.snapshots()
