from curator.api.utils import *
from curator.api.filter import *
from filter_utils import *
from utils import get_client
import sys
import logging

logger = logging.getLogger(__name__)


def snapshots(client, opts):
    """
    Get a list of snapshots to act on from the provided arguments.
    """
    if not opts.repository:
        print 'Missing required parameter: repository.'
        sys.exit(1)

    filter_list = build_filter_list(opts)

    # Get a master-list of snapshots
    snapshots = get_snapshots(client, repository=opts.repository)
    if snapshots:
        working_list = snapshots
    else:
        print 'ERROR. No snapshots found in Elasticsearch.'
        sys.exit(1)

    if opts.all_snapshots:
        logger.info('Matching all snapshots. Ignoring flags other than exclude.')
    else:
        logger.debug('All filters: {0}'.format(filter_list))

    # Handle simultaneous time filters, they can work together.
    result = filter_timerange(filter_list, working_list, opts)
    if result is not None:
        filter_list, working_list = result

    # Apply filters one by one from the list.
    for f in filter_list:
        if opts.all_snapshots and not 'exclude' in f:
            continue
        working_list = apply_filter(working_list, **f)

    # If there are manually added snapshots, we will add them here
    manually_set_snapshots = (opts.snapshot or '').split(',')
    working_list.extend((i for i in manually_set_snapshots if i in snapshots))

    if not working_list:
        print 'No snapshots matched provided args: {0}'.format(opts)
        sys.exit(99)

    working_list = sorted(list(set(working_list)))
    return working_list
