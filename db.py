import utils


def connect_to_database(name='database.db'):
    import sqlite3
    conn = sqlite3.connect(name, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(connection):
    cursor = connection.cursor()

    cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            balance REAL NOT NULL DEFAULT 0,
            credit_card TEXT, 
            img_path TEXT
		);
	''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL,
            genres TEXT NOT NULL,
            release_date TEXT NOT NULL,
            img_path TEXT NOT NULL,
            developers TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            paid_amount REAL NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE 
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaction_items (
            transaction_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL, 
            FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE, 
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE 
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS in_library (
            user_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL, 
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, 
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE 
        )
    ''')
    
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS in_cart (
            user_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL, 
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, 
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE 
        )
    ''')
    
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS comments (
            user_img TEXT NOT NULL,
            username TEXT NOT NULL,
            comment_body TEXT NOT NULL,
            game_id INTEGER NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE, 
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE 
        )
    ''')

    connection.commit()


def add_user(connection, username, password, email):
    cursor = connection.cursor()
    hashed_password = utils.hash_password(password)
    query = '''INSERT INTO users (username, password, email) VALUES (?, ?, ?)'''
    cursor.execute(query, (username, hashed_password, email))
    connection.commit()


def get_user(connection, email):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE email = ?'''
    cursor.execute(query, (email,))
    return cursor.fetchone()

