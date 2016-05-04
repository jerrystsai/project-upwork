
# coding: utf-8

# In[433]:

# author: Jerry Tsai
# program gbrt_eda.ipynb
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

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble.partial_dependence import plot_partial_dependence
import matplotlib.pyplot as plt
import numpy as np

from sklearn.cross_validation import KFold
from sklearn.metrics import mean_squared_error


# In[434]:

### MAKE PICKLES OF NEW DATAFRAMES
infile_skills_vectorized = 'data/_skills_vectorized_df.pkl'
infile_profiles = 'data/profiles_df.pkl'
infile_jobs = 'data/jobs_df.pkl'
infile_hr_paid_jobs = 'data/hr_paid_jobs_df.pkl'
infile_skills = 'data/skills_df.pkl'

hr_paid_jobs_df = pickle.load(open(infile_hr_paid_jobs, 'rb'))
sv_df = pickle.load(open(infile_skills_vectorized, 'rb'))
profiles_df = pickle.load(open(infile_profiles, 'rb'))


# ## Work up `profiles_df`

# In[435]:

profiles_df.T.head(30)


# In[473]:

profiles_usa_and_canada_ids = profiles_df[ (profiles_df['dev_country']=='United States') |                                       (profiles_df['dev_country']=='Canada') ]['dev_recno_ciphertext'].copy()


# In[441]:

profiles_usa_and_canada_ids.head()


# ## Work up `sv_df`

# In[442]:

svcopy_df = sv_df.copy()


# In[181]:

sv_df = svcopy_df.copy()


# In[182]:

# print np.array(sv_df.columns)[sums > 1000]


# In[443]:

skills_sums = np.array(sv_df.sum(axis=0))
pct_threshold = 0.5 / 100.
threshold = pct_threshold*float(len(sv_df))
insufficient_data_columns = (skills_sums < threshold)


# In[444]:

print '# of columns that will be kept: {}'.format(len(skills_sums) - np.sum(insufficient_data_columns))


# In[445]:

columns_to_drop = list(np.arange(len(skills_sums))[insufficient_data_columns])
sv_df.drop(sv_df.columns[columns_to_drop], axis=1, inplace=True)


# In[447]:

sv_df.info()


# ## Graft `sv_df` to `profiles_df` to create `profile_anly_ds`

# In[448]:

profile_anly_ds = pd.concat([profiles_df['dev_recno_ciphertext'], sv_df], axis=1)


# ## Work up `hr_paid_jobs_df`

# In[469]:

def get_number(str):
    return float(re.search(r'\d+.*\d*', str).group())

hr_paid_jobs_df['hours_as_number'] = hr_paid_jobs_df['as_total_hours_precise'].apply(get_number)
hr_paid_jobs_df['sqrt_hours'] = (hr_paid_jobs_df['hours_as_number'])**(0.5)


# In[470]:

todays_date = datetime.datetime.now().strftime('%m/%d/%Y')


# In[471]:

hr_paid_jobs_df['end_date_str'] = hr_paid_jobs_df['as_to_full'].replace({'Present': todays_date})


# In[472]:

hr_paid_jobs_df['end_date'] = pd.to_datetime(hr_paid_jobs_df['end_date_str'])


# In[474]:

hr_paid_jobs_df.drop([     'end_date_str',     'as_from_full',     'as_to_full',     'as_rate',     'as_total_charge',     'as_total_hours_precise' ], axis=1, inplace=True)


# In[476]:

hr_paid_jobs_2013_plus = hr_paid_jobs_df[hr_paid_jobs_df['end_date'] > datetime.datetime(2013, 1, 1, 0, 0, 0)].copy()


# In[477]:

hr_paid_jobs_2013_plus.drop(['end_date', 'hours_as_number'], axis=1, inplace=True)


# In[478]:

hr_paid_jobs_2013_plus.head()


# ## Create analysis data set for Questions 1 and 2 (GBRT)

# In[491]:

jobs_anly_temp = pd.merge(                         left=profile_anly_ds,                         right=hr_paid_jobs_2013_plus,                         how='inner', left_on='dev_recno_ciphertext',                         right_on='dev_recno_ciphertext'                        )


# In[492]:

jobs_anly_ds= pd.merge(                         left=pd.DataFrame(profiles_usa_and_canada_ids),                         right=jobs_anly_temp,                         how='inner', left_on='dev_recno_ciphertext',                         right_on='dev_recno_ciphertext'                        )


# In[493]:

jobs_anly_ds.info()


# ## Run GBRT models

# ### Try one GBRT model

# In[494]:

target = 'rate_as_number'
IDcol = 'dev_recno_ciphertext'
weight = 'sqrt_hours'
predictors = [x for x in jobs_anly_ds.columns if x not in [target, IDcol, weight]]

