#!/usr/bin/env python

import os, re, time
from datetime import datetime, timedelta
from flask import Flask, request, g, render_template, jsonify, json

LOGDIR = 'logs'

app = Flask(__name__)
app.config.from_object(__name__)

log_re = re.compile(r'log-(\d{8}).json')

@app.route("/")
def index():
    return render_template("main.htm")

@app.route("/_get_stats")
def get_stats():
    if not 'date' in request.args:
        return jsonify(result='error', message='Required "date" argument not supplied')
    date = request.args['date']
    logfile = os.path.join(app.config['LOGDIR'], 'log-{}.json'.format(date))
    if not os.path.exists(logfile):
        return jsonify(result='error', message='No logs for selected date')
    try:
        log = json.load(open(logfile, 'r'), encoding='utf8')
    except Exception as e:
        return jsonify(result='error', message=e.message)

    result = []
    for entry in sorted(log.values(), key=lambda x: x['online'], reverse=True):
        online = timedelta(seconds=entry['online'])
        result.append((entry['name'], str(online)))

    return jsonify(result='ok', data=result)

@app.route("/_get_info")
def get_info():
    logs = sorted(os.listdir(app.config['LOGDIR']))
    first, last = logs[0], logs[-1]
    first_date = time.mktime(time.strptime(first, "log-%Y%m%d.json"))
    last_date = time.mktime(time.strptime(last, "log-%Y%m%d.json"))

    return jsonify(first=first_date, last=last_date)

if __name__ == "__main__":
    app.run(debug=True)
