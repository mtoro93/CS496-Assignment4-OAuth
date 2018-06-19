# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import webapp2
import random
import string
import json
import httplib
import urllib
from google.appengine.ext.webapp import template

state=''
clientID = '#################.apps.googleusercontent.com'
clientSecret = '###############'
redirectURI = 'https://wide-surge-194519.appspot.com/oauth2callback'

class OAuthHandler(webapp2.RequestHandler):
    def get(self):
        get_values = self.request.GET
        state_value = self.request.GET['state']
        #verify state is the same
        if state_value == state:
            code_value = self.request.GET['code']
            global state
            currentState = state
            state = ''
            connection = httplib.HTTPSConnection('www.googleapis.com/oauth2/v4/token')
            payload = urllib.urlencode({'code': code_value, 'client_id': clientID, 'client_secret': clientSecret, 'redirect_uri': redirectURI, 'grant_type': 'authorization_code'})
            header = {"Content-type": "application/x-www-form-urlencoded; charset=utf-8"}
            connection.request('POST', '', payload, header)
            post_res = connection.getresponse()
            post_data = post_res.read()
            post_data_json = json.loads(post_data)
            access = 'Bearer '
            access+=post_data_json['access_token']
            #send a GET Request
            connection.close()
            connection = httplib.HTTPSConnection('www.googleapis.com/plus/v1/people/me')
            connection.request('GET', '', None, {"Authorization": access})
            get_res = connection.getresponse()
            get_data = get_res.read()
            #self.response.out.write(get_data)
            get_data_json = json.loads(get_data)
            name = get_data_json['name']
            firstName = name['givenName']
            lastName = name['familyName']
            if 'url' in get_data_json:
                profileURL = get_data_json['url']
                template_values = {
                        'first_name': firstName,
                        'last_name': lastName,
                        'url': profileURL,
                        'state': currentState
                        }
                path = os.path.join(os.path.dirname(__file__), 'end.html')
                self.response.out.write(template.render(path, template_values))
            else:
                template_values = {
                        'first_name': firstName,
                        'last_name': lastName,
                        'url': 'none',
                        'state': currentState
                        }
                path = os.path.join(os.path.dirname(__file__), 'end.html')
                self.response.out.write(template.render(path, template_values))


class MainPage(webapp2.RequestHandler):
    def get(self):
        global state
        global clientID
        server_url = 'https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id='
        server_url+=clientID
        server_url+='&redirect_uri=https://wide-surge-194519.appspot.com/oauth2callback&scope=email&state='
        state=''.join([random.choice(string.ascii_uppercase + string.digits) for _ in range(7)])
        server_url+=state
        template_values = {
                'url': server_url,
                'url_linktext': 'Click here to begin the OAuth Process'
                }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth2callback', OAuthHandler)
], debug=True)