y = jobs_anly_ds.pop('rate_as_number').values
weights = jobs_anly_ds.pop('sqrt_hours').values
X = jobs_anly_ds[predictors].values


# In[495]:

with open('data/predictors.txt', 'w') as f:
    for pred in predictors:
        f.write(pred + '\n')


# In[498]:

#Choose all predictors except target & IDcols
gbm0 = GradientBoostingRegressor(random_state=8, n_estimators=1000, learning_rate=0.1)
gbm0.fit(X, y, weights)
mse = mean_squared_error(y, gbm0.predict(X), sample_weight=weights)
print mse


# In[501]:

np_predictors = np.array(predictors)
skill_set = (              (np_predictors == 'python') +              (np_predictors == 'statistics') +              (np_predictors == 'machinedashlearning')             ).reshape(1, -1)
print np.sum(skill_set)


# In[502]:

gbm0.predict(skill_set)


# In[503]:

matrix_side = len(np_predictors)
skill_set_for_all = np.repeat(skill_set, matrix_side, axis=0)
plus_one_skill = (skill_set_for_all) | (np.eye(matrix_side).astype(bool))


# In[504]:

plus_one_preds = gbm0.predict(plus_one_skill)
top_20_plus_ones = plus_one_preds.argsort()[-20:][::-1]
print plus_one_preds[top_20_plus_ones ] - gbm0.predict(skill_set)
print np_predictors[top_20_plus_ones]


# ## Optimize regression model

# In[505]:

gd_grid = {'learning_rate': [0.06, 0.04, 0.02],
           'max_depth': [4, 6],
           'min_samples_leaf': [10],
           'n_estimators': [300, 500, 800],
           'random_state': [1]}


# In[506]:

results_list_of_tuples = list()
num_folds = 3
best_result = tuple()
for item1 in gd_grid['learning_rate']:
    for item2 in gd_grid['max_depth']:
        for item3 in gd_grid['min_samples_leaf']:
            for item4 in gd_grid['n_estimators']:
                for item5 in gd_grid['random_state']:
                    instance =                       'LR {}, max_depth {}, min_samp_leaf {}, n_est {}, rs {}'.format(item1, item2, item3, item4, item5)
                    print instance
                    gbrt = GradientBoostingRegressor(random_state=item5,                                                      n_estimators=item4,                                                      min_samples_leaf=item3,                                                      max_depth=item2,                                                      learning_rate=item1                                                     )
                    kf = KFold(X.shape[0], n_folds=num_folds)
                    mse_list = []
                    for train_index, test_index in kf:
                        X_train, X_test = X[train_index], X[test_index]
                        y_train, y_test = y[train_index], y[test_index]
                        w_train, w_test = weights[train_index], weights[test_index]
                        gbrt.fit(X_train, y_train, w_train)                 
                        y_pred = gbrt.predict(X_test)
                        mse = mean_squared_error(y_test, y_pred, sample_weight=w_test)
                        mse_list.append(mse)

                    kf_mse = np.mean(np.array(mse_list))
                    results_list_of_tuples.append((instance, kf_mse))



# In[507]:

for tup in results_list_of_tuples:
    print tup


# In[508]:

gd_grid = {'learning_rate': [0.024, 0.016, 0.008],
           'max_depth': [5, 6, 8],
           'min_samples_leaf': [10],
           'n_estimators': [240, 300, 360],
           'random_state': [1]}


# In[509]:

def grid_search():
    results_list_of_tuples = list()
    num_folds = 3
    best_result = tuple()
    for item1 in gd_grid['learning_rate']:
        for item2 in gd_grid['max_depth']:
            for item3 in gd_grid['min_samples_leaf']:
                for item4 in gd_grid['n_estimators']:
                    for item5 in gd_grid['random_state']:
                        instance =                           'LR {}, max_depth {}, min_samp_leaf {}, n_est {}, rs {}'.format(item1,                                                                                           item2, item3,                                                                                           item4, item5)
                        print instance
                        gbrt = GradientBoostingRegressor(random_state=item5,                                                          n_estimators=item4,                                                          min_samples_leaf=item3,                                                          max_depth=item2,                                                          learning_rate=item1                                                         )
                        kf = KFold(X.shape[0], n_folds=num_folds)
                        mse_list = []
                        for train_index, test_index in kf:
                            X_train, X_test = X[train_index], X[test_index]
                            y_train, y_test = y[train_index], y[test_index]
                            w_train, w_test = weights[train_index], weights[test_index]
                            gbrt.fit(X_train, y_train, w_train)                 
                            y_pred = gbrt.predict(X_test)
                            mse = mean_squared_error(y_test, y_pred, sample_weight=w_test)
                            mse_list.append(mse)

                        kf_mse = np.mean(np.array(mse_list))
                        results_list_of_tuples.append((instance, kf_mse))
                        
    return results_list_of_tuples

