
# coding: utf-8

# In[101]:


import pycrfsuite
import spacy
import re
import sys

nlp = spacy.load("en")

'''
input format: python extract.py <model> <input_file> <output_file_name>

command to run: python extract.py ucla.model test-ucla.txt output.txt
'''

model = sys.argv[1]
input_file = sys.argv[2]
output_file_name = sys.argv[3]

def get_test_data_unlabel(file):
    data = []
    dot = '.'
    with open(file, "r") as f:
        for course in f.readlines():
            sentences = re.split('\.\ ', course.strip())
            for i in range(len(sentences)):
#                 print(sentences[i])
                if sentences[i] == '\n':
                    sentences[i] = ''
                if i != len(sentences)-1:
                        sentences[i] = sentences[i] + dot
                
            c_data = []
            for sentence in sentences:
                if not sentence.isspace():
                    try:
                        docs = nlp(sentence)
                        chunk_name = ''
                        for token in docs:
                            c_data.append((token.text, token.tag_, chunk_name))  
                    except:
                        continue
            data.append(c_data)
        return data



def word2features(doc, i):
    """
    input:
        doc ->list(list[string]): tuples of (words, pos, label)
    output:
        features -> list(string): features of a single word, gotten from last and next word
    """
    word = doc[i][0] #word
    postag = doc[i][1] #tag
    features = [
        'word.lower=' + word.lower(),
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
        'word.isdot=%s' % isdot(word),
        'word.length=' + str(len(word)),
        'postag=%s' % postag,
        'postag[:2]=%s' % postag[:2]
    ]
    
    if i > 0:
        prev_word = doc[i-1][0]
        prev_postag = doc[i-1][1]
        features.extend([
            '-1:word.lower=' + prev_word.lower(),
            '-1:word.isupper=%s' % prev_word.isupper(),
            '-1:word.istitle=%s' % prev_word.istitle(),
            '-1:word.isdigit=%s' % prev_word.isdigit(),
            '-1:word.isdot=%s' % isdot(prev_word),
            '-1:word.length=' + str(len(prev_word)),
            '-1:postag=%s' % prev_postag,
            '-1:postag[:2]=%s' % prev_postag[:2], 
            'last|word=%s|%s' %(prev_word,word)
        ])
    else:
        features.append('BOS')
        
    if i > 1:
        prev_word = doc[i-2][0]
        prev_postag = doc[i-2][1]
        features.extend([
            '-2:word.lower=' + prev_word.lower(),
            '-2:word.length=' + str(len(prev_word)),
            '-2:word.isupper=%s' % prev_word.isupper(),
            '-2:word.istitle=%s' % prev_word.istitle(),
            '-2:word.isdigit=%s' % prev_word.isdigit(),
            '-2:word.isdot=%s' % isdot(prev_word),
            '-2:postag=%s' % prev_postag,
            '-2:postag[:2]=%s' % prev_postag[:2]
        ])

    if i < len(doc)-1:
        next_word = doc[i+1][0]
        next_postag = doc[i+1][1]
        features.extend([
            '+1:word.lower=' + next_word.lower(),
            '+1:word.isupper=%s' % next_word.isupper(),
            '+1:word.istitle=%s' % next_word.istitle(),
            '+1:word.isdigit=%s' % next_word.isdigit(),
            '+1:word.isdot=%s' % isdot(next_word),
            '+1:postag=%s' % next_postag,
            '+1:word.length=' + str(len(next_word)),
            '+1:postag[:2]=%s' % next_postag[:2], 
            'word|next=%s|%s' %(word,next_word), 
        ])
    else:
        features.append('EOS')
        
    if i < len(doc)-2:
        next_word = doc[i+2][0]
        next_postag = doc[i+2][1]
        features.extend([
            '+2:word.lower=' + next_word.lower(),
            '+2:word.length=' + str(len(next_word)),
            '+2:word.isupper=%s' % next_word.isupper(),
            '+2:word.istitle=%s' % next_word.istitle(),
            '+2:word.isdigit=%s' % next_word.isdigit(),
            '+2:word.isdot=%s' % isdot(next_word),
            '+2:postag=%s' % next_postag,
            '+2:postag[:2]=%s' % next_postag[:2]
        ])
    

    return features

def isdot(word):
    return True if '.' in word else False

def get_features(doc):
    """
    input: doc
    output: 
        feature list: list of features by each word
    """
    return [word2features(doc,i) for i in range(len(doc))] 

def get_labels(doc):
    return [label for (token, postag, label) in doc]

def get_token(doc):
    return [token for (token, postag, label) in doc]

    

test_data = get_test_data_unlabel(input_file)

X_test = [get_features(course_doc) for course_doc in test_data]

tagger = pycrfsuite.Tagger()
tagger.open(model)
y_pred = [tagger.tag(xseq) for xseq in X_test] #list[list[string]]




def write_txt(X_test,y_pred,test_data):
#     y_pred_copy = y_pred[:]
    output,wordList = [],[]
    pos = 0
    wordList = [get_token(course_doc) for course_doc in test_data]
    flat_list = [item for sublist in wordList for item in sublist]
#     print(flat_list)
    for i in range(len(y_pred)):
        output.append(y_pred[i][0])
        y_pred[i].append('<>')
        for j in range(1,len(y_pred[i])):
            prev,cur = y_pred[i][j-1],y_pred[i][j] #course i
            if prev != cur:
                output.append(flat_list[pos])
                pos += 1
                prev = prev.replace('<','</')
                cur = cur.replace('<>',' ')
#                 if cur == ' ':
#                     output.append(prev)
#                 else:
                output += prev,cur
            else:
                output.append(flat_list[pos])
                pos += 1
                
        output.append('\n')
    output_result = ' '.join([w for w in output])
#     print(output_result)

    with open(str(output_file_name), "w") as f:
        f.write(output_result)

write_txt(X_test,y_pred,test_data)

