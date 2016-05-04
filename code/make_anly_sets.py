# author: Jerry Tsai
# program make_anly_sets.py
# creation date: 2016-05-03
# version 1.0
#
# PURPOSE: Make several analysis data sets from the data in the
# Upwork provider profiles data (text file)
#

import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import time
import datetime
import re
import cPickle as pickle


def json_prep(in_file):
    '''
    Create pandas dataframe from text file of JSON strings
    '''
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

def triage(dict_, level=0):
    '''
    Visualize JSON data
    "Pretty Print" data, showing nesting via indentation
    '''
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


# ## Make pandas DataFrame out of detailed profiles data for exploration

profiles_df = json_prep('data/detailed_profiles_da.txt')

# ## Clean up and mung profiles data

# Drop agency information. Not going to attempt to assign effect to agency due to low participation frequency in agencies in general and most agencies have few people, so will not have sufficient power.
profiles_df.drop(['ag_cny_recno', 'ag_country', 'ag_country_tz', 'ag_description', 'ag_logo', 'ag_name', 'ag_recent_hours',     'ag_total_hours', 'agency_ciphertext'     ], axis=1, inplace=True)

# Drop redundant variables.
profiles_df.drop(['dev_portrait_100', 'dev_portrait_32', 'dev_portrait_50', 'dev_recno'     ], axis=1, inplace=True)

# Drop obviously or inherently irrelevant variables.
profiles_df.drop(['dev_ui_profile_access', 'permalink'], axis=1, inplace=True)

# Drop variables with data leak.
profiles_df.drop(['dev_adj_score', 'dev_adj_score_recent', 'dev_billed_assignments', 'dev_last_activity', 'dev_last_worked',     'dev_last_worked_ts', 'dev_portfolio_items_count', 'dev_tot_feedback',     'dev_total_hours'], axis=1, inplace=True)

# Drop variables that may be good to use, but for which I do not currently have the time to work up.

profiles_df.drop(['dev_city', 'dev_first_name', 'dev_last_name', 'dev_short_name'     ], axis=1, inplace=True)

# Drop variables that seem useful, but do not appear to someone looking at the profile, so are therefore non-factors in evaluating the profile.
profiles_df.drop(['dev_job_categories_v2', 'job_categories'     ], axis=1, inplace=True)


# In[4]:

### CREATE DERIVED VARIABLES

# `ciphertext` and `dev_recno_ciphertext`
equality_of_ciphertext = profiles_df['ciphertext'] == profiles_df['dev_recno_ciphertext']

if all(equality_of_ciphertext) == True:
    print 'All ciphertext == dev_recno_ciphertext'
    profiles_df.drop(['ciphertext'], axis=1, inplace=True)

# `dev_ac_agencies`: presence or absence
profiles_df['agency_affl'] = profiles_df['dev_ac_agencies'] <> ''

# `dev_bill_rate`: WILL LEAVE ALONE

# `dev_blurb`: WILL LEAVE ALONE

# `dev_country`: leaving it alone for now, will study it in the analysis

# CODE TO EXAMINE dev_country
# def pct_freq(series):
# return 1. * series.value_counts() / len(series)
# print pct_freq(profiles_df['dev_country'])

# CODE TO EXAMINE dev_eng_skill
# `dev_eng_skill`: leaving it alone for now, will study it in the analysis
# profiles_df.dev_eng_skill.value_counts(dropna=False)

# `dev_groups`
profiles_df['group_affl'] = profiles_df['dev_groups'] <> ''
# Check work
# print profiles_df['group_affl'].value_counts(dropna=True)

# Examine agency and group membership
# pd.crosstab(profiles_df['agency_affl'], profiles_df['group_affl'], dropna=False)

# `dev_portrait`: presence or absence
profiles_df['has_portrait'] = profiles_df['dev_portrait'] <> ''
# profiles_df['has_portrait'].value_counts(dropna=True)

