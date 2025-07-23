#!/usr/bin/env python

import sys
import os
import json
from steam.guard import SteamAuthenticator

if len(sys.argv) > 1:
    username = sys.argv[1]

    config_file = f"{os.path.dirname(os.path.realpath(sys.argv[0]))}/configs/{username}.json"

    if os.path.exists(config_file):
        try:
            config = json.loads(open(config_file, "r").read())
            if username is None or config['username'] == username:
                sa = SteamAuthenticator(config['steam_guard'])
                code = sa.get_code()
                print(code)
        except ValueError as e:
            print(e)
            pass
    else:
        print("No config for username: {0}".format(username))
else:
    print("Please provide username")
