import os
import sys
import json
import datetime
import trulogger

from time import sleep

from steam.client import SteamClient
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
            logger_config['log_file'] = f"{self.log_dir}/SteamBot_{self.username}_{date}.log"
        self.logger = trulogger.TruLogger(logger_config)

        if self.username is not None:
            config_file = f"{self.configs_dir}/{self.username}.json"
            if os.path.exists(config_file):
                self.config = json.loads(open(config_file, "r").read())
                if 'password' not in self.config:
                    self.logger.error("password not defined in config")
                    sys.exit(1)

                if 'steam_guard' not in self.config:
                    self.logger.error("steam_guard not defined in config")
                    sys.exit(1)

                self.logger.info(f"Logging in as user {self.username}...")
                self.sa = SteamAuthenticator(self.config['steam_guard'])
                self.login()
                self.logger.success(f"Logged in as user {self.username}")
            else:
                self.logger.warning(f"Config file for user provided does not exist: {config_file}")
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
                f"Steam Guard code failed; waiting {self.steam_guard_code_wait} seconds and trying again"
            )
            sleep(self.steam_guard_code_wait)
            self.login(code)

    def summary(self):
        self.logger.debug("Getting summary")

        @self.client.on(EMsg.ClientVACBanStatus)
        def print_vac_status(msg):
            self.logger.info("Number of VAC Bans: %s" % msg.body.numBans)

        self.logger.info(f"Logged on as: {self.client.user.name}")
        self.logger.info(f"Community profile: {self.client.steam_id.community_url}")
        self.logger.info(f"Last logon: {self.client.user.last_logon}")
        self.logger.info(f"Last logoff: {self.client.user.last_logoff}")
        self.logger.info(f"Number of friends: {len(self.client.friends)}")

        self.client.logout()

    def check_trade_requests(self):
        """Check for incoming trade offers"""
        self.logger.debug("Checking trade requests...")
        
        try:
            # Check if client has trade manager or web session
            if hasattr(self.client, 'get_trade_offers'):
                offers = self.client.get_trade_offers()
            elif hasattr(self.client, 'steam_id'):
                # Alternative approach - check if we can access trade data through other means
                self.logger.info("Trade offers API not directly available through client")
                self.logger.info("Consider using Steam Web API or trade manager for trade functionality")
                return
            else:
                self.logger.warning("Trade functionality not available with current Steam client")
                return
                
            if offers and 'trade_offers_received' in offers:
                received_offers = offers['trade_offers_received']
                self.logger.info(f"Found {len(received_offers)} incoming trade offers")
                
                for offer in received_offers:
                    offer_id = offer['tradeofferid']
                    partner_id = offer['accountid_other']
                    state = offer['trade_offer_state']
                    
                    if state == 2:  # Active state
                        self.logger.info(f"Active trade offer {offer_id} from user {partner_id}")
                        
                        if 'items_to_give' in offer:
                            self.logger.info(f"  Items to give: {len(offer['items_to_give'])}")
                        if 'items_to_receive' in offer:
                            self.logger.info(f"  Items to receive: {len(offer['items_to_receive'])}")
                            
                        if 'message' in offer and offer['message']:
                            self.logger.info(f"  Message: {offer['message']}")
            else:
                self.logger.info("No trade offers found")
                
        except Exception as e:
            self.logger.error(f"Failed to check trade requests: {e}")
