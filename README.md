# AWSRDS-ChatGPT-API-Caching

## Utilizing AWS RDS with Python PyMySQL for Efficient ChatGPT API Calls Management

### Introduction
In an era where AI chatbots, especially those powered by OpenAI's ChatGPT, are revolutionizing various industries, managing API calls efficiently is paramount. This project aims to significantly reduce ChatGPT API costs by up to 80% through a Python-based solution that incorporates AWS RDS and PyMySQL, enhancing performance and reducing operational expenses.

### Description
This Python script powers an AI chatbot capable of classifying users' MBTI personality types and learning styles. It harnesses OpenAI's GPT-3.5 model for response generation and employs a text similarity search algorithm to provide relevant answers from a pre-stored AWS RDS Table  file of question-answer pairs. The chatbot's knowledge base is continually updated and stored in the same AWS RDS Table.

### Project Overview
Our solution leverages the robustness of AWS RDS for database management, coupled with Python's PyMySQL for database interaction. By employing a caching mechanism and TF-IDF with cosine similarity for response retrieval, we minimize the need for frequent ChatGPT API calls.

Complete Project explaination 

#### Core Components and Implementation

1. **AWS RDS and PyMySQL Integration**: Utilize AWS RDS for a scalable database solution and PyMySQL for efficient Python-based database interactions.
   ```python
   import pymysql.cursors
   # Database connection setup...
   ```

2. **Caching Mechanism**: Implement a caching system to store and quickly retrieve question-answer pairs, reducing repetitive API calls.
   ```python
   qa_dict = {}
   # Code to load data from CSV...
   ```

3. **TF-IDF and Cosine Similarity for Query Matching**: Employ TF-IDF for vectorizing questions and cosine similarity for finding relevant stored answers.
   ```python
   from SimilarText import TextSimilarity
   # Code for similarity calculations...
   ```

4. **Reducing ChatGPT API Calls**: Prioritize using stored answers for similar questions before making new API calls.
   ```python
   if promptsimilarityvalue > 0.2:
       # Retrieve from database
   else:
       # API call to ChatGPT
   ```

5. **Smart Caching and Performance Optimization**: Enhance response time and cost efficiency by smartly caching recent queries and responses.
   ```python
   if prompt in qa_dict and qa_dict[prompt]['temperature'] == tem:
       # Use cached data
   else:
       # New data processing
   ```

### Conclusion
This approach integrates AWS RDS with Python PyMySQL to manage ChatGPT API usage effectively. The combined power of a caching system and similarity-based query matching significantly reduces API call frequency, offering a sustainable and economical solution for chatbot applications.

### Scope of Functionalities
- Classifies MBTI personality type and learning style.
- Generates responses using OpenAI's GPT-3.5 model.
- Utilizes a text similarity search algorithm for relevant answers.
- Continuously updates and stores data in a CSV file.

### Libraries Used
- OpenAI API
- Keras
- Pandas
- NumPy
- TfidfVectorizer
- Cosine Similarity
