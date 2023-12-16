from flask import Flask, render_template, request, redirect, url_for
import csv
import openai
import speech_recognition as sr
import pyttsx3

app = Flask(__name__)

def check_credentials(username, password):
    with open('credentials.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if row[0] == username and row[1] == password:
                return True
    return False

def ask_gpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].text.strip()
    return message

@app.route('/')
def index():
    return render_template('content.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_credentials(username, password):
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password.'
    return render_template('signin.html', error=error)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/content')
def content():
    return render_template('content.html')

from helper import send_gptnew

@app.route('/chat_2', methods=['GET', 'POST'])
def get_request_json():
    if request.method == 'POST':
        if len(request.form['question']) < 1:
            return render_template(
                'chat_2.html', question="NULL", res="Question can't be empty!",temperature="NULL")
        question = request.form['question']
        temperature = float(request.form['temperature'])
        print("======================================")
        print("Receive the question:", question)
        print("Receive the temperature:",temperature)
        res = send_gptnew(question.lower().title(),temperature)
        print("Q: \n", question)
        print("A: \n", res)

        return render_template('chat_2.html', question=question, res=str(res), temperature=temperature)
    return render_template('chat_2.html', question=0)

@app.route('/index2')
def index2():
    return render_template('index2.html')

@app.route('/voice')
def voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak:")
        audio = r.listen(source)

    try:
        prompt = r.recognize_google(audio)
        if prompt.lower() == "bye":
            print()
            print("Bye, tumharo din achha beete lala/lali")
        else:
            print("You said: " + prompt)
            bot_response = ask_gpt(prompt)
            print("Bot:", bot_response)

            engine = pyttsx3.init()
            engine.say(bot_response)
            engine.runAndWait()
        
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    return render_template('index2.html')


# @app.route('/SQLCHATBOTSIFA', methods=['GET', 'POST'])
# def get_request():
#     if request.method == 'POST':
#         if len(request.form['question']) < 1:
#             return render_template(
#                 'SQLCHATBOTSIFA.html', question="NULL", res="Question can't be empty!",temperature="NULL")
#         question = request.form['question']
#         temperature = float(request.form['temperature'])
#         print("======================================")
#         print("Receive the question:", question)
#         print("Receive the temperature:",temperature)
#         res = send_gptnew(question.lower().title(),temperature)
#         print("Q: \n", question)
#         print("A: \n", res)

#         return render_template('SQLCHATBOTSIFA.html', question=question, res=str(res), temperature=temperature)
#     return render_template('SQLCHATBOTSIFA.html', question=0)

from flask import jsonify
import re
from helper import DB, format_question, final_format_question, extract_sql_query , get_formated , get_response , direct_sql_query
import time
from openai.error import RateLimitError
@app.route('/SQLCHATBOTSIFA', methods=['GET', 'POST'])
def get_request():
    if request.method == 'POST':
        if len(request.form['question']) < 1:
            return render_template(
                'SQLCHATBOTSIFA.html', question="NULL", res="Question can't be empty!",temperature="NULL")
        question = request.form['question']
        temperature = float(request.form['temperature'])
        print("======================================")
        print("Receive the question:", question)
        print("Receive the temperature:",temperature)

        # SQL processing
        db = DB(
            host='cumulativedb.cn6kglpqpr9u.us-east-1.rds.amazonaws.com',
            port=3306,
            db='Cumulative',
            user='dbadmin',
            password='Kalokson1!'
        )
        column_mapping = {
    ("cumulativeinsight", "Cumulativeinsight"): "Cumulativeinsight",
    ("user_id", "Userid", "UserID", "User_Id", "User ID"): "user_id",
    ("client_id", "Clientid", "ClientID", "Client_Id", "Client ID"): "client_id",
    ("Name", "name", "NAME"): "Name",
    ("Age", "age", "AGE"): "Age",
    ("Retirement Age", "Retirement age", "retirement age", "Retirement_Age", "retirement_age"): "Retirement_Age",
    ("Email", "email", "EMAIL", "e-mail", "E-mail", "E-Mail"): "Email",
    ("Marital Status", "marital status", "Marital_Status", "marital_status"): "Marital_Status",
    ("Phone", "phone", "PHONE", "Phone Number", "phone number", "PhoneNumber", "phone_number"): "Phone",
    ("Date of Birth", "date of birth", "Date_of_Birth", "date_of_birth", "DOB", "dob"): "Date_of_Birth",
    ("Gender", "gender", "GENDER"): "Gender",
    ("Number of Children", "number of children", "Number_of_Children", "number_of_children"): "Number_of_Children",
    ("Salary", "salary", "SALARY"): "Salary",
    ("Profession", "profession", "PROFESSION", "Occupation", "occupation", "OCCUPATION"): "Profession",
    ("Country", "country", "COUNTRY"): "Country",
    ("Assets", "assets", "ASSETS"): "Assets",
    ("Expenses", "expenses", "EXPENSES"): "Expenses",
    ("Investments", "investments", "INVESTMENTS"): "Investments",
    ("Pension", "pension", "PENSION"): "Pension",
    ("Protection", "protection", "PROTECTION"): "Protection",
    ("Future Goals", "future goals", "Future_Goals", "future_goals"): "Future_Goals"
    }   
        response1 = make_api_call_response1(question,column_mapping)
        response2 = make_api_call_response2(response1, column_mapping)
        response3 = extract_sql_query(response2)
        if response3 == "No valid query":
            response3 = direct_sql_query(response2)
        query_result = process_query(response3, question, db)
        response = response3
        print("Q: \n", response)
        print("A: \n", query_result)  
        return render_template('SQLCHATBOTSIFA.html', question=response, res=(query_result), temperature=temperature)
    return render_template('SQLCHATBOTSIFA.html', question=0)

def process_query(response, Question, db):
    if check_sql_query(response):
        query_result = db.execute_query(response, Question)
    # print("Response:", response)
    # print("Query Result:", query_result)
        return query_result

def check_sql_query(query):
    pattern = r"^SELECT.+;$"
    return re.match(pattern, query, re.I | re.DOTALL) is not None

def make_api_call_response1(question, column_mapping):
    try:
        response1 = str(format_question(get_formated(question),column_mapping))
        # Rest of your code
    except RateLimitError as e:
        # Handle rate limit error
        print("Rate limit exceeded. Waiting for cooldown...")
        # Wait for a minute before retrying
        time.sleep(60)
        # Retry the API call recursively
        response1 = str(format_question(get_formated(question),column_mapping))
        # Rest of your code
    return response1

def make_api_call_response2(response1, column_mapping):
    try:
        response2 = final_format_question(str(get_response(response1)), column_mapping)
        # Rest of your code
    except RateLimitError as e:
        # Handle rate limit error
        print("Rate limit exceeded. Waiting for cooldown...")
        # Wait for a minute before retrying
        time.sleep(60)
        # Retry the API call recursively
        response2 = final_format_question(str(get_response(response1)), column_mapping)
        # Rest of your code
    return response2




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
