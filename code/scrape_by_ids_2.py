# author: Jerry Tsai
# program: scrape_by_ids_2.py
# creation date: 2016-04-30
# version 1.0
#
# PURPOSE: Given a text file of freelancers' IDs (aka "ciphertext"),
# write a text file containing their detailed profile information.
# Each line is a JSON string.
#

import os
import json
import time
from datetime import datetime
import upwork
import urllib2
import urllib3
from web_based_app import web_based_app, RateLimited

# Use only if you can read multiple IDs from get_provider()
#
# list_size = 5
# counter = 0
# set_size_m_1 = len(all_ids_set) - 1
# for index, id in enumerate(all_ids_set):
#     remainder = counter % list_size
#     if remainder == 0:
#         id_list = []
#     id_list.append(id)
#     if remainder == (list_size-1) or counter == set_size_m_1:
#         profiles_str = ';'.join(id_list)
#         print profiles_str
#     counter += 1
#

@RateLimited(0.462)
def GrabProfile(counter, profile_str):
    try_number = 0
    success = False
    while try_number < 4:
        try_number += 1
        try:
            profile = client.provider.get_provider(profile_str)
        except upwork.exceptions.HTTP403ForbiddenError:
            print 'upwork.exceptions.HTTP403ForbiddenError at counter = ', counter, ' Try #: ', try_number
            time.sleep(3)
        except urllib2.HTTPError:
            print 'urllib2.HTTPError at counter = ', counter, ' Try #: ', try_number
            time.sleep(3)
        except urllib3.exceptions.MaxRetryError:
            print 'urllib3.exceptions.MaxRetryError at counter = ', counter, 'Try #: ', try_number
            time.sleep(3)
        else:
            success = True
            break

    if success == True:
        return profile
    else:
        return None

client = web_based_app()

infile = 'data/candidates_da.txt'

ids_list = list()
with open(infile) as f:
    for line in f:
        ids_list.append(line.strip())

step = 10000
outroot = 'data/detailed_profiles_da_cand'
for index, base in enumerate(range(0, 10000, step)):
    print "Base = {} {}".format(base, str(datetime.now()))
    outfile = outroot + '_' + str(index) + '.txt'
    out_notfound_file = outroot + '_notfound_' + str(index) + '.txt'
    with open(outfile, 'w') as outf, open(out_notfound_file, 'w') as outnff:
        for counter, _id in enumerate(ids_list[base:base+step]):
            if counter % 1000 == 0:
                print 'Number of records = {}'.format(base+counter)
            profile = GrabProfile(base+counter, _id)
            if profile is not None:
                outf.write(json.dumps(profile)+'\n')
            else:
                outnff.write(json.dumps(_id)+'\n')
                print 'Not found: ID #: {}'.format(_id)
    print
