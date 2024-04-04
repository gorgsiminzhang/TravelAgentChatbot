from flask import Flask
from flask_cors import CORS
import flask
import json

#get SQL 
import mysql.connector
from mysql.connector import Error

import re

import logging
from colorlog import ColoredFormatter

# 创建一个日志记录器
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 创建一个流处理器
stream_handler = logging.StreamHandler()

# 设置颜色格式
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models import KeyedVectors
import numpy as np

from pathlib import Path



# current direction
current_dir = Path(__file__).parent
word2vec_output_file = current_dir /'glove.6B.300d.txt.word2vec'
# load transformed file
model = KeyedVectors.load_word2vec_format(word2vec_output_file, binary=False)


# 定义计算平均向量的函数
def word_vector(words):
    # remove functional words, lowercase, remove words not in the model
    function_words = ['a','an','the','this','that','these','those','it','includes','at','in', 'on', 'from','under','by','for','to','and','but','before','after','oh','well','hi','hello','please','can','could','what']
    lowerwords = [element.lower() for element in words]
    valid_words = [word for word in lowerwords if word in model and word not in function_words]
    if not valid_words:
        return None
    #return word vector
    return [model[word] for word in valid_words]

def cosine_similarity(vec1,vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
def classifyIfSQL():
    keyword = get_keyword()
    keyVec = word_vector(keyword)
    inputLst = userInput.split(' ')
    logger.debug(f"userInput is: {userInput}")
    logger.debug(f"inputLst is: {inputLst}")
    rmmklst = [re.sub(r'[^a-zA-Z]', '', inp) for inp in inputLst]
    userVec = word_vector(rmmklst)
    threshold = 0.6 
    if userVec == None:
        return False
    similarityUsers = [max([cosine_similarity(vecU, vecK) for vecK in keyVec]) for vecU in userVec]
    similarity = max(similarityUsers)
    logger.info(f"similarity is: {similarity}")
    #print(similarity)
    if similarity > threshold:
        return True
    else:
        return False

def split_on_uppercase(input_string):
    # Insert a space before each uppercase letter that follows a lowercase letter
    modified_string = re.sub('(?<=[a-z])(?=[A-Z])', ' ', input_string)
    # Optionally split the string into a list of words
    words = modified_string.split()
    return words

#This function get sql table name and column name, then make them a list
def get_keyword():
    qry3 = "SHOW TABLES"
    tables = execute_read_query(cnx, qry3)
    tbstr1 = ""
    tbstr3 = ""
    for tb in tables:
        qry4 = 'SHOW COLUMNS FROM '+ tb[0]
        tbinfo1 = execute_read_query(cnx,qry4)
        tbinfo2 = [tbif[0] for tbif in tbinfo1]
        tbstr1 += str(tb[0]) + ','
        tbstr2 = ','.join(tbinfo2)
        tbstr1 += tbstr2
    #tbstr1 is a long string with table name and column name 
    strlst = tbstr1.split(',')#str to list
    strlst.extend(["cheap","expensive","place","recommend"])
    #FeedbackAndReview splits into ‘Feedback’，‘And’，‘Review’
    for substr in strlst:
        tbstr3 += ','.join(split_on_uppercase(substr)) + ','
    strlst = tbstr3[0:-1].split(',')#str to list
    strlst = list(set(strlst))
    return strlst


def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database="tadb"
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_read_query(connection, query):
    #connection.ping(reconnect=True, attempts=3, delay=5)
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        #cursor.close()
        #cursor = connection.cursor()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()
        #print(str(result)+"cursor closed")
    

def get_structure():
    qry1 = "SHOW TABLES"
    tables = execute_read_query(cnx, qry1)
    tbstr = ""
    for tb in tables:
        qry2 = 'DESCRIBE '+ tb[0]
        tbinfo = execute_read_query(cnx,qry2)
        tbstr += str("table name: ")+ str(tb[0])+ str(" Describe table: ")+ str(tbinfo) + ","
    #print(tbstr)
    logger.info(f"strucure is: {tbstr}")
    return tbstr

def trimquery(sqlquery):
    for tag in ["```sql", "```SQL", "```mysql", "```MYSQL"]:
        start = sqlquery.find(tag)
        if start != -1:
            # 标记后面跟着的是SQL语句，所以要跳过标记本身
            start += len(tag)
            break  # 找到一个就停止搜索
        
    if start == -1:
        # 如果没有找到任何标记
        logger.warning("SQL query start tag not found.")
        return "SQL query start tag not found."
    
    startqry = sqlquery[start:]
    end = startqry.find("```")
    if end == -1:
        # 如果找不到结束标记，可以返回整个提取的字符串或处理错误
        logger.warning("SQL query end tag not found.")
        return "SQL query end tag not found."
    
    endquery = startqry[0:end] 
    
    return endquery

def qry2data(connection, sqlquery):
    #print("before trim:",sqlquery)
    query = trimquery(sqlquery)
    logger.debug(f"trim query is: {query}")
    #print(query)
    sqldata = execute_read_query(connection, str(query))
    #print(sqldata)
    return sqldata


apppy = Flask(__name__)
CORS(apppy)

@apppy.route('/userInput', methods=['POST'])
def handle_json1():
    data = flask.request.json  # request json data (userInput)
    global userInput
    userInput = data.get('bedir')
    return flask.jsonify(data)  # return received json data as response 

@apppy.route('/get-boolean', methods=['GET'])
def get_boolean():
    # This is where you might determine your boolean value, for now, we return True
    result = classifyIfSQL()
    #print(userInput)
    #result = False
    return flask.jsonify(result=result)

@apppy.route('/get-dbstructure', methods=['GET'])
def get_dbstructure():
    # return database structure (table name and column structure)
    structure = get_structure()
    return flask.jsonify(structure = structure)


@apppy.route('/sqlQuery', methods=['POST'])
def handle_json2():
    query = flask.request.json  # request json data (userInput)
    #print("sqlQuery",query)
    
    global sqlqry
    sqlqry = query.get('bedir')
    logger.debug(f"query is: {sqlqry}")
    return flask.jsonify(query)

@apppy.route('/get-data', methods=['GET'])
def get_data():
    sql_data = qry2data(cnx, sqlqry)
    #print("sqldata: ",sql_data)
    logger.info(f"sql data is: {sql_data}")
    return flask.jsonify(result = sql_data)

if __name__ == "__main__":
    cnx = create_connection("localhost", "root", "123456")
    userInput = ''
    sqlqry = None
    apppy.run("127.0.0.1", 6969)
    