
# coding: utf-8

# In[1]:

import json
import pandas as pd
import numpy as np
from pymongo import MongoClient
from collections import Counter
get_ipython().magic(u'matplotlib inline')


# Get freelancer profile by key
#
# Endpoint
# GET /api/profiles/v1/providers/{profile_key}.{format}

# In[2]:

def json_prep(in_file):
    # read the entire file `ainto a python array
    with open(in_file, 'rb') as f:
        data = f.readlines()

    # remove the trailing "\n" from each line
    data = map(lambda x: x.rstrip(), data)

    # each element of 'data' is an individual JSON object.
    # i want to convert it into an *array* of JSON objects
    # which, in and of itself, is one large JSON object
    # basically... add square brackets to the beginning
    # and end, and have all the individual business JSON objects
    # separated by a comma
    data_json_str = "[" + ','.join(data) + "]"

    data_list_of_dicts = json.loads(data_json_str)

    out_df = pd.read_json(data_json_str)
    return out_df


# ## Make lists of dicts out of JSON data

# In[80]:

# Get IDs that were scraped
infile = '../../data/profiles_by_skill/ids_da.txt'

ids_list = list()
with open(infile) as f:
    for line in f:
        ids_list.append(line.strip())


# In[81]:

print len(ids_list)
ids_set = set(ids_list)
print len(ids_set)


# In[83]:

print len(ids_list[:128175])
ids_set = set(ids_list[:128175])
print len(ids_set)


# In[ ]:




# In[ ]:




# In[5]:

jobs_df = json_prep('../../data/jobs_da_0.txt')


# In[11]:

jobs_df.info()


# In[8]:

hourly_jobs_df = jobs_df[jobs_df['job_type']=='Hourly']


# In[9]:

hourly_jobs_df.T.head(50)


# In[53]:

candidate_list = list()
for index, candidates in enumerate(jobs_df['candidates']):
    if isinstance(candidates, dict):
        if isinstance(candidates['candidate'], dict):
            # Is the only candidate
            candidate_list.append(job_seekers['candidate']['ciphertext'])
        elif isinstance(candidates['candidate'], list):
            # Is a list of candidates
            for candidate in candidates['candidate']:
                candidate_list.append(candidate['ciphertext'])
    else:
        print index


# In[59]:

for x in range(51,54):
    print x
    jobs = jobs_df.assignment_info[x]
    triage(jobs)


# In[84]:

got_job = list()
for index, assignment_info in enumerate(jobs_df['assignment_info']):
    if isinstance(assignment_info, dict):
        info = assignment_info['info']
        if isinstance(info, dict):
            got_job.append(info['ciphertext_developer_recno'])
        elif isinstance(info, list):
            for job_getter in info:
                got_job.append(job_getter['ciphertext_developer_recno'])
        else:
            print index
#             pass
    else:
        print index
#         pass


# In[86]:

print len(got_job)
got_job_set = set(got_job)
print len(got_job_set)


# In[89]:

new_ids = got_job_set.difference(ids_set)
print len(new_ids)


# In[10]:

hourly_jobs_df.info()


# In[13]:

def triage(dict_, level=0):
    if not(isinstance(dict_, float) or isinstance(dict_, basestring)):
        print type(dict_)
        for key, val in dict_.iteritems():
            print ' '*level*2, key
            if isinstance(val, dict):
                triage(val, level=level+1)
            elif isinstance(val, list):
                for index, item in enumerate(val):
                    print ' '*level*2, 'item', index
                    triage(item, level=level+1)
            elif isinstance(val, basestring):
                print ' '*(level+1)*2, '=', val

for x in range(1000,1020):
    print x
    jobs = jobs_df.candidates[x]
    triage(jobs)


# In[ ]:




# In[ ]:

for x in range(20):
    print x
    jobs = df.assignments[x]
    for k1, v1 in jobs.iteritems():
        print 'k1 = ', k1
        if isinstance(v1, basestring):
            print 'basestring'
            pass
        elif isinstance(v1, dict):
            print 'dict'
            for k2, v2 in v1.iteritems():
                print '  k2 = ', k2
                if isinstance(v2, basestring):
                    print '  basestring'
                    pass
                elif isinstance(v2, dict):
                    print '  dict'
                    for k3, v3 in v2.iteritems():
                        print '    k3 = ' + k3
                elif isinstance(v2, list):
                    print '  list'
                    for index2, item in enumerate(v2):
                        print '    item', index2
                        if isinstance(item, dict):
                            for k4, v4 in item.iteritems():
                                print '    k4 = ', k4
        elif isinstance(v1, list):
            print 'list'
            for item in v1:
                print item
    print



# In[ ]:

def triage(dict_, level=0):
    if not(isinstance(dict_, float) or isinstance(dict_, basestring)):
        print type(dict_)
        for key, val in dict_.iteritems():
            print ' '*level*2, key
            if isinstance(val, dict):
                triage(val, level=level+1)
            elif isinstance(val, list):
                for index, item in enumerate(val):
                    print ' '*level*2, 'item', index
                    triage(item, level=level+1)
            elif isinstance(val, basestring):
                print ' '*(level+1)*2, '=', val

for x in range(1000,1020):
    print x
    jobs = df.dev_job_categories_v2[x]
    triage(jobs)


# In[ ]:


print 'All ID counts: {}'.format(len(all_ids_set))

outfile = project_directory_path + '/data/profiles_by_skill/' + 'ids_da.txt'

with open(outfile, 'w') as f:
    for id in all_ids_set:
        f.write(id+'\n')

# In[ ]:
