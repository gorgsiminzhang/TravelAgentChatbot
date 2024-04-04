from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models import KeyedVectors

from pathlib import Path
import numpy as np
# 当前脚本所在目录
current_dir = Path(__file__).parent
word2vec_output_file = current_dir /'glove.6B.300d.txt.word2vec'
# 加载转换后的文件
model = KeyedVectors.load_word2vec_format(word2vec_output_file, binary=False)

keywords1 = ["price", "City", "Country", "StartDate","EndDate","PackageType","Flights"," Hotel"]
threshold = 0.5 
userInput = "What's the price to Tokyo"
#userInput = "what's the weather?"

# 定义计算平均向量的函数
def average_vector(words):
    # 过滤掉模型词汇表中不存在的词
    valid_words = [word for word in words if word in model]
    if not valid_words:
        return None
    # 计算平均向量
    return np.mean([model[word] for word in valid_words], axis=0)

# 函数：计算余弦相似度
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

userVec = average_vector(userInput)
#keyVec = average_vector(keywords1)
#similarity = np.dot(userVec, keyVec) / (np.linalg.norm(userVec ) * np.linalg.norm(keyVec))
not_included = [word for word in keywords1 if word not in model.key_to_index]
similarities = [cosine_similarity(userVec, model[keyword]) for keyword in keywords1 if keyword in model]
print(similarities)