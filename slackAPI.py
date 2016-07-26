# -*- coding: utf-8 -*-
from __future__ import print_function
from slacker import Slacker
import argparse
import datetime
import calendar
import json

# --- import settings
from settings import settings

# --- Default Time settings
# latest : Today's 00:00 , oldest : Yesterday's 00:00
# local time, naive object
latest = datetime.date.today()
oldest = datetime.date.today() - datetime.timedelta(days=1)


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
    args = parser.parse_args()

    print('# CHANNEL: {}'.format(args.channel))
    print('# RANGE  : from {} to {}'.format(args.oldest, args.latest))
    print('  CAUTION! Messages in {} are not included. '
          'To be exact, "to {}" of the previous day. \n'
          '  If you want to include them, please set the next day.'
          .format(args.latest, datetime.time.max))

    print('')
    return args


def get_history(channel_name, latest_date, oldest_date, channel_name2id, count=1000):
    # --- Get Channel History
    latest_datetime = calendar.timegm(latest_date.timetuple())
    oldest_datetime = calendar.timegm(oldest_date.timetuple())

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


def format_shaping(slacker, datum, format='simple'):
    try:
        username = slacker.users.info(datum['user']).body['user']['name']
    except KeyError:
        username = datum['username']

    text = datum['text']
    # from UNIX timestamp to datetime Object.
    dt = datetime.datetime.fromtimestamp(int(datum['ts'][0:datum['ts'].find('.')]))

    print("{:15}  {}\n\t{}".format(username, dt, text))


if __name__ == "__main__":
    args = read_argument()
    slacker = Slacker(settings['API-TOKEN'])

    data = slacker.channels.list().body  # '.body' calls 'json.load'

    # --- dictionary for get id from name
    channel_name2id = {}
    for data in data["channels"]:
        channel_name2id.update({data["name"]: data["id"]})

    history = get_history(settings["CHANNEL"], args.latest, args.oldest, channel_name2id)
    # print(json.dumps(history, sort_keys=True, indent=4))

    for datum in history['messages'][::-1]:
        format_shaping(slacker, datum)

    slacker.chat.post_message(settings['CHANNEL'], "Slack2Ever worked!")
