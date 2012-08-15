#!/usr/bin/env python

from __future__ import unicode_literals, print_function

import os, sys, json, argparse, time, logging
from datetime import timedelta

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

parser = argparse.ArgumentParser(description='Vk bot simple log analyzer')
parser.add_argument('--logdir', help='Directory with Vk bot logs', default='logs')
parser.add_argument('--date', help='Log date', default=time.strftime('%Y%m%d'))
parser.add_argument('--file', help='Log file to use', required=False)

args = parser.parse_args()

if args.file:
    logfile = args.file
else:
    logfile = os.path.join(args.logdir, 'log-{}.json'.format(args.date))

if not os.path.exists(logfile):
    logging.error('Log file {} does not exist'.format(logfile))
    sys.exit(1)

try:
    log = json.load(open(logfile), encoding='utf-8')
except Exception as e:
    logging.error('Malformed log file {}: {}'.format(logfile, e.message))
    sys.exit(1)

for entry in log.values():
    #Calculate total online time for currently online entries
    if entry['status'] == 'online':
        entry['online'] += time.time() - entry['last_enter']

for entry in sorted(log.values(), key=lambda x: x['online'], reverse=True):
    print ('{:30} {}\t{}'.format(
                                entry['name'],
                                timedelta(seconds=int(entry['online'])),
                                entry['status']))
