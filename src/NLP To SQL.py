
# Answer to Natural Language question, such as "Provide candidates with x-number of experience " and convert that into a SQL query. 

#import necessary libraries
import os
import pandas as pd
import openai


df = pd.read_csv("/home/mirafra/Downloads/resumes(1).csv",on_bad_lines='skip')  #load the csv file into padas dataframe

df.head()   #glance at the columns 

# ## SQL Database Set-up

from sqlalchemy import create_engine
from sqlalchemy import text

temp_db = create_engine('sqlite:///:memory:', echo=True)

# Using SQL Alchemy to establish a connection to this temporary database and query it for the results:

data = df.to_sql(name='Resumes',con=temp_db)    # Here we push our entire DataFrame to a table called Resumes

# ### Set-up Open AI API Key

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = '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'


# ### Inform GPT about the SQL Table Structure ---Prompt-Type-1 (extensive information)

# def create_table_definition_prompt(df):
#     """
#     This function returns a prompt that informs GPT that we want to work with SQL Tables
#     """
# 
#     prompt = ''' You are a helpful AI assistant expert in unserstanding the user's question and then creating a SQL query to find answer to.
#          user's question. 
#          Resumes table contains information about the candidate's id, candidate's name, the file_name for that candidate in our database, candidate's email, candidate's phone, candidate's experience, candidate's qualification.
#          The description for the Resumes table is provided below:
#          1) id = unique integer type id for each candidate 
#          2) name= collection of string despicting candidate's name
#          3) file_name=unique file name for that candidate in our database
#          4) email= collection of string and numbers and special characters 
#          5) phone= collection of positive integers
#          6) candidate's experience= positive float number
#          7) candidate's qualification= collection of string despicting candidate's college name which starts with capital 
#          letters and consists of abbreviations in capital letters
#     
#          Context:### sqlite SQL table, with its properties:
# #
# # Resumes({})
# #
# '''.format(",".join(str(x) for x in df.columns))
#     
#     return prompt


# ### Inform GPT about the SQL Table Structure ---Prompt-Type-2 (minimal information)

def create_table_definition_prompt(df):
    """
    This function returns a prompt that informs GPT that we want to work with SQL Tables
    """

    prompt = ''' You are a helpful AI assistant expert in unserstanding the user's question and then creating a SQL query to find answer to.
         user's question. 
         Resumes table contains information about the candidate. Before, generating the answer consider the name of the columns to understand 
         the data type and entries it could possibly have.
         Context:### sqlite SQL table, with its properties:
#
# Resumes({})
#
'''.format(",".join(str(x) for x in df.columns))
     
    return prompt


print(create_table_definition_prompt(df))


# Creating a function that grabs the natural language information request:


def prompt_input():
    nlp_text = input("Enter information you want to obtain: ")
    return nlp_text


# question could be like:
# provide me people with 5 years of experience and graduation from NIT
# provide me people with 5 years of experience and graduation from NIT and phone number ending with 6  #making harder questions to check model's strength


nlp_text = prompt_input()


def combine_prompts(df, query_prompt):       # combine the results in one function:
    definition = create_table_definition_prompt(df)
    query_init_string = f"### A query to answer: {query_prompt}\nSELECT"
    return definition+query_init_string
    

combine_prompts(df, nlp_text)


# We start prompt completion as a SQL query by writing "\nSELECT"


response = openai.Completion.create(
  model="gpt-3.5-turbo-instruct",
  prompt=combine_prompts(df, nlp_text),
  temperature=0.0,    #temperature=0 means no exploration 
  max_tokens=150,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0,
  stop=["#", ";"]
)



# function to parse the section of the response we are interested into

def handle_response(response):
    query = response["choices"][0]["text"]
    if query.startswith(" "):
        query = "Select"+ query
    return query


handle_response(response)


# Pass that response into our Database:


with temp_db.connect() as conn:
    result = conn.execute(text(handle_response(response)))

result.all()

