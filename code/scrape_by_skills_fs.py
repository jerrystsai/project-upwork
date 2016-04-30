# author: Jerry Tsai
# program scrape_skills_fs.py
# creation date: 2016-04-23
# version 1.0
#
# PURPOSE:
# Given skills of full stack web developers, return all
#   profiles that have at least one of these skills
#

# @RateLimited(0.462)  # 0.462 per second or essentially every 2.16 seconds or so
import json
import time
import upwork
import urllib2
from web_based_app import web_based_app, RateLimited

@RateLimited(0.462)
def GrabProviders(counter):
    while True:
        try:
            provider_list = client.provider_v2.search_providers(data=the_query, \
                page_offset=counter, page_size=page_size)
            break
        except upwork.exceptions.HTTP403ForbiddenError:
            print 'upwork.exceptions.HTTP403ForbiddenError at counter = ', counter
            time.sleep(3)
        except urllib2.HTTPError:
            print 'urllib2.HTTPError at counter = ', counter
            time.sleep(3)
    return provider_list

skills_list = \
[ \
u'ajax', \
u'angularjs', \
u'bootstrap', \
u'css', \
u'css3', \
u'c#', \
u'django-framework', \
u'html', \
u'html5', \
u'javascript', \
u'jquery', \
u'laravel-framework', \
u'node.js', \
u'php', \
u'postgresql', \
u'ruby', \
u'ruby-on-rails', \
u'twitter-bootstrap', \
u'wordpress' \
]

# These full stack skills already scraped by:
#     scrape_by_skills_da.py
# u'java', \
# u'mongodb', \
# u'mysql', \
# u'python', \
# u'sql', \


client = web_based_app()

page_size = 100
for skill in skills_list:
    print "Skill = ", skill
    the_query = {'skills': skill}
    outfile = 'data/' + skill + '.txt'

    counter = 0
    query_done_flag = False
    with open(outfile, 'w') as f:
        while query_done_flag == False:
            if counter % 10000 == 0:
                print 'Number of records = {}'.format(counter)
            provider_list = GrabProviders(counter)
            # data_list.append(provider_list)
            for provider in provider_list:
                f.write(json.dumps(provider)+'\n')
            if len(provider_list) < page_size:
                print 'Length of provider list = ', len(provider_list), \
                      'Counter = ', counter
                query_done_flag = True
                if len(provider_list) == 0:
                    break
            counter += 100
    print
