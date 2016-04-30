import json
import upwork
import pickle
from pprint import pprint

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


if __name__ == '__main__':
    client = web_based_app()

    try:
        print "My info"
        pprint(client.auth.get_info())
#        print "Team rooms:"
#        pprint(client.team.get_teamrooms())
        #HRv2 API
#       print "HR: companies"
#       pprint(client.hr.get_companies())
#       print "HR: teams"
#       pprint(client.hr.get_teams())
#       print "HR: userroles"
#       pprint(client.hr.get_user_roles())
        print "Get jobs"
#       pprint(client.provider_v2.search_jobs({'q': 'python'}))
        # python_jobs=client.provider_v2.search_jobs({'q': 'python'})
        data = {'q': 'python', 'title': 'Web Developer'}
        pyj1 = client.provider_v2.search_providers(data=data, page_offset=20, page_size=20)
        pyj2 = client.provider_v2.search_providers(data=data, page_offset=10000, page_size=20)
        print pyj1
        print pyj2
#       print "Categories"
#       print type(client.provider_v2.get_categories_metadata())
#       pprint(client.provider_v2.get_categories_metadata())
#       categories = client.provider_v2.get_categories_metadata()
#       print "Skills"
#       print type(client.provider.get_skills_metadata())
#       pprint(client.provider.get_skills_metadata())
#        skills = client.provider.get_skills_metadata()
#       print "Geographical regions"
#       print type(client.provider.get_regions_metadata())
#       print type(client.provider.get_regions_metadata()[0])
#       pprint(client.provider.get_regions_metadata())
        # regions = client.provider.get_regions_metadata()

        with open('pyj1.pkl', 'wb') as f:
            pickle.dump(pyj1, f)
        with open('pyj2.pkl', 'wb') as f:
            pickle.dump(pyj2, f)
        # with open('python_jobs.pkl', 'wb') as f:
        #     pickle.dump(python_jobs, f)
        # with open('categories.pkl', 'wb') as f:
        #     pickle.dump(categories, f)
        # with open('skills.pkl', 'wb') as f:
        #     pickle.dump(skills, f)
        # with open('regions.pkl', 'wb') as f:
        #     pickle.dump(regions, f)

    except Exception, e:
        print "Exception at %s %s" % (client.last_method, client.last_url)
        raise e
