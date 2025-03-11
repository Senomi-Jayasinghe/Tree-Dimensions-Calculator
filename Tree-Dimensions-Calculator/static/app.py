from flask import Flask, request, jsonify, render_template
import pyodbc
import os
from werkzeug.utils import secure_filename
from datetime import datetime  

app = Flask(__name__)

entry_user = None

db_config = {
    'server': 'DESKTOP-I8O0T49\\SQLEXPRESS',
    # 'server': 'ICT-HASHAN-L\SQLEXPRESS',
    'database': 'CarbonCreditDB'
}

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={db_config["server"]};'
            f'DATABASE={db_config["database"]};'
            'Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def image_to_binary(image_file):
    return image_file.read()


@app.route('/', methods=['GET'])
def index():
    global entry_user
    if request.method == 'GET':
        if not entry_user:
            print(f"Error: Tree ID (entry_user) is not provided. Value of entry_user: {entry_user}")
    
        entry_user = request.args.get('id')

        print(f"Received Tree ID: {entry_user}")

    return render_template('index.html')

@app.route('/insert', methods=['POST'])
def insert_tree_data():
    global entry_user

    if request.method == 'POST':
        if not entry_user:
            print(
                f"Error: Tree ID (entry_user) is not provided. Value of entry_user: {entry_user}")
            return jsonify({'status': 'error', 'message': 'Tree ID not provided from GET request. Please provide an ID first with a GET request'})

        tree_name = request.form.get('name', 'Unknown')
        geo_location = request.form.get('location', 'Unknown')
        tree_height = request.form.get('height')
        diameter_width = request.form.get('width')
        tree_age = request.form.get('age', 'Not provided')

        image_file = request.files.get('image')
        image_extension = None

        if image_file and allowed_file(image_file.filename):
            image_binary = image_to_binary(image_file)
            image_extension = image_file.filename.rsplit('.', 1)[1].lower()
            print(f"Image binary data size: {len(image_binary)} bytes")
        else:
            image_binary = None
            print("No valid image file provided.")

        entry_date = datetime.now()

        print(
            f"Inserting data for Tree: {tree_name}, Location: {geo_location}, Height: {tree_height}, Width: {diameter_width}, Age: {tree_age}, User ID: {entry_user}, Date: {entry_date}")

        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'Database connection failed'})

        cursor = conn.cursor()
        try:
            if image_binary:
                cursor.execute('''
                    INSERT INTO TreeDetails (tree_name, tree_location, tree_height, tree_width, tree_age, tree_picture, entry_user, entry_date, tree_picture_format)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tree_name, geo_location, tree_height, diameter_width, tree_age, image_binary, entry_user, entry_date,'.'+ image_extension))
            else:
                cursor.execute('''
                    INSERT INTO TreeDetails (tree_name, tree_location, tree_height, tree_width, tree_age, entry_user, entry_date, tree_picture_format)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tree_name, geo_location, tree_height, diameter_width, tree_age, entry_user, entry_date,'.'+ image_extension))

            conn.commit()
            response = {'status': 'success',
                        'message': 'Data and image inserted successfully'}
            print("Data inserted successfully")
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}
            print(f"Error inserting data: {e}")
        finally:
            cursor.close()
            conn.close()

        return jsonify(response)

    # elif request.method == 'GET':
    #     entry_user = request.args.get('id')

    #     # Check if entry_user was provided
    #     if not entry_user:
    #         print("Error: User ID not provided")
    #         return jsonify({'status': 'error', 'message': 'UserID not provided'})

    #     # Log the received ID
    #     print(f"Received Tree ID: {entry_user}")

    #     return jsonify({'status': 'success', 'message': f'ID {entry_user} stored successfully'})


if __name__ == '__main__':
    app.run(debug=True)
