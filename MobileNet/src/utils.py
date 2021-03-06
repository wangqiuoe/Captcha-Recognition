from captcha.image import ImageCaptcha
from PIL import Image
import random
import string
from keras import backend as K
import tensorflow as tf
import numpy as np

from config import *

def get_char_length():
    if FLAG_CHAR == 0:
        char_len = CHAR_LEN
    elif FLAG_CHAR == 1:
        char_len = MAX_CHAR_LEN
    else:
        raise ValueError(u'FLAG_CHAR should be 0 or 1')
        char_len = -1
    return char_len
    
def make_rand_char():
    return random.choice(string.ascii_letters+'0123456789')

def make_rand_text(length):
    text = ''
    for i in range(length):
        rand_char = ''
        r_char = make_rand_char()
        rand_char += r_char
        text += rand_char
    return text

def make_rand_image(text):
    image = ImageCaptcha()
    image = Image.open(image.generate(text))
    return image

def char2pos(c):
    if c >= '0' and c <= '9':
        k = ord(c) - ord('0')
    elif c >= 'a' and c <= 'z':
        k = ord(c) - ord('a') + 10
    elif c >= 'A' and c <= 'Z':
        k = ord(c) - ord('A') + 36
    elif c == '' or c == ' ':
        k = 62
    else:
        print ('character not in lists')
    return k

def pos2char(char_idx):
    if char_idx == -1:
        char = ''
    elif char_idx == 62:
        char = ''
    elif char_idx < 10:
        char = chr(int(char_idx + ord('0')))
    elif char_idx < 36:
        char = chr(int(char_idx - 10 + ord('a')))
    elif char_idx < 62:
        char = chr(int(char_idx - 36 + ord('A')))
    else:
        raise ValueError('error')
    return char

def text2index(text):
    index = []
    for i in text:
        text_index = char2pos(i)
        index.append(text_index)
    return index

def index2text(vec):
    text = ''
    for i in vec:
        char_code = pos2char(i)
        text += char_code
    return "".join(text)

def text2vec(text):
    text_len = len(text)
    length = get_char_length()
    
    if text_len != length:
        raise ValueError(u'Text length does not fit')

    vector = np.zeros(length * CHAR_NUM)
    for i in range(length):
        if i < text_len:
            idx = i * CHAR_NUM + char2pos(text[i])
        else:
            idx = i * CHAR_NUM + char2pos('')
        vector[idx] = 1        
    return vector

def vec2text(vec):
    char_pos = vec.nonzero()[0]
    text = []
    for i, c in enumerate(char_pos):
        char_at_pos = i  # c/63
        char_idx = c % CHAR_NUM
        char_code = pos2char(char_idx)
        text.append(char_code)
    return "".join(text)

def pred2text(pred):
    pred = np.array(pred)
    pred = np.reshape(pred,[-1,CHAR_NUM])
    length = pred.shape[0]
    text = []
    for i in range(length):
        pos = np.argmax(pred[i,:])
        text.append(pos2char(pos))
    return "".join(text)

def rgb2gray(rgb):
    gray = np.dot(rgb[...,:3], [0.299, 0.587, 0.114])
    #color = 255 - min(t, 10) * 13 if time_color else 255
    return gray

def accuracy(y_true, y_pred):
    char_len = get_char_length()
    y_true = K.reshape(y_true,[-1,char_len,CHAR_NUM])
    y_pred = K.reshape(y_pred,[-1,char_len,CHAR_NUM])

    class_true = K.argmax(y_true,axis=2)
    class_pred = K.argmax(y_pred,axis=2)
    
    correct_pred = K.cast(K.equal(class_true,class_pred),tf.int32)
    correct_pred = K.sum(correct_pred,axis=1) # for each position
    correct_pred = K.cast(K.equal(correct_pred,char_len),tf.int32)
    correct_pred = K.cast(K.sum(correct_pred),tf.float32)
    
    accuracy = correct_pred / K.cast(tf.shape(y_true)[0],tf.float32)
    return accuracy