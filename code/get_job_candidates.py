# author: Jerry Tsai
# program get_job_candidates.py
# creation date: 2016-04-29
# version 1.0
#
# PURPOSE: Given a text file of detailed job profiles, return
# the ids for the candidates for those jobs and ids for the people to
# which the job was assigned. From this set of ids, remove all
# ids that were previously scraped by get_ids_set.py and placed in
# the text file, data/profiles_by_skill/ids_da.txt. Write out the
# the resulting set of ids to a text file,
#   data/candidates_da.txt
#

import json
import pandas as pd
import numpy as np

def json_prep(in_file):
    '''
    Read in a text file where each line is a JSON string and
    return a pandas dataframe

    in_file: str: filename
    '''
    # read the entire file into a python array
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

def get_candidates_list(df):
    '''
    Given a pandas DataFrame containing Upwork job profiles, return
    ids of candidates and job getters as a set
    '''

    job_cats = list()
    for index, cat2_info in enumerate(jobs_df['op_job_category_v2']):
        cat_found = False
        if isinstance(cat2_info, dict):
            cat1_info = cat2_info['op_job_category_v']
            if isinstance(cat1_info, dict):
                groups = cat1_info['groups']
                if isinstance(groups, dict):
                    group = groups['group']
                    if 'name' in group:
                        job_cats.append(group['name'])
                        cat_found = True
        if cat_found == False:
            job_cats.append('')

    job_cats_array = np.array(job_cats)
    jobs_da = jobs_df[job_cats_array == u'Data Science & Analytics']

    candidate_list = list()
    for index, candidates in enumerate(jobs_da['candidates']):
        if isinstance(candidates, dict):
            if isinstance(candidates['candidate'], dict):
                # Is the only candidate
                candidate_list.append(candidates['candidate']['ciphertext'])
            elif isinstance(candidates['candidate'], list):
                # Is a list of candidates
                for candidate in candidates['candidate']:
                    candidate_list.append(candidate['ciphertext'])

    candidate_set = set(candidate_list)

    job_getter_list = list()
    for index, assignment_info in enumerate(jobs_da['assignment_info']):
        if isinstance(assignment_info, dict):
            if 'info' in assignment_info:
                info = assignment_info['info']
            else:
                print index, assignment_info
            if isinstance(info, dict):
                job_getter_list.append(info['ciphertext_developer_recno'])
            elif isinstance(info, list):
                for job_getter in info:
                    job_getter_list.append(job_getter['ciphertext_developer_recno'])

    job_getter_set = set(job_getter_list)

    jobs_associated_ids = candidate_set.union(job_getter_set)
    return jobs_associated_ids

if __name__ == '__main__':
    # GET MASTER LIST OF IDs PREVIOUSLY SCRAPED (if the Upwork API allowed)
    infile = 'data/profiles_by_skill/ids_da.txt'

    ids_list = list()
    with open(infile) as f:
        for line in f:
            ids_list.append(line.strip())
    ids_set = set(ids_list)
    print 'Number of IDs that were originally desired to be scraped: {}'.format(len(ids_set))

    jobs_profiles_list = \
    [ \
    'data/jobs_da_0.txt', \
    'data/jobs_da_1.txt', \
    'data/jobs_da_2.txt', \
    'data/jobs_da_3.txt', \
    'data/jobs_da_4.txt', \
    'data/jobs_da_5.txt', \
    ]

    all_jobs_associated_ids = set()
    for index, jobs_profiles_file in enumerate(jobs_profiles_list):
        jobs_df = json_prep(jobs_profiles_file)
        jobs_associated_ids = get_candidates_list(jobs_df)
        print 'Number of job_associated_ids for list item {}: {}'.format(index, len(jobs_associated_ids))

        all_jobs_associated_ids = all_jobs_associated_ids.union(jobs_associated_ids)

    not_yet_scraped_ids = all_jobs_associated_ids.difference(ids_set)
    print 'Number of ids not yet scraped: {}'.format(len(not_yet_scraped_ids))

    outfile = 'data/candidates_da_0_to_5.txt'

    with open(outfile, 'w') as f:
        for id_ in not_yet_scraped_ids:
            f.write(id_+'\n')

    # print 'All ID counts: {}'.format(len(all_ids_set))
    #
    # outfile = project_directory_path + '/data/profiles_by_skill/' + 'ids_da.txt'
    #
    # with open(outfile, 'w') as f:
    #     for id in all_ids_set:
    #         f.write(id+'\n')
