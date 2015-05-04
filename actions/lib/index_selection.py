from curator.api.utils import *
from curator.api.filter import *
from filter_utils import *
from utils import get_client
import sys
import logging

logger = logging.getLogger(__name__)

def indices(client, opts):
    """
    Get a list of indices to act on from the provided arguments.
    """
    filter_list = build_filter_list(opts)

    # Check if we have selection to operate
    if not any((opts.all_indices, opts.index, filter_list)):
        print 'Error: At least one index filter parameter must be provided!'
        sys.exit(1)

    # Get a master-list of indices
    indices = get_indices(client)
    logger.debug("Full list of indices: {0}".format(indices))

    if opts.index and not filter_list:
        working_list = []
    else:
        if indices:
            working_list = indices
        else:
            print 'ERROR. No indices found in Elasticsearch.'
            sys.exit(1)

    if opts.all_indices:
        working_list = indices
        logger.info('Matching all indices. Ignoring parameters other than exclude.')

    logger.debug('All filters: {0}'.format(filter_list))

    # Handle simultaneous time filters, they can work together.
    result = filter_timerange(filter_list, working_list, opts)
    if result is not None:
        filter_list, working_list = result

    # Apply filters one by one from the list.
    for f in filter_list:
        if opts.all_indices and not 'exclude' in f:
            continue
        working_list = apply_filter(working_list, **f)

    if opts.command == "delete": # Protect against accidental delete
        logger.info("Pruning Kibana-related indices to prevent accidental deletion.")
        working_list = prune_kibana(working_list)

    # If there are manually added indices, we will add them here
    manually_set_indexes = (opts.index or '').split(',')
    working_list.extend((i for i in manually_set_indexes if i in indices))

    if working_list and opts.command == 'delete':
        # If filter by disk space, filter the working_list by space:
        if opts.disk_space:
            working_list = filter_by_space(
                                client, working_list,
                                disk_space=opts.disk_space,
                                reverse=opts.reverse
                           )

    if not working_list:
        print 'No indices matched provided args: {0}'.format(opts)
        sys.exit(99)

    # Make a sorted, unique list of indices
    working_list = sorted(list(set(working_list)))

    return working_list
