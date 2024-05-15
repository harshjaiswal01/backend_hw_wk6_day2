from flask import Flask, jsonify, request #importing the Flask Class
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from db_connection import db_connection, Error

app = Flask(__name__)
ma = Marshmallow(app)

#Creating the Book Table Schema, to define the structure of data
class BookSchema(ma.Schema):
    id = fields.Int(dump_only=True) #dump_only means we dont input data for this field
    title = fields.String(required=True) #required means to be valid need a value
    isbn = fields.String(required=True)
    author = fields.String(required=True)
    publication_date = fields.Date(required=True)
    availability = fields.Bool(required=False)

    class Meta:
        fields = ("title", "isbn", "author", "publication_date")

book_schema = BookSchema()
books_schema = BookSchema(many=True)

@app.route('/') #Defining a simple home route
def home():
    return "Welcome to the Library Management System" #returning a response

#Reading all of our book data via GET request
@app.route("/books", methods=['GET'])
def get_bookss():
    conn = db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary=True)

            #writing query to get all users
            query = "SELECT * FROM books"
            cursor.execute(query)
            books = cursor.fetchall()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return books_schema.jsonify(books)
            

@app.route("/books", methods=['POST'])
def add_books():
    try:
        book_data = book_schema.load(request.json)
        print(book_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            #new_customer details
            new_book = (book_data['title'], book_data['isbn'], book_data['author'], book_data['publication_date'])

            #query
            query = "INSERT INTO Books (title, isbn, author, publication_date) VALUES (%s,%s,%s, %s)"

            #Execute query with new_book data
            cursor.execute(query, new_book)
            conn.commit()

            return jsonify({'Message': "New Book Added Successfully!"}), 201
        
        except Error as e:
            return jsonify(e.messages), 500
        
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"Error": "DB CONNECTION FAILED"}), 500
            
if __name__ == '__main__': #idiom to verify we're running this selected file and not allow running if imported
    app.run(debug=True)