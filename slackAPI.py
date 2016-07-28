# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from slacker import Slacker
import argparse
import datetime
import calendar
import time
import json
import os

# --- import settings
from settings import slacksettings as settings
from settings import outputformat

# --- Default Time settings
# latest : Today's 00:00 , oldest : Yesterday's 00:00
# local time, naive object
latest = datetime.date.today().strftime('%Y-%m-%d')
oldest = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

def read_argument():
    parser = argparse.ArgumentParser(description='Get Slack posts and save them to Evernote.')
    parser.add_argument('--channel', '-ch', default=settings['CHANNEL'],
                        help='Slack Channel to read. See settings.py for the default parameter.')
    parser.add_argument('--latest', '-late', default=latest,
                        help='End of time range, by date format.')
    parser.add_argument('--oldest', '-old', default=oldest,
                        help='Start of time range, by date format.')
    parser.add_argument('--format', '-f', default=settings['FORMAT'],
                        help='Output format.')
    parser.add_argument('--output', '-o',
                        help='Output filename.')
    args = parser.parse_args()

    if args.output is None:
        args.output = 'slackbackup/{}/from{}to{}.txt'.format(args.channel, args.oldest, args.latest)

    print('# CHANNEL: {}'.format(args.channel))
    print('# RANGE  : from {} to {}'.format(args.oldest, args.latest))
    print('  CAUTION! Messages in {} are not included. '
          'To be exact, "to {}" of the previous day. \n'
          '  If you want to include them, please set the next day.'
          .format(args.latest, datetime.time.max))
    print('# FORMAT : output as {} format.'.format(args.format))
    print('# OUTPUT : write to {} .'.format(args.output))

    # Make filelist (CAUTION! filelist.txt is overwritten for each time.)
    outputfilelist = open('slackbackup/filelist.txt', 'w')
    outputfilelist.write(args.output)
    outputfilelist.write('\n')
    outputfilelist.close()

    print('')
    return args


def get_history(channel_name, latest_date, oldest_date, channel_name2id, count=1000):
    # --- Get Channel History
    ## calender.timegm uses UTC. On the other hand, time.mktime uses local time zone.
    ## If you use local time zone in your slack and the environment to run this script, time.mktime is better.

    # latest_datetime = calendar.timegm(latest_date.timetuple())
    # oldest_datetime = calendar.timegm(oldest_date.timetuple())
    latest_datetime = time.mktime(latest_date.timetuple())
    oldest_datetime = time.mktime(oldest_date.timetuple())

    # If the 'channel' argument includes '#', KeyError occur.
    # In except session, channel[1:] removes first character '#'.
    try:
        channel_id = channel_name2id[channel_name]
    except KeyError:
        channel_id = channel_name2id[channel_name[1:]]

    history_json = slacker.channels.history(channel_id,
                                            latest=latest_datetime, oldest=oldest_datetime,
                                            count=count).body

    return history_json


def format_shaping(slacker, datum, format_name='simple'):
    try:
        username = slacker.users.info(datum['user']).body['user']['name']
    except KeyError:
        username = datum['username']

    text = datum['text']
    # from UNIX timestamp to datetime Object.
    dt = datetime.datetime.fromtimestamp(int(datum['ts'][0:datum['ts'].find('.')]))

    shaped_datum = outputformat[format_name].format(username, dt, text)
    print(shaped_datum, end='')

    return shaped_datum


if __name__ == "__main__":
    args = read_argument()
    slacker = Slacker(settings['API-TOKEN'])

    # Make a directory for the target channel under slackbackup/ .
    directory_for_backup = './slackbackup/{}'.format(args.channel)
    if not(os.path.exists(directory_for_backup)):
        os.makedirs(directory_for_backup)

    data = slacker.channels.list().body  # '.body' calls 'json.load'
    # print(json.dumps(data, sort_keys=True, indent=4))

    # --- dictionary for get id from name
    channel_name2id = {}
    for data in data["channels"]:
        channel_name2id.update({data["name"]: data["id"]})
    # print(channel_name2id)

    latest = datetime.datetime.strptime(args.latest, '%Y-%m-%d')
    oldest = datetime.datetime.strptime(args.oldest, '%Y-%m-%d')
    history = get_history(args.channel, latest, oldest, channel_name2id)
    # print(json.dumps(history, sort_keys=True, indent=4))

    # Format shaping and write to a file.
    outputfile = open(args.output, 'w')

    if args.format == 'pukiwiki':
        # Write pukiwiki header.
        outputfile.write("[[slack_backup]]\n"
                         "#contents\n\n"
                         )
        outputfile.write("* {} from {} to {}\n\n".format(args.channel, oldest, latest))

    for datum in history['messages'][::-1]:
        shaped = format_shaping(slacker, datum, args.format)
        outputfile.write(shaped)

    outputfile.close()

    # slacker.chat.post_message(settings['CHANNEL'], "Slack2Ever worked!")