def get_user_by_username(connection, username):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE username = ?'''
    cursor.execute(query, (username,))
    return cursor.fetchone()


def get_all_users(connection):
    cursor = connection.cursor()
    query = 'SELECT * FROM users'
    cursor.execute(query)
    return cursor.fetchall()


def seed_admin_user(connection):
    admin_email = 'admin@gmail.com'
    admin_name = 'admin'
    admin_password = 'admin'

    # Check if admin user exists
    admin_user = get_user(connection, admin_email)
    if not admin_user:
        add_user(connection, admin_name, admin_password, admin_email)

def search_games(connection, search_query):
    cursor = connection.cursor()
    query = '''SELECT * FROM games WHERE name LIKE ?'''
    cursor.execute(query, (f"%{search_query}%",))
    return cursor.fetchall()

def get_game(connection, game_id):
    cursor = connection.cursor()
    query = '''SELECT * FROM games WHERE id = ?'''
    cursor.execute(query, (game_id,))
    return cursor.fetchone()

def get_all_games(connection):
    cursor = connection.cursor()
    query = 'SELECT * FROM games'
    cursor.execute(query)
    return cursor.fetchall()

def get_user_games(connection, id):
    cursor = connection.cursor()
    query = '''
        SELECT games.*
        FROM in_library
        JOIN games ON in_library.game_id = games.id
        WHERE in_library.user_id = ?;
    '''
    cursor.execute(query, (id,))
    return cursor.fetchall()

def get_user_cart(connection, id):
    cursor = connection.cursor()
    query = '''
        SELECT games.*
        FROM in_cart
        JOIN games ON in_cart.game_id = games.id
        WHERE in_cart.user_id = ?;
    '''
    cursor.execute(query, (id,))
    return cursor.fetchall()

def is_game_in_library(connection,game_id = None,user_id = None):
    cursor = connection.cursor()
    query = '''
        SELECT * FROM in_library
        WHERE game_id = ? AND user_id = ?;
    '''
    cursor.execute(query, (game_id,user_id))
    return cursor.fetchone()

def is_game_in_cart(connection,game_id = None,user_id = None):
    cursor = connection.cursor()
    query = '''
        SELECT * FROM in_cart
        WHERE game_id = ? AND user_id = ?;
    '''
    cursor.execute(query, (game_id,user_id))
    return cursor.fetchone()


def add_game_to_cart(connection,game_id = None,user_id = None):
    cursor = connection.cursor()
    query = '''
        INSERT INTO in_cart (user_id,game_id) VALUES (?, ?)
    '''
    cursor.execute(query, (user_id,game_id))
    return connection.commit()

def remove_game_from_cart(connection,game_id = None,user_id = None):
    cursor = connection.cursor()
    query = '''
        DELETE FROM in_cart WHERE user_id = ? AND game_id = ?
    '''
    cursor.execute(query, (user_id,game_id))
    return connection.commit()

def add_games_to_library(connection,user_id,total_price,games):
    cursor = connection.cursor()
    query = '''
        INSERT INTO transactions (user_id,paid_amount) VALUES (?,?)
    '''
    cursor.execute(query, (user_id,total_price))
    transaction_id = cursor.lastrowid
    for game in games:
        query2 = '''
            INSERT INTO transaction_items (transaction_id, game_id) VALUES (?,?)
        '''
        cursor.execute(query2, (transaction_id,game['id']))
        query3 = '''
            INSERT INTO in_library (user_id, game_id) VALUES (?,?)
        '''
        cursor.execute(query3, (user_id,game['id']))
    return connection.commit()

def add_game_to_library(connection,user_id,total_price,game):
    cursor = connection.cursor()
    query = '''
        INSERT INTO transactions (user_id,paid_amount) VALUES (?,?)
    '''
    cursor.execute(query, (user_id,total_price))
    
    transaction_id = cursor.lastrowid
    query2 = '''
        INSERT INTO transaction_items (transaction_id, game_id) VALUES (?,?)
    '''
    cursor.execute(query2, (transaction_id,game['id']))

    query3 = '''
        INSERT INTO in_library (user_id, game_id) VALUES (?,?)
    '''
    cursor.execute(query3, (user_id,game['id']))
    return connection.commit()

def remove_games_from_cart(connection,user_id):
    cursor = connection.cursor()
    query = '''
        DELETE FROM in_cart WHERE user_id = ?
    '''
    cursor.execute(query, (user_id,))
    return connection.commit()

def update_user_balance(connection,user_id,total_price):
    cursor = connection.cursor()
    query = '''
        UPDATE users SET balance = balance - ? WHERE id = ?;
    '''
    cursor.execute(query, (total_price,user_id))
    return connection.commit()

def update_username(connection, email, new_name):
    cursor = connection.cursor()
    cursor.execute(
        '''
            UPDATE users
            SET username = ?
            WHERE email = ?
        '''
        , (new_name, email)
    )
    return connection.commit()
    
def update_password(connection, email, new_password):
    cursor = connection.cursor()
    cursor.execute(
        '''
            UPDATE users
            SET password = ?
            WHERE email = ?
        '''
        , (utils.hash_password(new_password), email)
    )
    return connection.commit() 
    
def update_credit_card(connection, email, new_cc):
    cursor = connection.cursor()
    cursor.execute(
        '''
            UPDATE users
            SET credit_card = ?
            WHERE email = ?
        '''
        , (new_cc, email)
    )
    return connection.commit()
    
def update_pfp(connection, email, new_pfp):
    cursor = connection.cursor()
    cursor.execute(
        '''
            UPDATE users
            SET img_path = ?
            WHERE email = ?
        '''
        , (new_pfp, email)
    )
    return connection.commit()

def add_game(connection,game_name,game_price,game_description,game_genres,game_release_date,game_img_path,game_developers):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO games (name,price,description,genres,release_date,img_path,developers)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (game_name,game_price,game_description,game_genres,game_release_date,game_img_path,game_developers))
    return connection.commit()

def remove_game(connection, game_id):
    cursor = connection.cursor()
    query = "DELETE FROM games WHERE id = ?"
    cursor.execute(query, (game_id,))
    return connection.commit()

def edit_game(connection,name,price,description,genres,release_date,img_path,developers,id):
    cursor = connection.cursor()
    cursor.execute(
        '''
            UPDATE games
            SET name = ?, price = ?,description = ? ,genres= ? ,release_date = ? ,img_path = ?,developers = ?
            WHERE id = ?
        '''
        , (name,price,description,genres,release_date,img_path,developers,id)
    )
    return connection.commit()

def add_comment(connection,user_img,username,game_id,comment_body):
    cursor = connection.cursor()
    cursor.execute(
        '''
           INSERT INTO comments (user_img,username,comment_body,game_id) VALUES (?,?,?,?)
        '''
        , (user_img,username,comment_body,game_id)
    )
    return connection.commit()

def get_comments(connection,game_id):
    cursor = connection.cursor()
    cursor.execute(
        '''
           SELECT * FROM comments where game_id = ?
        '''
        , (game_id,)
    )
    return cursor.fetchall()

def comments_update_pfp(connection, username, new_pfp):
    cursor = connection.cursor()
    cursor.execute(
        '''
            UPDATE comments
            SET user_img = ?
            WHERE username = ?
        '''
        , (new_pfp,username)
    )
    return connection.commit()