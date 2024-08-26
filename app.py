import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
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
    if not 'cart' in session :
        session['cart'] = []
    games = db.get_all_games(connection)
    if "email" in session :
        if session['email'] == "admin@gmail.com":
            return redirect(url_for('admin_add_game'))
    else:
        return render_template('index.html', user=None, games=games)
    user = db.get_user(connection, session['email'])
    return render_template('index.html', user=user, games=games)


@app.route('/add-money', methods=['GET', 'POST'])
def add_money():
    games = db.get_all_games(connection)
    if 'email' not in session:
        return render_template('index.html', user=None, games=games)
    user = db.get_user(connection, session['email'])
    return render_template('add-money.html')

@app.route('/add-funds', methods=['GET', 'POST'])
def add_funds():
    games = db.get_all_games(connection)
    if 'email' not in session:
        return render_template('index.html', user=None, games=games)
    else:
        if request.method == 'POST':
            data = request.get_json()
            user_email = session['email']
            new_funds = data['amount']
            print(data)
            # db.update_user_funds(connection, user_email, new_funds)
            return jsonify({'message': 'Funds updated successfully'})
        else:
            return render_template('add-money.html', message="Successfully added ")


@app.route('/library', methods=['GET', 'POST'])
def library():
    if "email" in session :
        if session['email'] == "admin@gmail.com":
            return redirect(url_for('admin_add_game'))
    else:
        return render_template('login.html',error_msg="")
    user = db.get_user(connection, session['email'])
    games = db.get_user_games(connection, user['id'])
    return render_template('library.html', user=user, games=games)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if "email" in session :
        if session['email'] == "admin@gmail.com":
            return redirect(url_for('admin_add_game'))
        else:
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

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def login():
    if "email" in session :
        if session['email'] == "admin@gmail.com":
            return redirect(url_for('admin_add_game'))
        else:
            return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not utils.is_email_valid(email) :
            return render_template('login.html',error_msg="Invalid Email")

        user = db.get_user(connection, email)

        if user["email"] == "admin@gmail.com" and utils.is_password_match(password ,user["password"]) :
            session['username'] = user["username"]
            session['email'] = user["email"]
            return redirect(url_for('admin_add_game'))

        if user:
            if utils.is_password_match(password, user['password']):
                session['username'] = user['username']
                session['email'] = user['email']
                session['user_id'] = user['id']
                return redirect(url_for("home"))
            else:
                return render_template('login.html',error_msg="Invalid Password or Email")

        else:
            return render_template('login.html',error_msg="Email Doesn't Exist")

    return render_template('login.html',error_msg="")

@app.route('/add_to_cart/<id>', methods=['GET', 'POST'])
def add_to_cart(id):
    game = db.get_game(connection, id)

    if "email" not in session:
        return redirect(url_for('login'))

    if session['email'] == "admin@gmail.com":
        return redirect(url_for('admin_add_game'))
    
    user = db.get_user(connection, session['email'])

    if not db.is_game_in_cart(connection,id,user["id"]):
        db.add_game_to_cart(connection,id,user["id"])

    return redirect(url_for('game_page', id=game['id']))

@app.route('/remove_from_cart/<id>', methods=['GET', 'POST'])
def remove_from_cart(id):
    game = db.get_game(connection, id)

    if "email" not in session:
        return redirect(url_for('login'))

    if session['email'] == "admin@gmail.com":
        return redirect(url_for('admin_add_game'))
    
    user = db.get_user(connection, session['email'])

    if db.is_game_in_cart(connection,id,user["id"]):
        db.remove_game_from_cart(connection,id,user["id"])

    return redirect(url_for('game_page', id=game['id']))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if "email" in session :
        if session['email'] == "admin@gmail.com":
            return redirect(url_for('admin_add_game'))
    else:
        return redirect(url_for('login'))
    user = db.get_user(connection, session['email'])
    games= db.get_user_cart(connection, user['id'])
    total_price = 0
    for game in games:
        total_price += game['price']
    return render_template("cart.html", user=user, games=games,total_price=round(total_price, 2))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if "email" not in session:
        return redirect(url_for('login'))

    if session['email'] == "admin@gmail.com":
        return redirect(url_for('admin_add_game'))
    user = db.get_user(connection, session['email'])
    games= db.get_user_cart(connection, user['id'])

    total_price = 0
    for game in games:
        total_price += game['price']

    if(user['balance'] >= total_price) :
        db.add_games_to_library(connection,user['id'],total_price,games)
        db.remove_games_from_cart(connection,user['id'])
        db.update_user_balance(connection,user['id'],total_price)
    else:
        return render_template("cart.html", user=user, games=games,total_price=round(total_price, 2))
    return redirect(url_for('library'))

