# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import datetime
import calendar
import json
import paramiko
import codecs

from settings import pukiwikisettings as settings

def encode(filename):
    # remove extension
    filename = filename.split('.txt')[0]

    # unicode -> binary -> hex (as binary) -> unicode -> UPPER CASE
    # Python 3 cannot use str.encode('hex'), because it don't treat 'hex' as a encoding.
    encoded_name = codecs.encode(filename.encode('utf-8'), 'hex').decode('utf-8').upper() + '.txt'

    return encoded_name


def sftp_client_wiki():
    sshclient = paramiko.SSHClient()
    sshclient.load_system_host_keys()
    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    sshclient.connect(hostname=settings['HostName'], port=int(settings['Port']),
                      username=settings['User'],
                      key_filename=settings['IdentityFile']
                      )

    sftpclient = sshclient.open_sftp()

    return [sshclient, sftpclient]


if __name__=='__main__':
    [ssh, sftp] = sftp_client_wiki()

    # TODO : get filename from args. (Not only filename, but also directory name)
    filename = 'requirements.txt'

    # TODO : use loop, or make archive file and send it.
    remote_path = settings['WikiDataPath'] + encode(filename)
    print("send {} to remote {}".format(filename, remote_path))

    # send file to $PATH_TO_PUKIWIKI/wiki/
    sftp.put(filename, remote_path)

    sftp.close()
    ssh.close()