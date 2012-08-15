#!/usr/bin/env python

import os, re, json, time
from datetime import datetime

log_file_re = re.compile(r"log.json-(\d{4}-\d{2}-\d{2})")

epoch = datetime(1970, 1, 1)

for log_file in sorted(os.listdir("oldlogs")):
    match = log_file_re.match(log_file)
    if not match:
        continue
    log_date = match.group(1).replace("-", "")
    try:
        log_json = json.load(open(os.path.join("oldlogs", log_file), "r"), encoding="utf-8")
    except:
        print "Skipped", log_date
        continue
    new_log = {}
    for record in log_json:
        jid = record["jid"]
        del record["jid"]
        online = time.strptime(record["online"].split(".")[0], "%H:%M:%S")
        online = online.tm_hour * 3600 + online.tm_min * 60 + online.tm_sec
        record["online"] = online
        new_log[jid] = record
    json.dump(new_log, open(os.path.join("logs", "log-{}.json".format(log_date)), "w"), encoding="utf-8")
    print "Processed ", log_date
