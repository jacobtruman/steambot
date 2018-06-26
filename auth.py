from steam.guard import SteamAuthenticator

secret = {}

sa = SteamAuthenticator(secret)
code = sa.get_code()
print(code)
