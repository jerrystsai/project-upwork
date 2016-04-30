# author: Jerry Tsai
# program scrape_jobs.py
# creation date: 2016-04-27
# version 1.0
#
# PURPOSE: Given a text file of jobs IDs (aka "ciphertext"),
# write a text file containing their detailed job profile information.
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

@RateLimited(0.60)
def GrabProfile(counter, profile_str):
    try_number = 0
    success = False
    while try_number < 2:
        try_number += 1
        try:
            profile = client.job.get_job_profile(profile_str)
        except upwork.exceptions.HTTP403ForbiddenError:
            print 'upwork.exceptions.HTTP403ForbiddenError at counter = ', counter, ' Try #: ', try_number
            time.sleep(2.2)
        except urllib2.HTTPError:
            print 'urllib2.HTTPError at counter = ', counter, ' Try #: ', try_number
            time.sleep(2.2)
        except urllib3.exceptions.MaxRetryError:
            print 'urllib3.exceptions.MaxRetryError at counter = ', counter, 'Try #: ', try_number
            time.sleep(2.2)
        else:
            success = True
            break

    if success == True:
        return profile
    else:
        return None

client = web_based_app()

infile = 'data/jobs_ids_unique.txt'

ids_list = list()
with open(infile) as f:
    for line in f:
        ids_list.append(line.strip())

step = 10000
outroot = 'data/jobs_da'
for index, base in enumerate(range(1000, 150000, step)):
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
