#!/usr/bin/env python

import sqlite3, json, time, re
from datetime import datetime
import os

log_file_re = re.compile(r"log.json-(\d{4}-\d{2}-\d{2})")

conn = sqlite3.connect("logs.db")
cursor = conn.cursor()

seen_jids = []

for log_file in sorted(os.listdir("logs")):
    match = log_file_re.match(log_file)
    if not match:
        continue
    log_date = datetime.strptime(match.group(1), "%Y-%m-%d")
    log_json = json.load(open(os.path.join("logs", log_file), "r"), encoding="utf-8")
    for record in log_json:
        online = datetime.strptime(record["online"].split(".")[0], "%H:%M:%S")
        cursor.execute("INSERT INTO logs (jid, date, online) VALUES (?, ?, ?)",
                       (record["jid"], log_date, online))
        jid_pair = (record["jid"], unicode(record["name"]))
        if not jid_pair in seen_jids:
            cursor.execute("INSERT INTO jids (jid, name) VALUES (?, ?)",
                           jid_pair)
            seen_jids.append(jid_pair)

conn.commit()
conn.close()
