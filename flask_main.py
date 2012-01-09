#!/usr/bin/env python

import sqlite3
from flask import Flask, request, g, render_template, jsonify, json

DATABASE = "logs.db"

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/")
def index():
    return render_template("main.htm")

@app.route("/_get_jids")
def get_jids():
    db_jids = map(lambda x: x[0], g.db.execute("SELECT DISTINCT jid FROM jids"))
    jids = {}
    for jid in db_jids:
        names = map(lambda x: x[0], g.db.execute("SELECT name from jids WHERE jid = ?", (jid,)))
        jids[jid] = names

    return jsonify(jids)

@app.route("/_get_stats", methods=['POST'])
def get_stats():
    json_request = json.loads(request.form["request"], encoding="utf-8")
    stats = {}
    jids = {}
    if "jids" in json_request:
        jids_placeholder = ",".join("?" * len(json_request["jids"]))
        records = g.db.execute("SELECT date, jid, online FROM logs WHERE \
                                jid in ({}) AND online != \"1900-01-01 00:00:00\" \
                                ORDER BY date, online DESC".format(jids_placeholder),
                                json_request["jids"])
        #Make {date: [list of (jid, online)]}
        for date, jid, online in records:
            date = date.split()[0] #Remove 00:00:00 time component
            online = online.split()[1] #Remove 1900-01-01 date component
            stats.setdefault(date, []).append((jid, online))
        jids_r = g.db.execute("SELECT jid, name FROM jids WHERE jid in ({})".format(jids_placeholder), json_request["jids"])
        #Make {jid: [list of names]}
        for jid, name in jids_r:
            jids.setdefault(jid, []).append(name)

        #Return stats as [(date, (jid, online))] list of tuples
        return jsonify(stats=sorted(stats.items()), jids=jids)
if __name__ == "__main__":
    app.run(debug=True)
