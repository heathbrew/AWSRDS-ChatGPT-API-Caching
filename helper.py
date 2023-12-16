import openai

openai.api_key = 'OPENAI API KEY'

# Load the model and vectorizer from pkl files
import pickle
with open('model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)
with open('vectorizer.pkl', 'rb') as f:
    loaded_vectorizer = pickle.load(f)

# Build the chatbot
def classify_personality(response):
    X_test = loaded_vectorizer.transform([response])
    prediction = loaded_model.predict(X_test)[0]
    return prediction

import pickle
from keras.models import load_model
from keras.utils import pad_sequences
import re
import numpy as np

def classify_learning_type(sentence):
    sentence = clean(sentence)
    sentence = tokenizer.texts_to_sequences([sentence])
    sentence = pad_sequences(sentence, maxlen=48, truncating='pre')
    result = le.inverse_transform(np.argmax(model.predict(sentence), axis=-1))[0]
    return result

# Text preprocessing function
def clean(text):
    global str_punc
    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = text.lower()
    return text    

# Load tokenizer
with open('tokenizer.pickle', 'rb') as f:
    tokenizer = pickle.load(f)

# Load label encoder
with open('labelEncoder.pickle', 'rb') as f:
    le = pickle.load(f)

# Load model
model = load_model('LearningStyleClassifier.h5')

import csv
import pandas as pd
import os


# Load the question-answer pairs and temperature from the CSV file into a dictionary
qa_dict = {}
with open('question_answer.csv', 'r') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        qa_dict[row['prompt']] = {
            'returnstring': row['returnstring'],
            'mbti': row['mbti'],
            'learning': row['learning'],
            'temperature': float(row['temperature'])
        }

# def send_gpt(prompt, tem):
#     # prompt = prompt.lower()
#         # Check if the prompt already exists in the QA dictionary
#     if prompt in qa_dict and qa_dict[prompt]['temperature'] == tem:
#         stored_data = qa_dict[prompt]
#         returnstring = "Found in Database \n"+stored_data['returnstring']
#     # if prompt in qa_dict and qa_dict[prompt]['temperature'] == tem:
#     #     stored_data = qa_dict[prompt]
#     #     returnstring = stored_data['returnstring']
#     #         # returnstring = stored_data['returnstring'] 
#     #         # print("Additional knowledge gained from memory: MBTI - " + stored_data['mbti'] + ", Learning type - " + stored_data['learning'])
#     else:
#         try:
#             # temprature = tem
#             mbti = str(classify_personality(prompt))
#             learning = str(classify_learning_type(prompt))
#             response = openai.ChatCompletion.create(
#                         model="gpt-3.5-turbo",
#                         messages=[
#                                 {"role": "system", "content": """You are Doubt solving teacher who consider all questions to be academic and answer question with strict adherence to the MBTI personality type of student and the Learning way of student in Depth and with high reasoning.
#                                                                 Your student has""" + learning  + """way of learning and 
#                                                                 the MBTI of your student is """ + mbti},
#                                 {"role": "user", "content": prompt},
#                             ],
#                         temperature=tem
#                     )
#             returnstring = "You are a " + mbti + " and prefer a " + learning + " way of learning \n" + str(response.choices[0].message.content)

#             # create dataframe and append row
#             # Update the QA dictionary with the new question-answer pair and temperature
#             qa_dict[prompt] = {
#                 'returnstring': returnstring,
#                 'mbti': mbti,
#                 'learning': learning,
#                 'temperature': tem
#             }
#             # Append the new question-answer pair and temperature to the CSV file
#             row = {'prompt': prompt, 'returnstring': returnstring, 'mbti': mbti, 'learning': learning, 'temperature': tem}
#             df = pd.DataFrame(row, index=[0])
#             df.to_csv('question_answer.csv', mode='a', header=not os.path.exists('question_answer.csv'), index=False)
#         except Exception as e:
#             return e

#     return returnstring

import pymysql.cursors
from SimilarText import  TextSimilarity
import openai
import pandas as pd
import os

# Connect to the database
db = pymysql.connect(host='<AWS RDS URL>>',
                     port=3306,
                     db = "<Database Name>",
                     user='<UserID>',
                     password='<Password>',
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)

# Prepare a cursor object using cursor() method
cursor = db.cursor()

# SQL query to select all rows from the table
sql = 'SELECT * FROM Learningchatbot'

# Execute the SQL command
cursor.execute(sql)

# Fetch all the rows in a dictionary format
results = cursor.fetchall()

# Load the question-answer data
qa_dict = {row['prompt']: {'returnstring': row['returnstring'], 'mbti': row['mbti'], 'learning': row['learning'], 'temperature': row['temperature']} for row in results}

# Create an instance of TextSimilarity
text_similarity = TextSimilarity()

# Update the embeddings
vectorstore = text_similarity.update_embeddings(qa_dict)

def send_gptnew(prompt, tem, vecstore=vectorstore):
    try:
        promptsimilarityvalue = text_similarity.top_similar_prompts(prompt, vecstore)[0][1]
    except Exception:
        promptsimilarityvalue = 0

    Databasescore =  "Databasesimilarity score is "+ str(promptsimilarityvalue)
    
    if prompt in qa_dict and qa_dict[prompt]['temperature'] == tem:
        stored_data = qa_dict[prompt]
        returnstring = Databasescore + " \nFound in Database \n" + stored_data['returnstring']
    elif promptsimilarityvalue > 0.2 :
        similar_conversation = text_similarity.top_similar_docs(prompt, vecstore, qa_dict)
        summary = text_similarity.extractive_summary(prompt, similar_conversation)
        returnstring = Databasescore + " \nSearched from Database \n" + summary 
    else:
        try:
            mbti = str(classify_personality(prompt))
            learning = str(classify_learning_type(prompt))
            response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": """You are Doubt solving teacher who consider all questions to be academic and answer question with strict adherence to the MBTI personality type of student and the Learning way of student in Depth and with high reasoning.
                                                                Your student has""" + learning  + """way of learning and 
                                                                the MBTI of your student is """ + mbti},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=tem
                    )
            returnstring = Databasescore + " \nYou are a " + mbti + " and prefer a " + learning + " way of learning \n" + str(response.choices[0].message.content)

            # Update the QA dictionary with the new question-answer pair and temperature
            qa_dict[prompt] = {
                'returnstring': returnstring,
                'mbti': mbti,
                'learning': learning,
                'temperature': tem
            }

            text_similarity.update_embeddings(qa_dict)

            # Append the new question-answer pair and temperature to the database
            sql = "INSERT INTO Learningchatbot (prompt, returnstring, mbti, learning, temperature) VALUES (%s, %s, %s, %s, %s)"
            values = (prompt, returnstring, mbti, learning, tem)
            cursor.execute(sql, values)
            db.commit()

        except Exception as e:
            return e
    # Whenever you're done with the operations, don't forget to close the database connection
    # db.close()
    return returnstring

