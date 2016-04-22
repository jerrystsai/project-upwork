# author: Jerry Tsai
# program scrape_skills.py
# creation date: 2016-04-20
# version 1.0
#
# PURPOSE:
# Find the skills of people claiming to be "Data Scientist"s
#

# @RateLimited(0.462)  # 0.462 per second or essentially every 2.16 seconds or so
import json
from web_based_app import web_based_app, RateLimited

@RateLimited(0.6)
def GrabProviders(counter):
    provider_list = client.provider_v2.search_providers(data=the_query, \
        page_offset=counter, page_size=page_size)
    return provider_list

client = web_based_app()

the_query = {'skills':['', ]}
data_list = []
page_size = 100
counter = 0
query_done_flag = False

with open('data/data_science.txt', 'w') as f:
    while query_done_flag == False:
        provider_list = GrabProviders(counter)
        # data_list.append(provider_list)
        for provider in provider_list:
            f.write(json.dumps(provider)+'\n')
        if len(provider_list) < page_size:
            query_done_flag = True
            if len(provider_list) == 0:
                break
        counter += 100
