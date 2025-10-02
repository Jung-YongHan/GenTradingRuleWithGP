import os
from os.path import dirname, join

from flask import Flask, request, render_template

template_dir = os.path.abspath('.')
app = Flask(__name__,  template_folder=template_dir)

##https://www.tutorialspoint.com/backbonejs/backbonejs_environment_setup.htm
@app.route('/backbone', methods=['POST', 'GET'])
def backbone():
    return render_template("backbone_ex1.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        return render_template("login.html", id=id, pw=pw)
    else:
        return render_template("login.html")



@app.route('/')
@app.route('/index')
def index():
    return render_template(
                'index.html',
                title     = 'Flask Template Test',
                home_str  = 'Hello Flask!',
                home_list = [1, 2, 3, 4, 5]
            )


# @app.route('/')
# def index():
#     root_dir = dirname(dirname(dirname(__file__)))
#     # file_name = join(root_dir, f'index.html')
#     file_name = "index.html"
#     return render_template(file_name)


# http://127.0.0.1:5000/user/stkim/23123
# converter type: string(default), int, float
@app.route('/user/<user_name>/<int:user_id>')
def user(user_name, user_id):
    return f'Hello, {user_name}({user_id})!'

if __name__ == '__main__':
    # app.run('127.0.0.1', 5000, debug=True)
    app.run(debug=True)