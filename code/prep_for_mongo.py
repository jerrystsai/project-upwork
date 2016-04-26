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

#     now, load it into pandas
#     out_df = pd.read_json(data_json_str)
    return data_list_of_dicts

list_of_filenames = os.listdir(os.getcwd()+'/data/profiles_by_skill')

for filename in list_of_filenames:
    if filename[-4:] == '.txt':
        skill_name = filename.split('.')[0]
        skill_name = skill_name.replace('-', '_')
        skill_name = skill_name.replace('#', 'Sharp')
        print skill_name

as_profiles_lod = json_prep('../data/apache-spark.txt')


# In[41]:

print len(as_profiles_lod), type(as_profiles_lod)  # it's a list of dicts


# ## Insert into MongoDB

# In[18]:

client = MongoClient()
# Access/Initiate Database
db = client['upwork_db']


# In[42]:

db.collection_names()


# In[43]:

# Access/Initiate Table
profiles = db['apache-spark_profiles']


# In[44]:

profiles.insert_many(as_profiles_lod)


# In[45]:

db.collection_names()


# In[47]:

db[u'apache-spark_profiles'].count()


# In[46]:

db[u'apache-spark_profiles'].find_one()


# In[27]:

# Deletes collection (table)
db['test_table'].drop()


# In[28]:

db.collection_names()


# In[26]:

list(tab.find())


# In[17]:

client.close()


# In[ ]:
