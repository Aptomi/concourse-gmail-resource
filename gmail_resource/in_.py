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
from gmail import Gmail, Message

def toJSON(msg):
    return {
        "uid": msg.uid,
        "subject": msg.subject,
        "body": msg.html,
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
    uid = version.get('uid', "") if version is not None else ""

    common.msg("logging into gmail as '{0}'".format(username))
    g = Gmail()

    # login, fail if unable to authenticate
    try:
        g.login(username, password)
    except:
        common.msg("unable to log in")
        exit(1)

    # fetch this particular email
    common.msg("fetching email with uid '{0}'".format(uid))
    msg = g.fetch_multiple_messages({uid: Message(g.inbox(), uid)})[uid]

    # if we haven't found the required email message, then exit
    if msg is None or msg.message is None:
        common.msg("unable to find email with uid '{0}'".format(uid))
        exit(1)

    # put it on a file system
    common.msg("writing email '{0}' to {1}".format(msg.subject, destdir))
    with safe_open(os.path.join(destdir, "email"), 'w') as f:
        f.write(json.dumps(toJSON(msg)))

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
