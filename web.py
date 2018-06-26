import urlparse
import glob
import os
import sys
import time
import json
from bs4 import BeautifulSoup

from steam.guard import SteamAuthenticator
import steam.webauth as wa

def get_all_config_files(configs_dir):
    if configs_dir is not None and os.path.exists(configs_dir):
        configs = glob.glob("{0}/*.json".format(configs_dir))
    else:
        configs = []

    return configs


def get_form_info(form, url):
    ret = {}
    fields = form.findAll('input')
    posturl = urlparse.urljoin(url, form['action'])
    formdata = dict((field.get('name'), field.get('value')) for field in fields)
    ret['url'] = posturl
    ret['data'] = formdata
    return ret


def process_forms(dom, url):
    form = dom.find(id="next_in_queue_form")
    if form:
        form_info = get_form_info(form, url)

        post_response = session.post(form_info['url'], data=form_info['data'])

        file = open("./out.html", "w")
        file.write(post_response.text.encode('utf-8'))
        file.close()

        response_dom = BeautifulSoup(post_response.text, 'html.parser')
        span_elements = response_dom.find_all('span')
        for span_element in span_elements:
            if 'class' in span_element.attrs and 'queue_sub_text' in span_element['class']:
                print(span_element.contents)
                break

        return process_forms(response_dom, url)
    else:
        div_elements = dom.find_all('div')
        for div_element in div_elements:
            if 'class' in div_element.attrs and 'subtext' in div_element['class']:
                if "tomorrow" not in str(div_element):
                    print(div_element.contents)
                    return False
        return True


def start_queue(session, url = None, trys = 0):
    max_tries = 5
    if url is None:
        url = 'https://store.steampowered.com/explore/startnew'
    response = session.get(url)

    if response.status_code is 200:
        base_dom = BeautifulSoup(response.text, 'html.parser')
        if not process_forms(base_dom, url):
            return start_queue(session)
        else:
            return True
    else:
        if trys < max_tries:
            trys += 1
            print("Bad response code: {0}".format(response.status_code))
            return start_queue(session, url, trys)
        else:
            print("Failed to load page {0} too many times ({1})".format(url, max_tries))
            return False


def get_game(session):
    planet_to_join = None
    zone_to_join = None
    url = "https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanets/v0001/?active_only=0&language=english"
    response = session.get(url)
    planets = json.loads(response.text)
    for planet in planets['response']['planets']:
        if planet['state']['active']:
            planet_to_join = planet['id']

    join_url = "https://community.steam-api.com/ITerritoryControlMinigameService/JoinPlanet/v0001/"
    join_data = {'id': planet['id'], 'access_token': 'e4190c66f398f165dfb30b284cef5242'}
    post_response = session.post(join_url, data=join_data)
    get_planet_url = "https://community.steam-api.com/ITerritoryControlMinigameService/GetPlanet/v0001/?id={0}&language=english".format(
        planet_to_join)
    planet_response = session.get(get_planet_url)
    planet_contents = json.loads(planet_response.text)
    for zone in planet_contents['response']['planets'][0]['zones']:
        if not zone['captured']:
            zone_to_join = zone['zone_position']

    print("Joining planet: {0}".format(planet_to_join))
    print("\tJoining zone: {0}".format(zone_to_join))
    join_zone_url = "https://community.steam-api.com/ITerritoryControlMinigameService/JoinZone/v0001/"
    join_zone_data = {'zone_position': zone_to_join, 'access_token': 'e4190c66f398f165dfb30b284cef5242'}
    join_zone_response = session.post(join_zone_url, data=join_zone_data)
    print(join_zone_response.text)


def login(user, previous_code=None):
    wait = 10
    sa = SteamAuthenticator(secret)
    code = sa.get_code()
    session = None
    if previous_code is None or previous_code != code:
        try:
            session = user.login(twofactor_code=code)
            print("Successful login with 2fa code")
        except wa.TwoFactorCodeRequired:
            return login(user, code)
    else:
        print("2fa code failed; waiting {0} seconds and trying again".format(wait))
        time.sleep(wait)
        return login(user, code)

    return session

api_key = "EB216E998E51A53208F84E96015A0605"

url = 'https://store.steampowered.com/explore/startnew'
username = "jacobtruman"

configs_dir = "./configs"

config_files = get_all_config_files(configs_dir)

base_config = {}
base_config_file = '{0}/config.json'.format(configs_dir)

user = None
for config_file in config_files:
    # exclude base config (config.json)
    if config_file != base_config_file:
        try:
            config = json.loads(open(config_file, "r").read())
            if config['username'] == username:
                user = wa.WebAuth(config['username'], config['password'])
                #print(config)
                secret = config['steam_guard']
        except ValueError, e:
            print(e.message)
            pass

if user is not None:
    session = login(user)

    if session is not None:

        # TODO: test this
        get_game(session)

        if start_queue(session, url):
            print("Successfully processed queue")
        else:
            print("Failed to process queue")
    else:
        print("Unable to login...")