@app.route('/game/<id>', methods=['GET', 'POST'])
def game_page(id):
    game = db.get_game(connection,id)
    if "email" in session :
        if session['email'] == "admin@gmail.com":
            return redirect(url_for('admin_add_game'))
    else:
        if game :
            return render_template('game_page.html', game=game, user=None, in_library=db.is_game_in_library(connection), in_cart=db.is_game_in_cart(connection))
        else :
            return "GAME NOT FOUND!", 404
    user = db.get_user(connection, session['email'])
    return render_template('game_page.html',game=game,user=user, in_library=db.is_game_in_library(connection, game['id'], user['id']), in_cart=db.is_game_in_cart(connection, game['id'], user['id']))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    session.pop('user_id', None)
    session.pop('cart', None)
    return redirect(url_for('login'))

@app.route('/info', methods=['GET', 'POST'])
def info():
    games = db.get_all_games(connection)
    if "email" in session :
        if session['email'] == "admin@gmail.com":
            return redirect(url_for('admin_add_game'))
    else:
        return render_template('index.html', user=None, games=games)
    return render_template("profile.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST" :
        query = request.form['search']
        games = db.search_games(connection, query)
    else:
        games = db.get_all_games(connection)
    if "email" in session :
        if session['email'] == "admin@gmail.com":
            return redirect(url_for('admin_add_game'))
    else:
        return render_template('search.html', user=None, games=games, query=query)
    user = db.get_user(connection, session['email'])
    return render_template('search.html',user=user, games=games, query=query)

@app.route('/add_game', methods=['GET', 'POST'])
def admin_add_game():
    if 'email' not in session:
        return redirect(url_for('home'))
    if session['email'] != 'admin@gmail.com':
        return "Access Denied", 403
    return render_template("admin-add.html")

@app.route('/edit_game', methods=['GET', 'POST'])
def admin_edit_game():
    if 'email' not in session:
        return redirect(url_for('home'))
    if session['email'] != 'admin@gmail.com':
        return "Access Denied", 403
    games = db.get_all_games(connection)
    return render_template("admin-edit.html", games=games)

@app.route('/update-general',  methods=['GET', 'POST'])
def update_username():
    if request.method == 'POST':
        name = request.form['username']
        creditcard  = request.form['creditcard']
        if  db.get_user_by_username(connection, name): #unique const violation
            flash("User already taken")
            return redirect(url_for("info"))
        if creditcard:
            db.update_credit_card(connection=connection, email=session['email'], new_cc=creditcard)
        if name:
            db.update_username(connection=connection, email=session['email'], new_name=name)
            
    return redirect(url_for('info'))

@app.route('/update-pfp',  methods=['GET', 'POST'])
def update_pfp():
    if request.method == 'POST':
        image = request.files['profilePicture']
        if image:
            db.update_pfp(connection, session['email'], image.filename)
            image.save(os.path.join('src/static/img/user', image.filename)) #works
    return redirect(url_for('info'))

@app.route('/update-password',  methods=['GET', 'POST'])
def update_password():
    if request.method == 'POST':
        opassword = request.form['opassword']
        password = request.form['password']
        cpassword = request.form['cpassword']    
        if utils.is_password_match(opassword, db.get_user(connection, session['email'])['password']):
            if password == cpassword:
                db.update_password(connection, session['email'], password)
            else:
                flash("Passwords Don't match")
                redirect(url_for("info"))
        else:
            flash("Wrong Password")
            redirect(url_for("info"))
            
    return redirect(url_for('info'))

if __name__ == '__main__':
    db.init_db(connection)
    db.seed_admin_user(connection)
    app.run(debug=True)
