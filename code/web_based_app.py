# author: Jerry Tsai
# program: web_based_app.py
# creation date: 2016-04-21
# version 1.0
#
# PURPOSE:
# Helper functions
# * To obtain Upwork API client
# * Rate limit calls
#
# Thanks to Greg Burek for RateLimited(), a useful decorator to rate
#   limit function calls, ideal for web scraping an API with rate limits.
#   http://blog.gregburek.com/2011/12/05/Rate-limiting-with-decorators/
#

import json
import time
import upwork

def web_based_app():
    """Emulation of web-based app.
    Your keys should be created with project type "Web".
    Returns: ``upwork.Client`` instance ready to work.
    """
    print "Emulating web-based app"

    with open('keys.json') as data_file:
        keys = json.load(data_file)
    # public_key = raw_input('Please enter public key: > ')
    # secret_key = raw_input('Please enter secret key: > ')
    public_key = keys['public_key']
    secret_key = keys['secret_key']

    #Instantiating a client without an auth token
    # client = upwork.Client(public_key, secret_key)
    client = upwork.Client(keys['public_key'], keys['secret_key'])

    print "Please go to this URL (authorize the app if necessary):"
    print client.auth.get_authorize_url()
    print "After that you should be redirected back to your app URL with " + \
          "additional ?oauth_verifier= parameter"

    verifier = raw_input('Enter oauth_verifier: ')

    oauth_access_token, oauth_access_token_secret = \
        client.auth.get_access_token(verifier)

    # Instantiating a new client, now with a token.
    # Not strictly necessary here (could just set `client.oauth_access_token`
    # and `client.oauth_access_token_secret`), but typical for web apps,
    # which wouldn't probably keep client instances between requests
    client = upwork.Client(public_key, secret_key,
                          oauth_access_token=oauth_access_token,
                          oauth_access_token_secret=oauth_access_token_secret)

    return client

def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate
