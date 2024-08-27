import re
import bcrypt
import os 

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    return hashed_password.decode()


def is_password_match(entered_password, stored_hash):
    stored_hash_bytes = stored_hash.encode()

    return bcrypt.checkpw(entered_password.encode(), stored_hash_bytes)


def is_strong_password(password):
    min_length = 8
    require_uppercase = True
    require_lowercase = True
    require_digit = True
    require_special_char = True

    if len(password) < min_length:
        return False

    if require_uppercase and not any(char.isupper() for char in password):
        return False

    if require_lowercase and not any(char.islower() for char in password):
        return False

    if require_digit and not any(char.isdigit() for char in password):
        return False

    if require_special_char and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True

def is_email_valid(email):

    if(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)):
        return True

    else:
        return False

def is_credit_card_valid(credit_card):
    return re.fullmatch(r'^\d{4}-\d{4}-\d{4}-\d{4}$', credit_card)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file_size(file):

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0, os.SEEK_SET)
    return file_size <= MAX_FILE_SIZE_BYTES