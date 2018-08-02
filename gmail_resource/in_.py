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
import os
import errno
from gmail import Gmail

def toJSON(msg):
    return {
        "uid": msg.uid,
        "subject": msg.subject,
        "body": msg.body,
        "to": msg.to,
        "fr": msg.fr,
        "cc": msg.cc,
        "sent_at": msg.sent_at.__str__(),
        "labels": msg.labels
    }

def in_(destdir, instream):
    input = json.load(instream)

    username = input['source']['username']
    password = input['source']['password']
    version = input.get('version')
    requiredUid = version.get('uid', "") if version is not None else ""

    common.msg("logging into gmail as '{0}'".format(username))
    g = Gmail()

    # login, fail if unable to authenticate
    try:
        g.login(username, password)
    except:
        common.msg("unable to log in")
        exit(1)

    # see what emails have appeared
    common.msg("searching for email with uid '{0}'".format(requiredUid))
    messages = g.inbox().mail(unread=True, prefetch=True)
    messages = sorted(messages, key=lambda m: m.sent_at)

    msg = None
    for m in messages:
        common.msg("[{0}] {1}".format(m.uid, m.subject))

        # only consider emails with the given uid
        if requiredUid == m.uid:
            msg = m
            break

    # if we haven't found the required email message, then exit
    if msg is None:
        common.msg("unable to find email with uid '{0}'".format(requiredUid))
        exit(1)

    # put it on a file system
    common.msg("writing email '{0}' to {1}".format(msg.subject, destdir))
    with safe_open(os.path.join(destdir, "email"), 'w') as f:
        f.write(json.dumps(toJSON(msg)))

    # read and archive the corresponding email message
    msg.read()
    msg.archive()

    # log out and swallow the error
    try:
        g.logout()
    except:
        pass

    metadata = [{'name': 'uid', "value": msg.uid}, {'name': 'subject', "value": msg.subject}]
    return {'version': {'uid': msg.uid}, 'metadata': metadata}

def safe_open(path, mode):
    mkdir_p(os.path.dirname(path))
    return open(path, mode)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def main():
    print(json.dumps(in_(sys.argv[1], sys.stdin)))

if __name__ == '__main__':
    main()
