import os
import json
import time
import upwork
import urllib2
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
    while try_number < 5:
        try_number += 1
        try:
            profile = client.provider.get_provider(profile_str)
            break
        except upwork.exceptions.HTTP403ForbiddenError:
            print 'upwork.exceptions.HTTP403ForbiddenError at counter = ', counter, ' Try #: ', try_number
            time.sleep(3)
        except urllib2.HTTPError:
            print 'urllib2.HTTPError at counter = ', counter, ' Try #: ', try_number
            time.sleep(3)

    if try_number < 5:
        return profile
    else:
        return None

client = web_based_app()

ids_list = list()
with open('data/ids_da.txt') as f:
    for line in f:
        ids_list.append(line.strip())

outfile = 'data/detailed_profiles_da.txt'

step = 40000
outroot = 'data/detailed_profiles_da'
for index, base in enumerate(range(0, 240000, step)):
    print "Base = {}".format(base)
    outfile = outroot + '_' + str(index) + '.txt'
    with open(outfile, 'w') as outf:
        for counter, _id in enumerate(ids_list[base:base+step]):
            if counter % 1000 == 0:
                print 'Number of records = {}'.format(base+counter)
            profile = GrabProfile(base+counter, _id)
            if profile is not None:
                outf.write(json.dumps(profile)+'\n')
            else:
                print 'Not found: ID #: {}'.format(_id)
    print
