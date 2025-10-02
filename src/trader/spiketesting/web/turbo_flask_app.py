import os
import random
import re
import sys
import time
from flask import Flask, render_template
from turbo_flask import Turbo
import threading

template_dir = os.path.abspath('.')
app = Flask(__name__,  template_folder=template_dir)
turbo = Turbo(app)

## see
## https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask

@app.route('/')
def index():
    return render_template('turbo_flask_index.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.context_processor
def inject_load():
    if sys.platform.startswith('linux'):
        with open('/proc/loadavg', 'rt') as f:
            load = f.read().split()[0:3]
    else:
        load = [int(random.random() * 100) / 100 for _ in range(3)]
    return {'load1': load[0], 'load5': load[1], 'load15': load[2]}

def update_load():
    with app.app_context():
        while True:
            time.sleep(5)
            turbo.push(turbo.replace(render_template('loadavg.html'), 'load'))  # the name of div'sid is 'load'

@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()

if __name__ == '__main__':
    # app.run('127.0.0.1', 5000, debug=True)
    app.run(debug=True)