# `dev_profile_title`: leaving it alone, will study it in the analysis
# profiles_df['dev_profile_title'][:5]

# `dev_timezone`: leaving it alone, will study it in the analysis
profiles_df['dev_timezone'].value_counts(dropna=True)


### "MULTI"-VARIABLES (I.E., NESTED JSON VARIABLES)

def grab_data(datalist, creature, id_, list_of_keys):
    if isinstance(creature, basestring):
        pass
    elif isinstance(creature, dict):
        tuple_to_add = tuple([id_] + [creature.get(key, '') for key in list_of_keys])
        datalist.append(tuple_to_add)
    elif isinstance(creature, list):
        for creature_item in creature:
            tuple_to_add = tuple([id_] + [creature_item.get(key, '') for key in list_of_keys])
            datalist.append(tuple_to_add)


### GOING THROUGH EACH "MULTI"-VARs

# ### `assignments`:

### CREATE LIST OF TUPLES ABOUT JOBS
jobs_tuples = list()

key_list = ['as_opening_title', 'as_from_full', 'as_to_full', \
            'as_rate', 'as_total_hours_precise', 'as_total_charge', \
            'as_job_type' \
            ]

for index, assignments_tuple in \
  enumerate(profiles_df[['dev_recno_ciphertext', 'assignments']].itertuples(index=False)):
    profile_id = assignments_tuple[0]
    assignments = assignments_tuple[1]
    if 'hr' in assignments:
        hr_assignments = assignments['hr']
        if 'job' in hr_assignments:
            grab_data(jobs_tuples, hr_assignments['job'], profile_id, key_list)
        elif 'assignment' in hr_assignments:
            grab_data(jobs_tuples, hr_assignments['assignment'], profile_id, key_list)

    if 'fp' in assignments:
        fp_assignments = assignments['fp']
        if 'job' in fp_assignments:
            grab_data(jobs_tuples, fp_assignments['job'], profile_id, key_list)
        elif 'assignment' in fp_assignments:
            grab_data(jobs_tuples, fp_assignments['assignment'], profile_id, key_list)

### MAKE PANDAS DATAFRAME FROM LIST OF TUPLES
jobs_df = pd.DataFrame(jobs_tuples)
jobs_df.columns = ['dev_recno_ciphertext'] + key_list

# CHECK WORK
# jobs_df['dev_recno_ciphertext'].nunique()


### MAKE PANDAS DATAFRAME FOR HOURLY PAID JOBS DATA
def blank_or_zero(str):
    if str == '':
        return True
    else:
        match = re.search(r'\d+.*\d*', str)
        number = float(match.group())
        if number == 0:
            return True
        else:
            return False

def get_number(str):
    return float(re.search(r'\d+.*\d*', str).group())

hr_paid_jobs_df = jobs_df[(jobs_df['as_job_type'] == 'Hourly') & (~jobs_df['as_rate'].apply(blank_or_zero))]

rate_as_number = hr_paid_jobs_df['as_rate'].apply(get_number)
rate_as_number.name='rate_as_number'
hr_paid_jobs_df = pd.concat([hr_paid_jobs_df, rate_as_number], axis=1)

### DELETE COLUMNS THAT WON'T BE USED
hr_paid_jobs_df.drop(['as_opening_title', 'as_job_type'], axis=1, inplace=True)
# hr_paid_jobs.head(50)


# ### `education`:

