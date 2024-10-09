from get_time_table import get_time_table
from login import login
import json
import threading
from flask import Flask, request, render_template, jsonify, send_from_directory
from gevent.pywsgi import WSGIServer, WSGIHandler, LoggingLogAdapter

import urllib3
from urllib3.exceptions import InsecureRequestWarning
app = Flask(__name__)
@app.route('/api',methods=['GET','POST'])
def run():
    urllib3.disable_warnings(InsecureRequestWarning)
    session, LoginCSRFToken = login()
    time_table, BookCSRFToken, available_table = get_time_table(session)
    dic = {}
    id = 0
    #print(available_table)
    for it in available_table:
        #print(it.to_json())
        dic[str(id)] = it.to_json()
        id = id + 1
    return jsonify(dic)
        

if __name__ == "__main__":
    http_server = None
    address = r'127.0.0.1:9999'
    try:
        host = address.split(':')
        http_server = WSGIServer((host[0], int(host[1])), app, handler_class=WSGIHandler)
        print(f'HTTP server starts on {address}')
        http_server.serve_forever()
    except Exception as e:
        if http_server:
            http_server.stop()
        print("error:" + str(e))
        app.logger.error(f"[app]start error:{str(e)}")
    finally:
        if http_server:
            http_server.stop()
