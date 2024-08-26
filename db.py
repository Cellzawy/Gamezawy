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

def is_game_in_cart(connection,game_id = None,user_id = None):
    cursor = connection.cursor()
    query = '''
        SELECT * FROM in_cart
        WHERE game_id = ? AND user_id = ?;
    '''
    cursor.execute(query, (game_id,user_id))
    return cursor.fetchone()