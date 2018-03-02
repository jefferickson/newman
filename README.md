Newman
================

Batch your Gmail.

![Newman](https://www.factinate.com/wp-content/uploads/2017/02/Newman-4.jpg)

### What does it do?

Newman allows you to reduce your daily distractions by delivering your emails in batches at times you specify. Just like the old days before push notifications when you had to log onto your email service to get your emails at times you controlled.

### Requirements

1. A Google account
1. An AWS account (Lambda, S3, and SSM)
1. Docker
1. Python 2
1. Python libraries installed: `boto` and `request_oauthlib`

### Setup Google

1. Go to [Google Developers Console](https://console.developers.google.com)
1. Create a new project called `Newman`
1. Enable the Gmail API in the Newman project
1. Click Credentials on the left navbar, and then select the OAuth Consent Screen tab
1. Select your email, and enter `Newman` as the product name. Click Save
1. Click on the Create Credentials dropdown and select OAuth Client ID
1. Select application type Other and name the service `Newman`
1. Google will display your credentials. Click OK and then download the JSON version of the credentials. This is your client secret file

### Setup AWS

Get your AWS keys ([instructions here](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)). We recommend setting up a user for Newman first.

### Setup Gmail

1. Create a new filter (Settings -> Filters and Blocked Addresses -> Create a new filter)
1. Put `*` into the From box. You want a filter that will cause all incoming emails to skip your inbox
   1. You can cause certain high-priority senders' emails to arrive immediately by _excluding_ them from this filter. For example: `* -important_sender@email.com -another_important_sender@gmail.com`
1. Put `label:inbox` into the Has the words box. This will make the filter only apply to incoming emails
1. Click Continue, confirming when prompted
1. Select the following options:
   1. Skip the Inbox (Archive it)
   1. Apply the label -> New label... -> Create a new label called `Newman`

All of your incoming emails will now skip the inbox and be tagged with the label. You can always see them by clicking the Newman label on the left navbar in Gmail.

### Setup and Deploy Newman

1. Open your terminal
1. If you do not already have them installed, install both `boto` and `request_oauthlib` Python libraries using `pip`
1. Clone the Newman repo: `git clone https://github.com/jefferickson/newman.git`
1. Run the Newman setup and deploy script from the `newman` directory: `cd newman; newman/newman_setup.py`. You will have to specify the following options or accept the defaults where possible:
   1. Client Secret File Location [Required]: This is the file you downloaded from the Google Developers Console
   1. Inbox Label: The label name of your Inbox in Gmail.
   1. Newman Label: The label name you created in the filter above.
   1. Cron Setting: The default is at the top of the hour. Any valid AWS cron is valid here (both `cron()` and `rate()` syntax)
   1. AWS Access Key ID [Required]: The access key ID for your AWS user
   1. AWS Secret Access Key [Required]: The secret access key for your AWS user
1. You will then be prompted with a URL. Copy and paste it into your web browser and log into your Gmail account. Allow Newman to access your account
1. You will then be redirected to a localhost URL that probably doesn't resolve. Copy and paste this URL (starts with `https://localhost`) from your browser back into the setup script at the prompt
1. Newman will now:
   1. Store your OAuth tokens into SSM
   1. Start a docker image to deploy the stack to your AWS account. This may take awhile the first time you run it
1. If you ever want to make changes (to the cron, for example), just rerun the setup script

That's it!
