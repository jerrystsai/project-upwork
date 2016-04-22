# author: Jerry Tsai
# creation date: 2016-04-20
# version 1.0
#
# PURPOSE:
# Scrape Upwork for user profiles
#
# Thanks to Greg Burek, who provided a useful decorator to rate
#   limit function calls, ideal for web scraping an API with rate limits.
#   http://blog.gregburek.com/2011/12/05/Rate-limiting-with-decorators/
#
#   I of course modify the function that is called
#

from code.web_based_app import web_based_app, RateLimited
client = web_based_app()
# @RateLimited(0.462)  # 0.462 per second or essentially every 2.16 seconds or so
#     def PrintNumber(num):
#         print num

# data = {'title':'Data Scientist', 'skills':['python', \
#     'django-framework', 'mongodb']}
#

data = {'q':'Data Scientist'}

data_list = []
page_size = 100
counter = 0
for i in xrange(2):
    provider_list = client.provider_v2.search_providers(data=data, \
        page_offset=counter, page_size=page_size)
    data_list.append(provider_list)

print data_list[0]



client.provider.get_provider('~aaa99955d3f394624e')

# data = {'q': 'python', 'title': 'Web Developer'}
# client.provider_v2.search_providers(data=data, page_offset=0, page_size=20)