grid_search()


# In[510]:

for tup in results_list_of_tuples:
    print tup


# In[512]:

gd_grid = {'learning_rate': [0.008, 0.004, 0.002],
           'max_depth': [6],
           'min_samples_leaf': [7, 10, 13],
           'n_estimators': [280, 300, 320],
           'random_state': [2]}


# In[513]:

def grid_search():
    results_list_of_tuples = list()
    num_folds = 3
    best_result = tuple()
    for item1 in gd_grid['learning_rate']:
        for item2 in gd_grid['max_depth']:
            for item3 in gd_grid['min_samples_leaf']:
                for item4 in gd_grid['n_estimators']:
                    for item5 in gd_grid['random_state']:
                        instance =                           'LR {}, max_depth {}, min_samp_leaf {}, n_est {}, rs {}'.format(item1,                                                                                           item2, item3,                                                                                           item4, item5)
                        print instance
                        gbrt = GradientBoostingRegressor(random_state=item5,                                                          n_estimators=item4,                                                          min_samples_leaf=item3,                                                          max_depth=item2,                                                          learning_rate=item1                                                         )
                        kf = KFold(X.shape[0], n_folds=num_folds)
                        mse_list = []
                        for train_index, test_index in kf:
                            X_train, X_test = X[train_index], X[test_index]
                            y_train, y_test = y[train_index], y[test_index]
                            w_train, w_test = weights[train_index], weights[test_index]
                            gbrt.fit(X_train, y_train, w_train)                 
                            y_pred = gbrt.predict(X_test)
                            mse = mean_squared_error(y_test, y_pred, sample_weight=w_test)
                            mse_list.append(mse)

                        kf_mse = np.mean(np.array(mse_list))
                        results_list_of_tuples.append((instance, kf_mse))
                        
    return results_list_of_tuples

print grid_search()


# In[515]:

gd_grid = {'learning_rate': [0.008, 0.007],
           'max_depth': [6],
           'min_samples_leaf': [13, 16, 21],
           'n_estimators': [300],
           'random_state': [2]}

print grid_search()

Best:
('LR 0.008, max_depth 6, min_samp_leaf 13, n_est 300, rs 2', 424.45884207251601),
# In[517]:

gbm1 = GradientBoostingRegressor(                                  learning_rate=0.008,                                  max_depth=6,                                  min_samples_leaf=13,                                  n_estimators=300,                                  random_state=3,                                 )
gbm1.fit(X, y, weights)


# In[518]:

np_predictors = np.array(predictors)
skill_set = (              (np_predictors == 'python') +              (np_predictors == 'statistics') +              (np_predictors == 'machinedashlearning')             ).reshape(1, -1)
print np.sum(skill_set)


# In[520]:

gbm1.predict(skill_set)


# In[521]:

matrix_side = len(np_predictors)
skill_set_for_all = np.repeat(skill_set, matrix_side, axis=0)
plus_one_skill = (skill_set_for_all) | (np.eye(matrix_side).astype(bool))


# In[526]:

plus_one_preds = gbm0.predict(plus_one_skill)
top_20_plus_ones = plus_one_preds.argsort()[-20:][::-1]
delta = plus_one_preds[top_20_plus_ones ] - gbm0.predict(skill_set)
print delta
print np_predictors[top_20_plus_ones]


# In[530]:

for tup in zip(delta, 100*delta/gbm1.predict(skill_set), np_predictors[top_20_plus_ones]):
    print tup


# In[ ]:

skill_set = (              (np_predictors == 'python') +              (np_predictors == 'statistics') +              (np_predictors == 'machinedashlearning')             ).reshape(1, -1)


# In[534]:

skill_set_list = [
    'python',
    'statistics',
    'machinedashlearning'
]


# In[536]:

skill_index_list = [predictors.index(skill) for skill in skill_set_list]
print skill_index_list


# In[542]:

plus_one_list = [     'datadashmining',     'bigdashdata',     'datadashscience',     'jpa' ]


# In[543]:

plus_one_index_list = [predictors.index(skill) for skill in plus_one_list]
print plus_one_index_list


# In[556]:

def distance_metric(skill_index_list, plus_one_index):
    index_array = np.array([plus_one_index] + skill_index_list)
    calc_X = X[:, index_array]
    print calc_X.shape
    only_plus_one_rows = calc_X[calc_X[:, 0] == 1,]
    distance = 1 - (np.sum(np.sum(only_plus_one_rows, axis=1) > 1)/float(only_plus_one_rows.shape[0]))
    return distance


# In[557]:

for plus_one_index in plus_one_index_list:
    print predictors[plus_one_index], distance_metric(skill_index_list, plus_one_index)


# In[ ]:



