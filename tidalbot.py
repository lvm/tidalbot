#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy, time, sys
import os
from subprocess import Popen, PIPE, STDOUT
import config # includes the below keys + secrets for twitter
import re
import requests
from pprint import pprint

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_KEY, config.ACCESS_SECRET)
api = tweepy.API(auth)



class TidalbotListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)
        matcher = re.compile(r'@tidalbot\s*')
        code = matcher.sub('', status.text)
        code = code.decode('unicode_escape').encode('ascii', 'ignore')
        print("code: " + code)
        p = Popen(['./runpattern'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        tidalout = p.communicate(input=code)[0]
        print(tidalout.decode())
        print("return code: " + str(p.returncode))
        if p.returncode == 0:
            clyp_file_upload_url = 'http://upload.clyp.it/upload'
            cyclefile = open('/home/tidalbot/tidalbot/cycle.wav', 'rb')
            send_files = {'audioFile': ('cycle.wav',cyclefile, 'audio/wav'),
                          'description': code
                         }
            r = requests.post(clyp_file_upload_url, files=send_files)
            print(r.status_code)
            clypurl = r.json()['Url']
            pprint(r.json())
            print(clypurl)
            m = ".@%s Listen: %s" % (status.user.screen_name, clypurl)
            api.update_status(m, in_reply_to_status_id = status.id)
        else:
            m = "@%s Sorry there's something wrong with that pattern" % (status.user.screen_name)
            api.update_status(m, in_reply_to_status_id = status.id)


tidalbotListener = TidalbotListener()
stream = tweepy.Stream(auth = api.auth, listener=tidalbotListener)

stream.filter(track=['@tidalbot'])