def degree_categ(str):
    if 'master' in str.lower():
        return 'Master'
    elif 'bachelor' in str.lower():
        return 'Bachelor'
    elif 'doctor' in str.lower():
        return 'Doctor'
    elif 'b.' in str.lower():
        return 'Bachelor'
    elif 'm.' in str.lower():
        return 'Master'
    elif 'mba' in str.lower():
        return 'Master'
    elif 'msc' in str.lower():
        return 'Master'
    elif 'bsc' in str.lower():
        return 'Bachelor'
    elif 'bs' in str.lower():
        return 'Bachelor'
    elif 'ba ' in str.lower():
        return 'Bachelor'
    elif 'ms' in str.lower():
        return 'Master'
    elif 'ma' in str.lower():
        return 'Master'
    elif 'phd' in str.lower():
        return 'Doctor'
    elif 'ph.d' in str.lower():
        return 'Doctor'
    elif 'engineer' in str.lower():
        return 'Engineer'
    else:
        return 'Other'
vect_deg_cat = np.vectorize(degree_categ)

def degree_score(ed_degree):
    if degree_categ(ed_degree) == 'Bachelor':
        return 1
    elif degree_categ(ed_degree) == 'Engineer':
        return 2
    elif degree_categ(ed_degree) == 'Master':
        return 3
    elif degree_categ(ed_degree) == 'Doctor':
        return 4
    elif degree_categ(ed_degree) == 'Other':
        return 0

def grab_max_data(datalist, creature, id_, max_func, key_to_be_maxed, list_of_keys):
    if isinstance(creature, basestring):
        tuple_to_add = tuple((id_, 'Other'))
    elif isinstance(creature, dict):
        tuple_to_add = tuple([id_] + [creature.get(key, '') for key in list_of_keys])
        datalist.append(tuple_to_add)
    elif isinstance(creature, list):
        curr_score = -1
        for creature_item in creature:
            score = max_func(creature_item.get(key_to_be_maxed, ''))
            if score > curr_score:
                tuple_to_beat = tuple([id_] + [creature_item.get(key, '') for key in list_of_keys])
                curr_score = score
                tuple_to_add = tuple_to_beat
                datalist.append(tuple_to_add)

### CREATE EDUCATION TUPLES, RETURNING HIGHEST DEGREE ACHIEVED FOR EACH PERSON
degrees_tuples = list()
for index, education_tuple in enumerate(profiles_df[['dev_recno_ciphertext', 'education']].itertuples(index=False)):
    profile_id = education_tuple[0]
    schools = education_tuple[1]
    if isinstance(schools, basestring):
        degrees_tuples.append((profile_id, 'Other'))
    else:
        for key in schools.keys():
            if key == u'institution':
                school_institution = schools['institution']
                grab_max_data(degrees_tuples, school_institution, profile_id, degree_score, 'ed_degree', ['ed_degree'])

# CHECK WORK
# for index, tup in enumerate(degrees_tuples):
# print tup
# if index > 4: break


### CREATE DATA FRAME INDICATING HIGHEST DEGREE ACHIEVED
### AND ADD `highest_degree` to analysis data set
degrees_df = pd.DataFrame(degrees_tuples)
degrees_df.columns = ['dev_recno_ciphertext'] + ['highest_degree']

profiles_df['highest_degree'] = degrees_df['highest_degree']


# In[5]:

# ### `experiences` will be skipped because of uncertain usefulness and lack of time

# ### `portfolio_items`: presence or absence
profiles_df['has_portfolio'] = profiles_df['portfolio_items'] <> ''

# ### `tsexams`: presence or absence

profiles_df['took_tests'] = profiles_df['tsexams'] <> ''
# profiles_df['took_tests'].value_counts(dropna=True)

# ### `skills`
### CREATE LIST OF TUPLES ABOUT SKILLS
skills_tuples = list()
key_list = ['skl_name']

for index, skills_tuple in enumerate(profiles_df[['dev_recno_ciphertext', 'skills']].itertuples(index=False)):
    profile_id = skills_tuple[0]
    skills = skills_tuple[1]
    skills_list = list()
    if 'skill' in skills:
        grab_data(skills_tuples, skills['skill'], profile_id, key_list)

### CREATE PANDAS DATA FRAME FROM LIST OF TUPLES
skills_df = pd.DataFrame(skills_tuples)
skills_df.columns = ['dev_recno_ciphertext'] + key_list

