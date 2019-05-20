#!/usr/bin/env python

import urlparse
import glob
import os
import sys
from time import sleep
import json
from bs4 import BeautifulSoup

from steam.guard import SteamAuthenticator
import steam.webauth as wa

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = None


def get_all_config_files(configs_directory):
    if configs_directory is not None and os.path.exists(configs_directory):
        configs = glob.glob("{0}/*.json".format(configs_directory))
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


def process_forms(session, dom, url):
    form = dom.find(id="next_in_queue_form")
    if form:
        form_info = get_form_info(form, url)

        post_response = session.post(form_info['url'], data=form_info['data'])

        tmp_file = open("./{0}.html".format(username), "w")
        tmp_file.write(post_response.text.encode('utf-8'))
        tmp_file.close()

        response_dom = BeautifulSoup(post_response.text, 'html.parser')
        span_elements = response_dom.find_all('span')
        for span_element in span_elements:
            if 'class' in span_element.attrs and 'queue_sub_text' in span_element['class']:
                print(span_element.contents)
                break

        return process_forms(session, response_dom, url)
    else:
        div_elements = dom.find_all('div')
        for div_element in div_elements:
            if 'class' in div_element.attrs and 'subtext' in div_element['class']:
                if "tomorrow" not in str(div_element):
                    print(div_element.contents)
                    sleep(5)
                    return False
        return True


def start_queue(session, url=None, tries=0):
    max_tries = 5
    if url is None:
        url = 'https://store.steampowered.com/explore/startnew'
    response = session.get(url)

    if response.status_code is 200:
        base_dom = BeautifulSoup(response.text, 'html.parser')
        if not process_forms(session, base_dom, url):
            return start_queue(session)
        else:
            return True
    else:
        if tries < max_tries:
            tries += 1
            print("Bad response code: {0}".format(response.status_code))
            return start_queue(session, url, tries)
        else:
            print("Failed to load page {0} too many times ({1})".format(url, max_tries))
            return False


def login(user, secret, previous_code=None):
    wait = 10
    sa = SteamAuthenticator(secret)
    code = sa.get_code()
    if previous_code is None or previous_code != code:
        try:
            print("Successful login ({0}) with 2fa code".format(user.username))
            return user.login(twofactor_code=code)
        except wa.TwoFactorCodeRequired:
            return login(user, secret, code)
    else:
        print("2fa code failed; waiting {0} seconds and trying again".format(wait))
        sleep(wait)
        return login(user, secret, code)


def process_config(user_config):
    if 'username' in user_config and 'password' in user_config:
        user = wa.WebAuth(user_config['username'], user_config['password'])
        if 'steam_guard' in user_config:
            secret = user_config['steam_guard']
            session = login(user, secret)
            if session is not None:

                if start_queue(session):
                    print("Successfully processed queue")
                else:
                    print("Failed to process queue")
            else:
                print("Unable to login...")
        else:
            print("steam_guard is not defined in config")
    else:
        print("username or password is not defined in config")


configs_dir = "./configs"

config_files = get_all_config_files(configs_dir)

base_config = {}
base_config_file = '{0}/config.json'.format(configs_dir)

for config_file in config_files:
    # exclude base config (config.json)
    if config_file != base_config_file:
        try:
            config = json.loads(open(config_file, "r").read())
            if username is None or config['username'] == username:
                process_config(config)
        except ValueError, e:
            print(e.message)
            pass
