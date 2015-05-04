from utils import xstr
import curator.api as api


def build_filter_list(opts):
    """
    Build filter list from action configuration parameters.
    """
    filter_list = []
    # Add timebased filtering
    timebased = zip(('newer_than', 'older_than'), (opts.newer_than,
                                                   opts.older_than))
    for opt, value in timebased:
        if value is None: continue
        f = api.filter.build_filter(kindOf=opt, value=value, timestring=opts.timestring,
                                    time_unit=opts.time_unit)
        if f: filter_list.append(f)

    # Timestring alone filtering
    if opts.timestring is not None and not all(( xstr(opts.newer_than), 
                                                 xstr(opts.older_than) )):
        f = api.filter.build_filter(kindOf='timestring', value=opts.timestring)
        if f: filter_list.append(f)

    # Add filtering based on suffix|prefix|regex
    patternbased = zip(('suffix', 'prefix', 'regex'),
                       (opts.suffix, opts.prefix, opts.regex))

    for opt, value in patternbased:
        if value is None: continue
        f = api.filter.build_filter(kindOf=opt, value=value)
        if f: filter_list.append(f)

    return filter_list


def filter_timerange(filter_list, working_list, opts):
    """
    Checks if time range is specified and filters by newer_than and older_than
    separatly and intersects both ranges.
    Result is a tuple containing new filter and working lists.

    If no time range is specified returns None otherwise returns the new working
    list.

    :rtype: NoneType or tuple
    """
    # Handle simultaneous time filters, they can work together.
    if opts.newer_than and opts.older_than:
        if opts.newer_than < opts.older_than:
            print 'ERROR: Wrong time period newer_than must be > older_than.'
            sys.exit(1)

        timebased = {}
        for f in [i for i in filter_list]:
            # Filter list is duplicated since we mangle it.
            if f['method'] in ['older_than', 'newer_than']:
                timebased[f['method']] = f
                filter_list.remove(f)
                if len(timebased) == 2: break

        newer = set(apply_filter(working_list, **timebased['newer_than']))
        older = set(apply_filter(working_list, **timebased['older_than']))

        # new filter list and intersection of new_than and older_than ranges
        return (filter_list, list(newer & older))
