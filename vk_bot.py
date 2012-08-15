#!/usr/bin/env python

from __future__ import unicode_literals, print_function

import os, sys, logging, getpass, signal
import json, time, argparse
from copy import deepcopy

logger = logging.getLogger('VkBot')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
ch = logging.StreamHandler()
ch.setFormatter(fmt)
logger.addHandler(ch)

#SleekXMPP logger configuration
sleeklogger = logging.getLogger('sleekxmpp')
sleeklogger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(fmt)
ch.setLevel(logging.INFO)
fh = logging.FileHandler('vk_bot.debug', 'w')
fh.setFormatter(fmt)
sleeklogger.addHandler(ch)
sleeklogger.addHandler(fh)

try:
    from gevent.monkey import patch_socket
    patch_socket()
except ImportError:
    pass

import sleekxmpp

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

class VkBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, log_dir):
        super(VkBot, self).__init__(jid, password)

        self.log_dir = log_dir
        self.logfile = os.path.join(log_dir, 'log-{}.json'.format(
            time.strftime('%Y%m%d')))
        self.load_log_file()

        self.register_plugin('xep_0199') #Enable pings

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('got_online', self.log_enter)
        self.add_event_handler('got_offline', self.log_leave)
        self.add_event_handler('disconnected', self.dump_log)

        signal.signal(signal.SIGHUP, self.rotate)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        logger.info('Started')

    def load_log_file(self):
        self.log = {}
        if os.path.exists(self.logfile):
            try:
                self.log = json.load(open(self.logfile), encoding='utf-8')
            except Exception as e:
                logger.warning('Malformed log file {}: {}'.format(self.logfile, e.message))

    def dump_log(self, event=None):
        try:
            #Make copy to save master log from spoiling
            log = deepcopy(self.log)
            if event is not None:
                for entry in log.values():
                    #Mark all entries as offline if we are closing
                    entry['last_leave'] = time.time()
                    entry['online'] += entry['last_leave'] - entry['last_enter']
                    entry['status'] = 'offline'
            json.dump(log, open(self.logfile, 'w'), encoding='utf-8')
        except Exception as e:
            logger.warning('Could not dump log to {}: {}'.format(self.logfile, e.message))

    def log_enter(self, presence):
        jid = presence['from']
        name = self.client_roster[jid]['name']
        logger.info('Logged enter of {}'.format(name))

        jid = str(jid)

        if not jid in self.log:
            entry = {}
            entry['name'] = name
            entry['last_leave'] = 0
            entry['last_enter'] = time.time()
            entry['online'] = 0
            entry['status'] = 'online'
            self.log[jid] = entry
        else:
            self.log[jid]['last_enter'] = time.time()
            self.log[jid]['status'] = 'online'

        self.dump_log()

    def log_leave(self, presence):
        jid = presence['from']
        name = self.client_roster[jid]['name']
        logger.info('Logged leave of {}'.format(name))

        jid = str(jid)

        if not jid in self.log:
            logger.warning('Left jid {}({}) was not logged entering'.format(jid, name))
            return

        self.log[jid]['last_leave'] = time.time()
        self.log[jid]['online'] += self.log[jid]['last_leave'] - self.log[jid]['last_enter']
        self.log[jid]['status'] = 'offline'

        self.dump_log()

    def rotate(self, signum, frame):
        self.dump_log(1) #Write full log, as we are stopping

        cur_time = time.time()
        new_log = {}
        for jid, entry in self.log.items():
            if entry['status'] == 'online':
                entry['online'] += cur_time - entry['last_enter']
                entry['last_enter'] = cur_time
                new_log[jid] = entry
                logger.debug('Online while rotating: {}'.format(entry['name']))
        self.log = new_log

        self.logfile = os.path.join(self.log_dir, 'log-{}.json'.format(
            time.strftime('%Y%m%d')))
        logger.info('Rotated log file, new log: {}'.format(self.logfile))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vkontakte bot')
    parser.add_argument('--logdir', help='Directory for storing logs', default='logs')
    args = parser.parse_args()

    vk_id = raw_input('Vk id: ')
    vk_pass = getpass.getpass('Password: ')

    xmpp = VkBot('{}@vk.com'.format(vk_id), vk_pass, args.logdir)
    if xmpp.connect():
        xmpp.process(block=True)
    else:
        logger.error("Unable to connect!")
