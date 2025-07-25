#!/usr/bin/env python

import argparse
import sys
import glob
import os
import json
import atexit
import steambot


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Run Steambot.',
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='Enable verbose logging',
    )

    parser.add_argument(
        '-u', '--username',
        dest='username',
        help='Steam Username',
    )

    parser.add_argument(
        '-c', '--configs_dir',
        default=None,
        dest='configs_dir',
        help='Directory containing the config files',
    )

    args = parser.parse_args()
    return args


def get_all_config_files(configs_dir):
    if configs_dir is not None and os.path.exists(configs_dir):
        configs = glob.glob(f"{configs_dir}/*.json")
    else:
        configs = []

    return configs


def fail(msg):
    print(f"FAILURE: {msg}")
    sys.exit(0)


def cleanup(args):
    if 'lock_file' in args:
        os.remove(args['lock_file'])
        msg = f"Lock file removed: {args['lock_file']}"
        if 'logger' in args:
            args['logger'].info(msg)
        else:
            print(msg)


def main():
    """
    Main function.
    """
    args = parse_args()

    bot_args = {}

    if args.username is not None:
        bot_args['username'] = args.username.lower()

        home_dir = os.path.expanduser("~")

        if args.configs_dir is not None:
            configs_dir = args.configs_dir
        else:
            configs_dir = '~/steam_configs'

        if configs_dir[:1] == '~':
            configs_dir = configs_dir.replace('~', home_dir)

        if not os.path.exists(configs_dir):
            fail(f"Configs directory provided does not exist: {configs_dir}")

        bot_args['configs_dir'] = configs_dir

        base_config = {}
        base_config_file = f"{configs_dir}/config.json"
        if os.path.exists(base_config_file):
            try:
                base_config = json.loads(open(base_config_file, "r").read())
            except ValueError as e:
                fail(e)

        bot_args['base_config'] = base_config

        if 'log_dir' in base_config:
            log_dir = base_config['log_dir']
            if log_dir[:1] == '~':
                log_dir = log_dir.replace('~', home_dir)
            bot_args['log_dir'] = log_dir

        bot_args['verbose'] = args.verbose

        bot = steambot.SteamBot(bot_args)
        bot.logger.debug("Bot initialized")

        # check if process is already running
        lock_file = f"/tmp/steambot_{bot_args['username']}.lock"
        if os.path.exists(lock_file):
            fail(f"Lock file exists: {lock_file}")
        else:
            atexit.register(cleanup, args={'lock_file': lock_file, 'logger': bot.logger})
            open(lock_file, 'w+')
            bot.logger.info(f"Lock acquired: {lock_file}")

        bot.logger.debug("About to get summary")

        bot.summary()
        bot.check_trade_requests()
    else:
        fail('Username parameter (-u) not specified')


if __name__ == '__main__':
    main()
