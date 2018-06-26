from steam import SteamClient
from steam.enums.emsg import EMsg
from steam.guard import SteamAuthenticator

sa = SteamAuthenticator(secret)
code = sa.get_code()

client = SteamClient()

@client.on(EMsg.ClientVACBanStatus)
def print_vac_status(msg):
    print("Number of VAC Bans: %s" % msg.body.numBans)

#client.cli_login()
print(ret)
if ret is not 1:
    print("Logged on as: %s" % client.user.name)
    print("Community profile: %s" % client.steam_id.community_url)
    print("Last logon: %s" % client.user.last_logon)
    print("Last logoff: %s" % client.user.last_logoff)
    print("Number of friends: %d" % len(client.friends))

    client.logout()
