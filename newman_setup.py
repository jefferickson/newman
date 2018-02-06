#!/usr/bin/env python2

import os
import sys
from json import loads
import readline
from subprocess import call

from boto3 import client
from requests_oauthlib import OAuth2Session

TO_CONFIG = [(u'clientsecretfilename', 'Client Secret File Location', None),
             (u'inboxlabel', 'Inbox Label', u'INBOX'),
             (u'newmanlabel', 'Newman Label', u'Newman'),
             (u'newmancron', 'Cron Setting', u'cron(0 * * * ? *)'),
             (u'awsaccesskeyid', 'AWS Access Key ID', None),
             (u'awssecretaccesskey', 'AWS Secret Access Key', None)]
SETTINGS = {}

APPLICATION_NAME = 'Newman'
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
REDIRECT_URI = 'https://localhost'

STAGE = os.environ.get('STAGE') or 'prod'
SSM_PATH = '/{app}/{stage}/'.format(app=APPLICATION_NAME, stage=STAGE)


def prompt_user():
    print 'Welcome to {} setup!'.format(APPLICATION_NAME)
    readline.set_completer_delims('\t')
    readline.parse_and_bind('tab: complete')

    for value, name, default in TO_CONFIG:
        text = unicode(raw_input('{name} [{default}]: '.format(name=name,
                                                               default=default)))

        if text:
            SETTINGS[value] = text
        elif default is None:
            raise ValueError('{} is a required field. Please try again.'.format(name))
        else:
            SETTINGS[value] = default

    return


def write_env_vars():
    print 'Writing AWS credentials to .env...'
    with open('./.env', 'w') as f:
        f.write('export AWS_ACCESS_KEY="' + SETTINGS['awsaccesskeyid'] + '"\n')
        f.write('export AWS_SECRET_KEY="' + SETTINGS['awssecretaccesskey'] + '"\n')

    print 'Writing cron preference to vars.yml...'
    with open('./vars.yml', 'w') as f:
        f.write('newman_cron: ' + SETTINGS['newmancron'] + '\n')

    return


def parse_client_secret_file():
    secret_file = os.path.expanduser(SETTINGS['clientsecretfilename'])

    try:
        SETTINGS.update(loads(open(secret_file, 'r').read())['installed'])
        SETTINGS['redirect_uris'][1] = REDIRECT_URI
    except IOError:
        print 'Cannot find file \'{}\'. Please try again.'.format(secret_file)
        sys.exit(1)
    except KeyError:
        print 'Invalid secret file. Please try redownloading it from Google.'
        sys.exit(1)

    return


def auth_google():
    client_id = SETTINGS.get('client_id')
    client_secret = SETTINGS.get('client_secret')
    auth_base_url = SETTINGS.get('auth_uri')
    token_url = SETTINGS.get('token_uri')

    google = OAuth2Session(client_id, scope=SCOPES, redirect_uri=REDIRECT_URI)
    authorization_url, _ = google.authorization_url(auth_base_url,
                                                    access_type='offline')
    print 'Please login to your Gmail account at', authorization_url

    redirect_response = raw_input('Paste the full redirect URL here: ')

    token = google.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=redirect_response)
    SETTINGS.update(token)

    return


def store_params():
    print 'Storing into SSM...'
    ssm = client('ssm',
                 aws_access_key_id=SETTINGS['awsaccesskeyid'],
                 aws_secret_access_key=SETTINGS['awssecretaccesskey'])

    try:
        for k, v in SETTINGS.iteritems():
            if k in ('awsaccesskeyid', 'awssecretaccesskey'):
                continue
            ssm.put_parameter(Name=(SSM_PATH + '{k}').format(k=unicode(k)),
                              Description='{} config value'.format(APPLICATION_NAME),
                              Value=unicode(v),
                              Type='SecureString',
                              Overwrite=True)
    except Exception, e:
        print 'Something went wrong, sorry:', e
        sys.exit(1)

    print '... DONE'
    return


def run_deploy():
    call(['./deploy.sh'])


if __name__ == '__main__':
    prompt_user()
    write_env_vars()
    parse_client_secret_file()
    auth_google()
    store_params()
    print '{} has been configured! We are ready to deploy!'.format(APPLICATION_NAME)

    run_deploy()
    print 'Deployment complete. {} has been setup.'.format(APPLICATION_NAME)
