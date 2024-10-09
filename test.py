from get_time_table import get_time_table
from login import login
import json
import threading
from flask import Flask, request, render_template, jsonify, send_from_directory
from gevent.pywsgi import WSGIServer, WSGIHandler, LoggingLogAdapter

if __name__ == "__main__":
    session, LoginCSRFToken = login()
    time_table, BookCSRFToken, available_table = get_time_table(session)
    dic = {}
    id = 0
    for it in available_table:
        print(it.to_json())
        dic[str(id)] = it.to_json()