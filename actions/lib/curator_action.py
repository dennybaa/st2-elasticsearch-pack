from st2actions.runners.pythonrunner import Action
from curator.api.utils import index_closed
from utils import xstr
import utils
import logging
import sys
import itertools

logger = logging.getLogger(__name__)


class CuratorAction(Action):

    def __init__(self, config=None):
        super(CuratorAction, self).__init__(config=config)
        self.success = True
        self._act_on = None
        self._command = None


    @property
    def act_on(self):
        if not self._act_on:
            _act_on = 'snapshots' if '.snapshots' in self.action else 'indices'
            self._act_on = _act_on
        return self._act_on

    @property
    def command(self):
        if not self._command:
            self._command = self.action.split('.')[0]
        return self._command


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

        if self.command in ('snapshot', 'optimize') and self.config.timeout < 21600:
            logger.warn('Raising timeout because {0} operation might take time!'.
                            format(self.command))
            self.config.timeout = 21600


    def show_dry_run(self, items):
        """
        Log dry run output with the command which would have been executed.
        """
        client = self.api.client
        command = self.command
        print "DRY RUN MODE.  No changes will be made."
        for item in items:
            if self.act_on == 'snapshots':
                print "DRY RUN: {0}: {1}".format(command, item)
            else:
                print "DRY RUN: {0}: {1}{2}".format(command, item, ' (CLOSED)' if index_closed(client, item) else '')


    def do_show(self):
        """
        Show indices or snapshots command.
        """
        items = self.api.fetch(act_on=self.act_on)
        if not self.config.dry_run:
            for item in items:
                print item
        else:
            self.show_dry_run(items)
        sys.exit(0)


    def exit_msg(self, success):
        """
        Display a message corresponding to whether the job completed successfully or
        not, then exit.
        """
        if success:
            logger.info("Job completed successfully.")
        else:
            logger.warn("Job did not complete successfully.")
        sys.exit(0) if success else sys.exit(1)


    def do_command(self):
        """
        Do the command.
        """
        opts = self.config
        if self.command == "show":
            self.do_show()

        # I don't care about using only timestring if it's a `dry_run` of show
        if not any((xstr(opts.newer_than), xstr(opts.older_than), opts.dry_run)) and \
                opts.timestring:
            logger.warn('Used only timestring parameter.')
            logger.warn('Actions can be performed on all indices matching {0}'.format(opts.timestring))

        if opts.dry_run:
            items = self.api.fetch(act_on=self.act_on)
            self.show_dry_run(items)
        else:
            logger.info("Job starting: {0} {1}".format(self.command, self.act_on))
            logger.debug("Params: {0}".format(opts))

            success = self.api.invoke(method=self.action)
            self.exit_msg(success)
