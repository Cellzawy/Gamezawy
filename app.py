from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
# import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.secret_key = "SUPER-SECRET"
# limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["3 per minute"], storage_uri="memory://")
app.config['SESSION_COOKIE_HTTPONLY'] = False

@app.route('/')
def index():
    return render_template('login.html')

# @limiter.limit("3 per minute")
# def login():

if __name__ == '__main__':
    # db.init_db(connection)
    # db.init_comments_table(connection)
    # db.seed_admin_user(connection)
    app.run(debug=True)