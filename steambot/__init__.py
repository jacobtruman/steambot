import os
import sys
import json
import datetime
import trulogger

from time import sleep

from steam import SteamClient
from steam.enums.emsg import EMsg
from steam.guard import SteamAuthenticator


class SteamBot(object):

    def __init__(self, args):
        """
        :param args:
        """
        if 'base_config' not in args:
            raise ValueError('base_config not provided')

        self.configs_dir = None
        self.log_dir = None
        self.verbose = True
        self.username = None
        self.config = None
        self.steam_guard_code_wait = 10
        self.client = SteamClient()

        # override any default settings defined in params
        for arg in args:
            self.__dict__[arg] = args[arg]

        logger_config = {'colorize': True, 'verbose': self.verbose}
        if self.log_dir is not None:
            date = datetime.datetime.today().strftime('%Y-%m-%d')
            logger_config['log_file'] = '{0}/SteamBot_{1}_{2}.log'.format(self.log_dir, self.username, date)
        self.logger = trulogger.TruLogger(logger_config)

        if self.username is not None:
            config_file = "{0}/{1}.json".format(self.configs_dir, self.username)
            if os.path.exists(config_file):
                self.config = json.loads(open(config_file, "r").read())
                if 'password' not in self.config:
                    self.logger.error("password not defined in config")
                    sys.exit(1)

                if 'steam_guard' not in self.config:
                    self.logger.error("steam_guard not defined in config")
                    sys.exit(1)

                self.logger.info("Logging in as user {0}...".format(self.username))
                self.sa = SteamAuthenticator(self.config['steam_guard'])
                self.login()
                self.logger.success("Logged in as user {0}".format(self.username))
            else:
                self.logger.warning("Config file for user provided does not exist: {0}".format(config_file))
                # self.client.cli_login()
        else:
            self.logger.warning("Username not provided")
            # self.client.cli_login()

    def login(self, previous_code=None):
        code = self.sa.get_code()
        if previous_code is None or previous_code != code:
            self.logger.debug("Attempting login...")
            self.client.login(self.username, password=self.config['password'], two_factor_code=code)
        else:
            self.logger.warning(
                "Steam Guard code failed; waiting {0} seconds and trying again".format(self.steam_guard_code_wait))
            sleep(self.steam_guard_code_wait)
            self.login(code)

    def summary(self):
        self.logger.debug("Getting summary")

        @self.client.on(EMsg.ClientVACBanStatus)
        def print_vac_status(msg):
            self.logger.info("Number of VAC Bans: %s" % msg.body.numBans)

        self.logger.info("Logged on as: {0}".format(self.client.user.name))
        self.logger.info("Community profile: {0}".format(self.client.steam_id.community_url))
        self.logger.info("Last logon: {0}".format(self.client.user.last_logon))
        self.logger.info("Last logoff: {0}".format(self.client.user.last_logoff))
        self.logger.info("Number of friends: {0}".format(len(self.client.friends)))

        self.client.logout()
