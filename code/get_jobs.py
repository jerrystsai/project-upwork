# author: Jerry Tsai
# program get_jobs.py
# creation date: 2016-04-26
# version 1.0
#
# PURPOSE:
#
import json

def json_prep(in_file):
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

    return data_list_of_dicts

def possible_key(dict):
    key_flag = False
    possible_key = ''.join([dict[key] if '~' in dict[key] else '' for key in dict.keys()])
    if possible_key <> '':
        key_flag = False
        possible_key = None
    return key_flag, possible_key

def write_job_keys(out_file_object, job_type = 'hr'):
    assignments = dict_item['assignments'][job_type]
    if isinstance(assignments, basestring):
        if '~' in assignments:
            f.write(assignments + '\n')
    elif isinstance(assignments, dict):
        if 'job' in assignments:
            assignments_jobs = assignments['job']
            if isinstance(assignments_jobs, list):
                for job in assignments_jobs:
                    if 'as_ciphertext_opening_recno' in job:
                        f.write(job['as_ciphertext_opening_recno'] + '\n')
                    else:
                        poss_key, ciphertext = possible_key(job)
                        if poss_key: f.write(ciphertext + '\n')
            elif isinstance(assignments_jobs, dict):
                if 'as_ciphertext_opening_recno' in assignments_jobs:
                    f.write(assignments_jobs['as_ciphertext_opening_recno'] + '\n')
        elif 'assignment' in assignments:
            assignments_jobs = assignments['assignment']
            if isinstance(assignments_jobs, list):
                for job in assignments_jobs:
                    if 'as_ciphertext_opening_recno' in job:
                        f.write(job['as_ciphertext_opening_recno'] + '\n')
        else:
            print 'Has neither job nor assignment as key: Row #: {}'.format(index)
            print 'Jobs:'
            for job in assignments:
                print job
                print
    elif isinstance(assignments, list):
        print 'assignments has a list, not dict. Row # {}'.format(index)
        for job in assignments:
            print job

    return None

if __name__ == '__main__':
    profiles_data_file = 'data/detailed_profiles_da.txt'
    outfile = 'data/jobs_ids.txt'

    # Make lists of dicts out of JSON data
    profiles_lod = json_prep(profiles_data_file)

    with open(outfile, 'w') as f:
        for index, dict_item in enumerate(profiles_lod):
            write_job_keys(f, job_type = 'hr')
            write_job_keys(f, job_type = 'fp')
