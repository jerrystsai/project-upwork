# author: Jerry Tsai
# program most_common.py
# creation date: 2016-04-22
# version 1.0
#
# PURPOSE:
#

fs_profiles = json_read('../data/full_stack.txt')
fs_profiles['title'].value_counts()

def full_stack_in(str):
    # Some people may not have titles, in which case their titles are NaNs
    if isinstance(str, float):
        return False
    if 'full' in str.lower() and 'stack' in str.lower():
        return True
    else: return False

vect_fsi = np.vectorize(full_stack_in)
fs_profiles['fs_flag'] = vect_fsi(np.array(fs_profiles[u'title']))
print fs_profiles[fs_profiles['fs_flag'] == True][u'title'].value_counts()
print fs_profiles[fs_profiles['fs_flag'] == True][u'skills'][0]

skills_of_fs = fs_profiles[fs_profiles['fs_flag'] == True][u'skills']
fs_skill_words = Counter()
for index, skill_set in enumerate(skills_of_fs):
    if isinstance(skill_set, float):
        pass
    else: fs_skill_words += Counter(skill_set)

for skill_tuple in fs_skill_words.most_common(20):
    print skill_tuple
