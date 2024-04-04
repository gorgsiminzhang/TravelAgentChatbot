from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models import KeyedVectors
import os
from pathlib import Path

# 当前脚本所在目录
current_dir = Path(__file__).parent

print(os.getcwd())
# 将GloVe格式转换为Word2Vec格式

glove_input_file = current_dir / 'glove.42B.300d.txt'
word2vec_output_file = current_dir /'glove.42B.300d.txt.word2vec'
glove2word2vec(glove_input_file, word2vec_output_file)