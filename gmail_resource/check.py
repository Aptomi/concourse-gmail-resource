#!/usr/bin/env python

# Copyright (c) 2018 Aptomi, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import sys
import common
from gmail import Gmail

def check(instream):
    input = json.load(instream)

    username = input['source']['username']
    password = input['source']['password']
    version = input.get('version')
    startUid = version.get('uid', "") if version is not None else ""

    common.msg("logging into gmail as '{0}'".format(username))
    g = Gmail()

    # login, fail if unable to authenticate
    try:
        g.login(username, password)
    except:
        common.msg("unable to log in")
        exit(1)

    # see what emails have appeared
    messages = g.inbox().mail(unread=True, prefetch=True)
    messages = sorted(messages, key=lambda m: m.sent_at)

    messages_after_start = []
    found = False
    for m in messages:
        # only consider emails after the given startUid
        if startUid == m.uid:
            found = True

        common.msg("[{0}] {1} [check = {2}]".format(m.uid, m.subject, found))
        if found:
            messages_after_start.append(m)

    # if it's the very first call, let's return the very first email
    if len(startUid) <= 0:
        messages_after_start = [messages[0]] if len(messages) > 0 else []
    else:
        # if nothing has been found, let's return the complete list
        if not found:
            messages_after_start = messages

    # return the resulting list
    result = []
    for m in messages_after_start:
        try:
            # read the corresponding email message (so we don't receive it during the next check)
            # but keep it in the mailbox and don't move anywhere, so it doesn't change uid
            m.read()
            result.append({'uid': m.uid})
        except:
            common.msg("[{0}] {1} [unable to mark message as read".format(m.uid, m.subject))
            break

    # log out and swallow the error
    try:
        g.logout()
    except:
        pass

    return result

def main():
    print(json.dumps(check(sys.stdin)))

if __name__ == '__main__':
    main()
