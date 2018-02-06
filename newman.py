import os
from math import floor

from boto3 import client
from requests_oauthlib import OAuth2Session

APPLICATION_NAME = 'Newman'
STAGE = os.environ.get('STAGE', 'prod')

SSM_PATH = '/{app}/{stage}/'.format(app=APPLICATION_NAME, stage=STAGE)

SETTINGS = {}


def fetch_params():
    ssm = client('ssm')
    ssm_obj = ssm.get_parameters_by_path(Path=SSM_PATH,
                                         Recursive=True,
                                         WithDecryption=True)

    params = {p['Name'].split('/')[3]: p['Value'] for p in ssm_obj['Parameters']}
    SETTINGS.update(params)

    while 'NextToken' in ssm_obj:
        ssm_obj = ssm.get_parameters_by_path(Path=SSM_PATH,
                                             Recursive=True,
                                             WithDecryption=True,
                                             NextToken=ssm_obj['NextToken'])

        params = {p['Name'].split('/')[3]: p['Value'] for p in ssm_obj['Parameters']}
        SETTINGS.update(params)

    return


def create_client():
    token = {'token_type': 'Bearer',
             'access_token': SETTINGS['access_token'],
             'refresh_token': SETTINGS['refresh_token'],
             'expires_in': SETTINGS['expires_in'],
             'expires_at': floor(float(SETTINGS['expires_at']))}

    extra = {'client_id': SETTINGS['client_id'],
             'client_secret': SETTINGS['client_secret']}

    return OAuth2Session(SETTINGS['client_id'], token=token,
                         auto_refresh_url=SETTINGS['token_uri'],
                         auto_refresh_kwargs=extra,
                         token_updater=_store_token)


def _store_token(token):
    ssm = client('ssm')
    for k, v in token.iteritems():
        ssm.put_parameter(Name=(SSM_PATH + '{k}').format(k=unicode(k)),
                          Description='{} config value'.format(APPLICATION_NAME),
                          Value=unicode(v),
                          Type='SecureString',
                          Overwrite=True)
    return


def fetch_emails(client):
    endpoint = ('https://www.googleapis.com/gmail/v1/users/me/messages?'
                'labelIds={label_id}&'
                'pageToken={page_token}')
    response = (client.get(endpoint.format(label_id=SETTINGS['newman_label_id'],
                                           page_token=''))
                      .json())

    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = (client.get(endpoint.format(label_id=SETTINGS['newman_label_id'],
                                               page_token=page_token))
                          .json())
        messages.extend(response['messages'])

    return messages


def fetch_newman_label_id(client):
    endpoint = 'https://www.googleapis.com/gmail/v1/users/me/labels'
    labels = client.get(endpoint).json()['labels']

    for label in labels:
        if label['name'] == SETTINGS['newmanlabel']:
            SETTINGS['newman_label_id'] = label['id']
            break
    else:
        raise ValueError('Error: Are you sure you created the label {} in Gmail?'
                         .format(SETTINGS['newmanlabel']))


def move_to_inbox(client, emails):
    endpoint = 'https://www.googleapis.com/gmail/v1/users/me/messages/batchModify'
    batch_body = {'ids': [email['id'] for email in emails],
                  'addLabelIds': [SETTINGS['inboxlabel']],
                  'removeLabelIds': [SETTINGS['newman_label_id']]}

    if batch_body['ids']:
        print 'Moving {n} email(s) to {inbox}.'.format(n=len(batch_body['ids']),
                                                       inbox=SETTINGS['inboxlabel'])
        client.post(endpoint, json=batch_body)

    return


def handler(_, __):
    fetch_params()
    client = create_client()
    fetch_newman_label_id(client)
    move_to_inbox(client, fetch_emails(client))


if __name__ == '__main__':
    handler(None, None)
