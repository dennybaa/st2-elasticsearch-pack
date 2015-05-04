from st2actions.runners.pythonrunner import Action
from utils import compact_dict, xstr
import utils
import index_selection
import snapshot_selection
import curator.api as api
import logging
import sys
import itertools

logger = logging.getLogger(__name__)


class CuratorAction(Action):
    CMD2API = {
        'snapshot': 'create_snapshot',
        'open': 'opener'
    }

    def __init__(self, config=None):
        super(CuratorAction, self).__init__(config=config)
        self.success = True
        self._operate_on = None


    @property
    def operate_on(self):
        if not self._operate_on:
            self._operate_on = self.config.command_on or 'indices'
        return self._operate_on


    def fetch_items(self):
        """
        Retrieve items invokes propper method returning its results:
        indices or snapshots.
        """
        if self.operate_on == 'snapshots':
            return snapshot_selection.snapshots(self.client, self.config)
        else:
            return index_selection.indices(self.client, self.config)


    def set_up_logging(self):
        """
        Set log_level. Default is to display warnings.
        """
        log_level = self.config.log_level or 'warn'
        numeric_log_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_log_level, int):
            raise ValueError('Invalid log level: {0}'.format(log_level))
        logging.basicConfig(level=numeric_log_level)


    def override_timeout(self):
        """
        Overides default timeout for long lasting operations. Sets it to 6 hours.
        """
        # TOFIX: default runner options if overried are NOT passed to the script.
        #
        # !!!!
        self.config.timeout = 600

        if self.config.command in ('snapshot', 'optimize') and self.config.timeout < 21600:
            logger.warn('Raising timeout because {0} operation might take time!'.
                            format(self.config.command))
            self.config.timeout = 21600


    def show_dry_run(self, items):
        """
        Log dry run output with the command which would have been executed.
        """
        client = self.client
        command = self.config.command
        print "DRY RUN MODE.  No changes will be made."
        for item in items:
            if self.operate_on == 'snapshots':
                print "DRY RUN: {0}: {1}".format(command, item)
            else:
                print "DRY RUN: {0}: {1}{2}".format(command, item, ' (CLOSED)' if api.index_closed(client, item) else '')



    def do_show(self):
        """
        Show indices or snapshots command.
        """
        items = self.fetch_items()
        if not self.config.dry_run:
            logger.info('Matching {0}:'.format(self.operate_on))
            for item in items:
                print item
        else:
            self.show_dry_run(items)

        sys.exit(0)


    def chunked_item_lists(self):
        """
        Iterate over whole list of indices in chunks.
        In case operation is performed on snapshots the won't be chunked.
        """
        working_list = self.fetch_items()
        # The snapshot command should get the full list,
        # but the index list may need to be segmented.
        if len(api.utils.to_csv(working_list)) > 3072 and \
                                self.operate_on == 'indices':

            logger.warn('Very large list of indices.  Breaking it up into smaller chunks.')
            index_lists = utils.chunk_index_list(working_list)
            for l in index_lists:
                yield l
        else:
            yield working_list


    def _api_call_kwargs(self):
        opts = self.config
        command = opts.command
        if command == "alias":
            kwargs = {'alias': opts.name, 'remove': opts.remove}
        elif command == 'allocation':
            kwargs = {'rule': opts.rule}
        elif command == 'bloom':
            kwargs = {'delay': opts.delay}
        elif command == 'optimize':
            kwargs = {'max_num_segments': opts.max_num_segments,
                      'request_timeout': opts.request_timeout,
                      'delay': opts.delay}
        elif command == 'replicas':
            kwargs = {'replicas': opts.count}
        elif command == 'snapshot':
            kwargs = {'name': opts.name, 'prefix': opts.snapshot_prefix, 
                      'repository': opts.repository, 'partial': opts.partial,
                      'ignore_unavailable': opts.ignore_unavailable,
                      'include_global_state': opts.include_global_state,
                      'wait_for_completion': opts.wait_for_completion,
                      'request_timeout': opts.request_timeout}
        else:
            kwargs = {}
        # Compact all those values with none and return
        return compact_dict(kwargs)


    def _api_call(self, items):
        """
        Invoke curator API method.
        """
        opts = self.config
        command = opts.command
        client = self.client
        kwargs = self._api_call_kwargs()
        if command in [ 'alias', 'allocation', 'bloom', 'close', 'open' 
                        'optimize', 'replicas', 'snapshot' ]:
            func_name = self.CMD2API.get(command, command)
            api_method = api.__dict__.get(func_name, None)
            if not api_method:
                print 'Error: unsupported api method called: {0}'.format(command)
                sys.exit(1)

            # Call api method with/without parameters
            if kwargs:
                return api_method(client, items, **kwargs)
            else:
                return api_method(client, items)

            # Also need:
            # 1. delete and delete_snapshot(client, snapshot=items, repository=opts.repository)

    def exit_msg(self):
        """
        Display a message corresponding to whether the job completed successfully or
        not, then exit.
        """
        if self.success:
            logger.info("Job completed successfully.")
        else:
            logger.warn("Job did not complete successfully.")
        sys.exit(0) if self.success else sys.exit(1)


    def do_command(self):
        """
        Do the command.
        """
        opts = self.config

        if opts.command == "show":
            # do_show will exit
            self.do_show()

        # I don't care about using only timestring if it's a `dry_run` of show
        if not any((xstr(opts.newer_than), xstr(opts.older_than), opts.dry_run)) and \
                opts.timestring:
            logger.warn('Used only timestring parameter.')
            logger.warn('Actions can be performed on all indices matching {0}'.format(opts.timestring))

        if opts.dry_run:
            items = self.fetch_items()
            self.show_dry_run(items)
        else:
            logger.info("Job starting: {0} {1}".format(opts.command, self.operate_on))
            logger.debug("Params: {0}".format(opts))

            # Make two generators since we want show all items when debug is on.
            chunked_list, working_list = itertools.tee(self.chunked_item_lists())
            working_list = list(itertools.chain(*working_list))
            logger.debug('ACTION {0} {1} will be executed against: {2}'.format(opts.command,
                                                            self.operate_on, working_list))

            for items in chunked_list:
                result = self._api_call(items)
                if not result:
                    self.success = False

            self.exit_msg()
