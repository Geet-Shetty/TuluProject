import os

database_scripts = os.path.dirname(__file__)
scripts = os.path.dirname(database_scripts)
data_creation = os.path.dirname(scripts)
data = os.path.join(data_creation, 'data')
# print(os.path.join(data_creation,'data','raw_html_data.txt'))