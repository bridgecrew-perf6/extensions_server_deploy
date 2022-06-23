import bcrypt
import jwt

JWT_secret = "awdsx"

def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    hashedPass = bcrypt.hashpw(plain_text_password.encode('utf8'), bcrypt.gensalt())
    return hashedPass.decode('utf8')


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))


def getUserIdFromToken(token):
    return jwt.decode(token, JWT_secret, algorithms=["HS256"])['user_id']

def append_new_line(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)