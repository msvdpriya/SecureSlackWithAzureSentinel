import json
import requests
import datetime
import time
import hashlib
import hmac
import base64
import os
from slack import WebClient
from slack.errors import SlackApiError

SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
client = WebClient(token=SLACK_API_TOKEN)

# Upload slack logs to azure sentinel
# Update the customer ID to your Log Analytics workspace ID
customer_id = os.environ.get('AZURE_LOG_ANALYTICS_WORKSPACE_ID')

# For the shared key, use either the primary or the secondary Connected Sources client authentication key   
shared_key = os.environ.get('AZURE_CLIENT_AUTHENTICATION_KEY')

log_prefix = 'Slack_'
# The log type is the name of the event that is being submitted
USER_LOGS = log_prefix + 'User_Logs'
CONVERSATION_LOGS = log_prefix + 'Conversation_Logs'
ACCESS_LOGS = log_prefix + 'Access_Logs'
AUDIT_LOGS = log_prefix + 'Audit_Logs'
time_interval = 60
start_time = datetime.datetime.now() - datetime.timedelta(minutes=time_interval)
start_time = time.mktime(start_time.timetuple())

#####################
######Functions######  
#####################

# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    print(content_length)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
    else:
        print("Response code:" + str(response))
        print(response.text)

def get_users_list():
    try:
        return client.users_list()
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

def get_conversations_history(channel, start_time):
    try:
        return client.conversations_history(channel=channel, oldest=start_time)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

def list_conversations():
    try:
        return client.conversations_list()
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

def get_access_logs():
    try:
        return client.team_accessLogs()
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

def get_audit_logs():
    try:
        hed = {'Authorization': 'Bearer ' + SLACK_API_TOKEN}
        url = 'https://api.slack.com/audit/v1/logs'
        response = requests.get(url, headers=hed)
        return response
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

conversations = list_conversations()

for conversation in conversations['channels']:
    conversation_history = get_conversations_history(conversation['id'], start_time)
    messages = conversation_history['messages']
    if len(messages) > 0:
        post_data(customer_id, shared_key, json.dumps(messages), CONVERSATION_LOGS)

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

users_list = get_users_list()['members']
for user in users_list:
    if 'email' in user['profile']:
        user['email'] = user['profile']['email']
    user = removekey(user,'profile')

post_data(customer_id, shared_key, json.dumps(users_list), USER_LOGS)

access_log_list = get_access_logs()
post_data(customer_id, shared_key, json.dumps(access_log_list), ACCESS_LOGS)

audit_log_list = get_audit_logs()
post_data(customer_id, shared_key, json.dumps(audit_log_list), AUDIT_LOGS)
