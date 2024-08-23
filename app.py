from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
connection = db.connect_to_database()
app.secret_key = "SUPER-SECRET"
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"], storage_uri="memory://")
app.config['SESSION_COOKIE_HTTPONLY'] = False

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['name']
        password = request.form['password']
        if not utils.is_strong_password(password):
            flash("Sorry You Entered a weak Password Please Choose a stronger one", "danger")
            return render_template('signup.html')

        if db.get_user(connection, email):
            flash("Email already exists. Please choose a different email.", "danger")
            return render_template('signup.html')

        if db.get_user_by_username(connection, username):
            flash("Username already exists. Please choose a different username.", "danger")
            return render_template('signup.html')
        
        db.add_user(connection, username, password, email)
        return redirect(url_for('login'))

    return render_template('signup.html')

# @limiter.limit("3 per minute")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db.get_user(connection, email)

        if user:
            if utils.is_password_match(password, user['password']):
                session['username'] = user['username']
                session['user_id'] = user['id']
                return render_template('login.html')
            else:
                flash("Invalid Password or Email", "danger")
                return flash("Invalid Password or Email", "danger")

        else:
            flash("Invalid Password or Email", "danger")
            return flash("Invalid Password or Email", "danger")

    return render_template('login.html')

if __name__ == '__main__':
    db.init_db(connection)
    db.seed_admin_user(connection)
    app.run(debug=True)