### MODIFY SKILLS SO THAT CountVectorizer TREATS THEM AS SINGLE WORDS
### AND NOT AS MULTIPLE WORDS OR ONE-LETTER CHARACTERS TO IGNORE
def multiple_replace(dict, text):
    # Make one-letter skills longer
    if text == 'c':
        longtext = 'cprog'
    elif text == 'r':
        longtext = 'rprog'
    elif text == 's':
        longtext = 'sprog'
    else:
        longtext = text

    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], longtext)

substitution_dict = { \
    '+': 'plus', \
    '#': 'sharp', \
    '/': 'slash', \
    '-': 'dash', \
    '.': 'dot' \
}

def contiguous_word(skill):
    return multiple_replace(substitution_dict, skill)

### CREATE PROFILE-LEVEL SKILLS VARIABLE ('skills_string')
###   TO FEED INTO CountVectorizer
skills_content_list = list()
key_list = ['skills_string']
start_tuple_number = 0
end_tuple_number = len(skills_tuples) - 1

for index, skills_tuple in enumerate(skills_tuples):
    if index == start_tuple_number:
        curr_ciphertext = skills_tuple[0]
        skills_string = contiguous_word(skills_tuple[1])
    elif curr_ciphertext == skills_tuple[0]:
        skills_string += (' ' + contiguous_word(skills_tuple[1]) )
    elif curr_ciphertext <> skills_tuple[0]:
        skills_content_list.append((curr_ciphertext, skills_string))
        curr_ciphertext = skills_tuple[0]
        skills_string = contiguous_word(skills_tuple[1])

    if index == end_tuple_number:
        skills_content_list.append((curr_ciphertext, skills_string))


### CREATE PANDAS DATAFRAME
skills_content_df = pd.DataFrame(skills_content_list)
skills_content_df.columns = ['dev_recno_ciphertext'] + key_list

### ADD `skills_string` to PROFILES DATAFRAME
profiles_df['skills_string'] = skills_content_df['skills_string']

skill_vectorizer = CountVectorizer()
sv_sparse_matrix = skill_vectorizer.fit_transform(profiles_df['skills_string'])

# CHECK WORK
# frequencies = sum(sv_sparse_matrix).toarray()[0]
# check_work = pd.DataFrame(frequencies, index=skill_vectorizer.get_feature_names(), columns=['frequency'])

### MAKE SKILLS VECTORIZED DF
skills_vectorized_df = pd.DataFrame(sv_sparse_matrix.todense())
skills_vectorized_df.columns = list(skill_vectorizer.get_feature_names())

# ### Drop variables from which other variables have been derived.
profiles_df.drop([ \
                  'dev_ac_agencies', 'dev_groups', \
                  'dev_is_affiliated' \
                  ], axis=1, inplace=True)

# ### Drop aggregate variables
profiles_df.drop([ \
                 'assignments', 'experiences', 'portfolio_items', 'skills', 'tsexams' \
                 ], axis=1, inplace=True)

### MAKE PICKLES OF NEW DATAFRAMES
outfile_skills_vectorized = 'data/_skills_vectorized_df.pkl'
outfile_profiles = 'data/profiles_df.pkl'
outfile_jobs = 'data/jobs_df.pkl'
outfile_hr_paid_jobs = 'data/hr_paid_jobs_df.pkl'
outfile_skills = 'data/skills_df.pkl'

outfile_list = [ \
outfile_skills_vectorized, \
outfile_profiles, \
outfile_jobs, \
outfile_hr_paid_jobs, \
outfile_skills \
]

out_df_list = [ \
skills_vectorized_df, \
profiles_df, \
jobs_df, \
hr_paid_jobs_df, \
skills_df \
]

for index, outfile in enumerate(outfile_list):
    f = open(outfile, 'wb')
    pickle.dump(out_df_list[index], f)
    f.close()
