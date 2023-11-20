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


# function for getting column info from a DataFrame
def get_column_info(df):
    column_names = df.columns.tolist()
    data_types = df.dtypes.tolist()
    num_columns = df.shape[1]  # Get the number of columns
    #data_size = df.shape
    missing_values = df.isnull().sum().tolist()
    print("Column Names:", column_names)
    print("Data Types:", data_types)
    print("Number of Columns:", num_columns)
    print("Missing Values:", missing_values)
    return column_names, data_types, num_columns, missing_values


def get_json_column_info(json_data):
    column_info = []

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            dtype = type(value).__name__ if value is not None else 'Unknown'
            size = 1
            missing = 0 if value is not None else 1

            column_info.append({
                'col': key,
                'dtype': dtype,
                'size': size,
                'missing': missing
                  })
    return column_info

def get_xml_column_info(xml_data):
    column_info = []

    soup = BeautifulSoup(xml_data, 'xml')

    for element in soup.find_all():
        #  info based on the element name
        name = element.name
        text = element.text.strip() if element.text else None
        print(f"Name: {name}, Text: {text}")  # debug line

        column_info.append({
            'name': name,
            'text': text,
        })
    print("Column Info:", column_info)  # debug line
    return column_info



# Route to show information about the uploaded  file
@app.route('/get_info')
def file_info():
    if 'username' in session and 'uploaded_data_file_path' in session:
        file_path = session['uploaded_data_file_path']
        
        if os.path.exists(file_path):
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                column_info = get_column_info(df)
                print("Column Info:", column_info)
                return render_template('showdata.html', column_info=column_info)
            elif file_path.endswith('.json'):
                 # Handling .json file
                with open(file_path, 'r') as json_file:
                    json_data = json.load(json_file)
                column_info = get_json_column_info(json_data)
                return render_template('showdata_json.html',column_info=column_info)
            elif file_path.endswith('.xml'):
                # Handling .xml file using BeautifulSoup
                with open(file_path, 'r') as xml_file:
                    xml_data = xml_file.read()
                column_info = get_xml_column_info(xml_data)
                print("Column Info:", column_info)  
                return render_template('showdata_xml.html', column_info=column_info)
            else:
                return "Unsupported file format. Only CSV, JSON, and XML files are allowed."

        return "Invalid file path."
    return redirect(url_for('login'))

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