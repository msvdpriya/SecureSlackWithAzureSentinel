# Protect Slack With Azure Sentinel

Many organisations use Slack for secure collaboration across teams, departments, offices and countries. Azure Sentinel can be used by security teams at these organizations to secure and monitor Slack. "Protect Slack With Azure Sentinel" enables you to Secure and Monitor Slack using Azure Sentinel. We have developed a solution to collect logs from Slack via the Slack API. 

## Inspiration

Many organisations use Slack for secure collaboration across teams, departments, offices and countries. **Azure Sentinel** can be used by security teams at these organizations to secure and monitor Slack.

## What it does

One of the great features of Azure Sentinel is its ability to ingest and analyze data from any source not just from Microsoft products. Our project is an end-to-end solution to enable enterprises that use slack onboard to Azure Sentinel.

Our Project is made up of:
- Log Agent
- Azure Sentinel Detections and Hunting Queries

Log Agent collects logs from Slack and ingests them into **Azure Sentinel Log Analytics WorkSpace**. Setup script deploys Log Agent as a Cron Job that runs at intervals defined by the user. You can also setup the Log agent in Azure VM. On Windows machine, you can run setup the file 'setup.py' as a scheduled task.

After the data is available in **Azure Sentinel Log Analytics WorkSpace**, cybersecurity experts at companies that use slack can use Detections and Hunting Queries to monitor Slack activity.

## Architecture
![Architecture](/architecture.png)

## How we built it

Log Agent is built using Python. Azure Sentinel is used for Detections and Hunting Queries.

## Steps to Secure Slack with Azure Sentinel:

**Step 1**: Create a Slack API token for log collection

This section demonstrates how to generate a Slack API token for all types of Slack plans, and is organized based on the type of Slack plan and log type. Identify your Slack plan and generate the Slack API token, as described in the following steps.

If you are on any plan other than the 'Slack Enterprise Grid', follow only the steps mentioned below to generate a Slack API token. Slack Enterprise plan users need to generate an additional token as mentioned in the next section.

1. Go to Apps page.
2. Click Create New App.
3. Enter the App Name and select the Development Slack Workspace for which you need to generate a token and collect logs.
4. Click Create App.
5. In the Basic Information section for the app created above, click Permissions.
6. In the Scopes section, add the following permissions to collect logs, and then click Save. Logs will be collected based on these permissions:
- admin
- channels:read
- channels:history
- Users:read
- users:read.email
- team:read
7. Go to Install App and click Install App to Workspace.
8. Click Allow to install the app to workspace.
9. Copy the generated token. You will need to use this token when configuring the **SecureSlackWithAzureSentinel** Log Agent.

(Optional) If you are on the 'Slack Enterprise Grid', use the steps below to generate a Slack API token. This Slack API token will be used for audit logs:

NOTE: You must have owner privileges to perform this task.

1. For the Slack app you created in Users, channels and access logs, Go To OAuth and Permission.
2. Go to Redirect URLs and add a Redirect URL as http://localhost, then click Save URLs.
3. Go To Manage Distribution > Share Your App with Other Workspaces
4. Open the Remove Hard Coded Information section on the same page and check the I’ve reviewed and removed any hard-coded information checkbox.
5. Click the Activate Public Distribution.
6. Copy the Shareable URL and append auditlogs:read at the end. Such as in the following example:
```
https://slack.com/oauth/authorize?client_id=12349876.993599993397&scope=admin,channels:history,channels:read,team:read,users:read,users:read.email,auditlogs:read
```
7. Open a new tab in your browser, paste the modified URL and press Enter.
8. Select the drop-down menu in the upper right corner and choose the correct organization.
9. Click Allow.
10. Ignore the error message and copy the Code in the URL field, as shown in the following example.
11. Get the client ID and client secret from the Basic information of your Slack app. Replace the CODE, CLIENT_ID and CLIENT_SECRET variables in the following URL.
  
```
https://slack.com/api/oauth.access?code=<CODE>&client_id=<CLIENT_ID>&client_secret=<CLIENT_SECRET>
```
12. Open a new browser tab and paste the URL from the previous step into the URL field, then press Enter.
13. From the response, copy the token value from the field access_token.
  
**Step 2**: Create **Azure Sentinel WorkSpace** and get the credentials(AZURE_LOG_ANALYTICS_WORKSPACE_ID and AZURE_CLIENT_AUTHENTICATION_KEY).

**Step 3**: Clone repository **'SecureSlackWithAzureSentinel'** using the following git command:

```
git clone https://github.com/msvdpriya/SecureSlackWithAzureSentinel.git
```

**Step 4**: Configure Credentials that you got in Step 1 and Step 2 in the credentials.sh file. Edit the following variables in the file and set the credentials as their values:
- SLACK_API_TOKEN
- AZURE_LOG_ANALYTICS_WORKSPACE_ID
- AZURE_CLIENT_AUTHENTICATION_KEY

**Step 5**: Run setup.py (This step will setup **Log Agent**)

```
NOTE: python and pip3 are prerequisites to run the setup.py file. All other requirements will be downloaded when you run setup.py file.
```

This step will also configure crontab in your machine that will run the app.py script(Log Agent) periodically to fetch logs from Slack API and upload it to **Azure Sentinel Log Analytics workspace**. You can also setup the Log agent in Azure VM. On Windows machine, you can run setup the file 'setup.py' as a scheduled task.

**Step 6**: Verify that the logs are being pushed to **Azure Sentinel Log Analytics Workspace**. 
**Step 7**. Use the KQL queries that are present in detections and hunting folders of the project to detect and hunt for cybersecurity threats on **Azure Sentinel**.
