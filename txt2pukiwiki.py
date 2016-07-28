# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import glob
import paramiko
import codecs

# --- import settings
from settings import pukiwikisettings as settings


def read_arguments():
    parser = argparse.ArgumentParser(description='Sending text files to pukiwiki server and make new page.')
    parser.add_argument('filename', nargs='*',
                        help='Names of text files to be transfer (pukiwiki format is recommended).')
    parser.add_argument('--filelist', '-l',
                        help='Using this option instead of writing each file name, '
                             'this program imports a list of filename from a ".txt" file.')
    args = parser.parse_args()

    # --- Get files to be send, as a name list.
    filelist = []

    if args.filename == [] and args.filelist is None:
        raise ValueError("Please tell this program at least one filename to be send!")

    # Manage wild cards in filename
    for argument in args.filename:
        filenames = glob.glob(argument)
        for item in filenames:
            filelist.append(item)

    if args.filelist is not None:
        filelist_from_listfile = open(args.filelist, 'r')
        items = filelist_from_listfile.readlines()
        for item in items:
            # Remove newline characters.
            item = item.rstrip('\n').rstrip('\r\n')
            if item != '':
                filelist.append(item)

    return [args, filelist]


# --- encode a filename for pukiwiki page data (<hex>.txt).
def encode(filename):
    # remove extension
    filename = filename.split('.txt')[0]

    # unicode -> binary -> hex (as binary) -> unicode -> UPPER CASE
    # Python 3 cannot use str.encode('hex'), because it don't treat 'hex' as a encoding.
    encoded_name = codecs.encode(filename.encode('utf-8'), 'hex').decode('utf-8').upper() + '.txt'

    return encoded_name


# --- Make SFTP client for pukiwiki server
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


# --- Main function of this python program
def main(target_file_list):
    print('# Target File: {}'.format(target_file_list))

    if not target_file_list:
        print("Please tell this program at least one filename to be send!")
        return -1

    [ssh, sftp] = sftp_client_wiki()

    for filename in target_file_list:
        remote_path = settings['WikiDataPath'] + encode(filename)
        print("send {} to remote {}".format(filename, remote_path))

        # send the file to $PATH_TO_PUKIWIKI/wiki/
        sftp.put(filename, remote_path)

    sftp.close()
    ssh.close()

    return


if __name__=='__main__':
    main(read_arguments()[1])
