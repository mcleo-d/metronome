#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    metronome bot
'''

__author__ = 'Matt Joyce'
__email__ = 'matt.joyce@symphony.com'
__copyright__ = 'Copyright 2016, Symphony'

import datetime
import json
import logging
import sys
import symphony
import time
import uuid

# silence INFO alerts from requests module
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(filename='/var/log/metronome.log', level=logging.INFO, format='%(asctime)s %(message)s')


def get_counter():
    cachefile = open('/var/cache/metronome/counter', 'r')
    count = cachefile.read().rstrip()
    count = int(count)
    cachefile.close()
    return count


def inc_counter():
    cachefile = open('/var/cache/metronome/counter', 'r+')
    count = get_counter()
    count += 1
    cachefile.seek(0)
    count = str(count)
    cachefile.write(count)
    cachefile.close()
    return count


def main():
    ''' main program loop '''
    # run configuration
    conn = symphony.Config('/etc/metronome/metronome.cfg')
    try:
        agent, pod, symphony_sid = conn.connect()
    except Exception, err:
        print 'failed to connect to symphony: %s' % err
        sys.exit(1)
    # get datafeed
    try:
        datafeed_id = agent.create_datafeed()
        print datafeed_id
    except Exception, err:
        print 'failed to allocate datafeed id: %s' % err
        sys.exit(1)
    # msgFormat = 'TEXT'
    while True:
        # this polls and returns a list of alert ids
        try:
            # increment counter and initiate sleep cycle
            inc_counter()
            time.sleep(5)
            # accept pending connection requests
            connection_resp = pod.list_connections()
            for request in connection_resp:
                if request['status'] == 'PENDING_INCOMING':
                    pod.accept_connection(request['userId'])
            # perform user search globally
            search_filter = {"company": "Symphony Corporate"}
            local = 'false'
            search_resp, search_ret = pod.search_user('maximilian', search_filter, local)
            search_data = json.loads(search_ret)
            searched_count = search_data['count']
            searched_id = search_data['users'][0]['id']
            searched_email = search_data['users'][0]['emailAddress']
            searched_name = search_data['users'][0]['displayName']
            search_stats = '%s results found, showing first : (%s) %s - %s'\
                           % (searched_count, searched_id, searched_name, searched_email)
            # check counter
            count = get_counter()
            # build polling message
            msgFormat = 'MESSAGEML'
            message = '<messageML><b>%s ( %s )</b> <i>%s</i> \
                       %s - search maximilian - <b> %s </b> : <i> %s </i> </messageML>'\
                      % ('tick',
                         str(count),
                         datetime.datetime.now(),
                         uuid.uuid4(),
                         str(search_resp),
                         search_stats)
            # send message
            retstring = agent.send_message(symphony_sid, msgFormat, message)
            print retstring
        # if main loop fails... try to reconnect
        except Exception, err:
            try:
                datafeed_id = agent.create_datafeed()
            except:
                agent, pod, symphony_sid = conn.connect()
            logging.error("failed to run main loop: %s" % err)


if __name__ == "__main__":
    main()
