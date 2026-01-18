from flask import Flask, request, jsonify
from flask_login import (LoginManager, UserMixin, login_user, logout_user, login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)

def connect():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    con = connect()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT* FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    con.close()
    if user:
        return User(**user)
    return None

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    password_hash = generate_password_hash(data["password"])
    con = connect()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (data["username"], data["email"], password_hash))
        con.commit()
    except mysql.connector.IntegrityError:
        return jsonify({"error": "User already exists"}), 400
    finally:
        con.close()

    return jsonify({"message": "User registered successfully."}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    con = connect()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (data["email"],))
    user = cur.fetchone()
    con.close()

    if not user or not check_password_hash(user["password_hash"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    login_user(User(**user))
    return jsonify({"message": "Login successful"})

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})    

@app.route("/books", methods=["POST"])
@login_required
def add_book():
    data = request.json
    con = connect()
    cur = con.cursor()
    query = """INSERT INTO books (title, author, year, genre) VALUES (%s, %s, %s, %s)"""
    cur.execute(query,(data["title"], data["author"], data["year"], data["genre"]))
    con.commit()
    print("Book added successfully!")
    con.close()
    return jsonify({"message": "Book added successfully"}), 201

@app.route("/books", methods=["GET"])
@login_required
def view_books():
    con = connect()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM books WHERE user_id=%s", (current_user.id,))
    books = cur.fetchall()
    con.close()
    return jsonify(books)

@app.route("/book/search")
@login_required
def search_book():
    title = request.args.get("title")
    con = connect()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM books WHERE title LIKE %s", ("%" + title + "%",))
    books = cur.fetchall()
    con.close()
    return jsonify(books)

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    con = connect()
    cur = con.cursor()
    cur.execute("DELETE FROM books WHERE id = %s", (book_id, current_user.id))
    con.commit()
    con.close()
    return jsonify({"message":"Book deleted successfully"})
        
if __name__ == "__main__":
    app.run(debug=True)    



