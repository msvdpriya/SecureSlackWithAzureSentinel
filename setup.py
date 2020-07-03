import os
import pwd

#install all requirements
print('[SecureSlackWithAzureSentinel] installing requirements')
with open('requirements.txt') as REQUIREMENTS:
    REQS_TO_INSTALL = REQUIREMENTS.read().split('\n')

for REQ in REQS_TO_INSTALL:
    os.system('pip3 install '+ REQ)
print('[SecureSlackWithAzureSentinel] requirements installed')

def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]

# Variables

CRONTAB_INTERVAL_IN_MINUTES = 1
USER_NAME = get_username()

# if you want to setup crontab under different username
# un-comment the below line and specify username
# USER_NAME = ''

# setup crontab
from crontab import CronTab

my_cron = CronTab(user=USER_NAME)
job = my_cron.new(command='source '+ os.getcwd() +'/credentials.sh;/Library/Frameworks/Python.framework/Versions/3.7/bin/python3 '+ os.getcwd() +'/app.py')
job.minute.every(CRONTAB_INTERVAL_IN_MINUTES)
my_cron.write()
print('[SecureSlackWithAzureSentinel] Log Agent has been setup on your machine as crontab')
print('[SecureSlackWithAzureSentinel] Log Agent will run on your machine every ' + str(CRONTAB_INTERVAL_IN_MINUTES) + ' minutes')



