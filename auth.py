import sys
import os
import json
from steam.guard import SteamAuthenticator

if len(sys.argv) > 1:
    username = sys.argv[1]

    config_dir = "./configs"
    config_file = "{0}/{1}.json".format(config_dir, username)

    if os.path.exists(config_file):
        try:
            config = json.loads(open(config_file, "r").read())
            if username is None or config['username'] == username:
                sa = SteamAuthenticator(config['steam_guard'])
                code = sa.get_code()
                print(code)
        except ValueError, e:
            print(e.message)
            pass
    else:
        print("No config for username: {0}".format(username))
else:
    print("Please provide username")
