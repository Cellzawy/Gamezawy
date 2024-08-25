from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from markupsafe import Markup, escape


app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
connection = db.connect_to_database()
app.secret_key = "SUPER-SECRET"
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"], storage_uri="memory://")
app.config['SESSION_COOKIE_HTTPONLY'] = False

@app.route('/', methods=['GET', 'POST'])
def home():
    print(session)
    games = db.get_all_games(connection)
    if 'email' not in session:
        return render_template('index.html', user=None, games=games)
    user = db.get_user(connection, session['email'])
    return render_template('index.html', user=user, games=games)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if "email" in session :
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = escape(request.form['email'])
        username = escape(request.form['name'])
        password = escape(request.form['password'])
        if not utils.is_email_valid(email) :
            return render_template('signup.html',error_msg="Invalid Email")

        if not utils.is_strong_password(password):
            return render_template('signup.html',error_msg="Sorry You Entered a weak Password Please Choose a stronger one")
        

        if db.get_user(connection, email):
            return render_template('signup.html',error_msg="Email already exists.")

        if db.get_user_by_username(connection, username):
            return render_template('signup.html',error_msg="Username already exists.")
        
        db.add_user(connection, username, password, email)
        return redirect(url_for('login'))

    return render_template('signup.html',error_msg="")

# @limiter.limit("3 per minute")
@app.route('/login', methods=['GET', 'POST'])
def login():

    if "email" in session :
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not utils.is_email_valid(email) :
            return render_template('login.html',error_msg="Invalid Email")

        user = db.get_user(connection, email)

        if user:
            if utils.is_password_match(password, user['password']):
                session['username'] = user['username']
                session['email'] = user['email']
                session['user_id'] = user['id']
                return redirect(url_for("home"))
            else:
                return render_template('login.html',error_msg="Invalid Password or Email")

        else:
            return render_template('login.html',error_msg="Invalid Password or Email")

    return render_template('login.html',error_msg="")

@app.route('/game/<id>', methods=['GET', 'POST'])
def game_page(id):
    game = db.get_game(connection,id)
    if 'email' not in session:
        if game :
            return render_template('game_page.html', game=game, user=None)
        else :
            return "GAME NOT FOUND!", 404
    user = db.get_user(connection, session['email'])
    return render_template('game_page.html',game=game,user=user)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/info', methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        opassword = request.form['opassword']
        password = request.form['password']
        cpassword = request.form['cpassword']
        creditcard  = request.form['creditcard']

    return render_template("profile.html")

@app.route('/categories')
def categories():
    return render_template('categories.html')

if __name__ == '__main__':
    db.init_db(connection)
    db.seed_admin_user(connection)
    app.run(debug=True)