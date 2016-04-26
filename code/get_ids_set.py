import os
import json
import time
import upwork
import urllib2
# from web_based_app import web_based_app, RateLimited
# from code.web_based_app import web_based_app, RateLimited

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

#     now, load it into pandas
#     out_df = pd.read_json(data_json_str)
    return data_list_of_dicts

# @RateLimited(0.462)
# def GrabProfiles(counter, profile_str):
#     while True:
#         try:
#             profile = client.provider.get_provider(profile_str)
#             # profile_list = client.provider.get_provider(profiles_str)
#             client.provider.get_provider(profile_list)
#
#             break
#         except upwork.exceptions.HTTP403ForbiddenError:
#             print 'upwork.exceptions.HTTP403ForbiddenError at counter = ', counter
#             time.sleep(3)
#         except urllib2.HTTPError:
#             print 'urllib2.HTTPError at counter = ', counter
#             time.sleep(3)
    # return provider_list

# project_directory_path = '/Users/JerryTsai/userjst/individ/knowledg/cur/galvanize/project-upwork'
project_directory_path = os.getcwd()
list_of_filenames = os.listdir(project_directory_path + '/data/profiles_by_skill')

all_ids_set = set()
for filename in list_of_filenames:
    # Set up
    if filename[-4:] == '.txt':
        skill_name = filename[:-4].replace('-', '_').replace('#', 'Sharp')
        filepath = project_directory_path + '/data/profiles_by_skill/' + filename

        profiles_lod = json_prep(filepath)
        ids_list = []
        for profile_as_dict in profiles_lod:
            ids_list.append(profile_as_dict['id'])

        ids_set = set(ids_list)
        print 'Skill: {}, ID count {}'.format(skill_name, len(ids_set))
        all_ids_set.update(ids_set)

print 'All ID counts: {}'.format(len(all_ids_set))

outfile = project_directory_path + '/data/profiles_by_skill/' + 'ids_da.txt'

with open(outfile, 'w') as f:
    for id in all_ids_set:
        f.write(id+'\n')

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
# client = web_based_app()
