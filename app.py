from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import json
import os
from bs4 import BeautifulSoup
app = Flask(__name__)
app.secret_key = 'Nick' 


# function for checking user credentials
def check_credentials(username, password):
    with open('data/user.txt', 'r') as file:
        for line in file:
            stored_username, stored_password = line.strip().split(',')
            if username == stored_username and password == stored_password:
                return True
    return False

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('upload_csv.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_credentials(username, password):
            session['username'] = username
            return redirect(url_for('home'))

        return "Invalid username or password. Please try again."

    return render_template('login.html')



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' in session:
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file:
                filename = uploaded_file.filename
                file_path = os.path.join('my_sql_temp_data', filename)
                uploaded_file.save(file_path)
                session['uploaded_data_file_path'] = file_path
                return f"File {filename} has been uploaded successfully."
            
           
        return render_template('upload.html')

    return redirect(url_for('login'))

def get_file_info(file_path):
    column_info = []

    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        column_info = [{'col': col, 'dtype': str(dtype), 'size': df[col].size, 'missing': df[col].isnull().sum()}
                       for col, dtype in zip(df.columns, df.dtypes)]

    elif file_path.endswith('.json'):
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)
        column_info = [{'col': key, 'dtype': type(value).__name__, 'size': 1, 'missing': 0 if value is not None else 1}
                       for key, value in json_data.items()]

    elif file_path.endswith('.xml'):
        with open(file_path, 'r') as xml_file:
            soup = BeautifulSoup(xml_file, 'xml')
        column_info = [{'name': element.name, 'text': element.text.strip() if element.text else None}
                       for element in soup.find_all()]

    return column_info

@app.route('/get_info')
def file_info():
    if 'username' in session and 'uploaded_data_file_path' in session:
        file_path = session['uploaded_data_file_path']
        
        if os.path.exists(file_path):
            column_info = get_file_info(file_path)
            return render_template('showdata.html', column_info=column_info)
        
        return "Invalid file path."
    return "User not authenticated or no file uploaded."


@app.route('/dashboard')
def dashboard():
    # Any necessary logic here
    return render_template('Tableau.html')


@app.route('/logout')
def logout():
    session.pop('username', None)

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
