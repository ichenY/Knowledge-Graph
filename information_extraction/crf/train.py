import pycrfsuite
import spacy
import re
import sys

nlp = spacy.load("en")



def get_data(file):
    data = []
    with open(file, "r", encoding='utf8') as f:
        """
        input: "<tag>w w w w."
        output: list of ([w pos y])
        """
        for course in f.readlines(): 
            sentences = re.split('\<\/\w+\>', course)
            c_data = []
            for sentence in sentences:
                if not sentence.isspace():
                    try:
                        match = re.match('\<\w+\>', sentence.strip())
                        chunk_name = match.group()
                        sentence = sentence[:match.start()]+ sentence[match.end():]
                        docs = nlp(sentence)
                        for token in docs:
                            if token.text != '>':
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


train_data = get_data('train-ucla.txt')
test_data = get_data('test-ucla_tag.txt')
X_train = [get_features(course_doc) for course_doc in train_data]
y_train = [get_labels(course_doc) for course_doc in train_data]

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
X_test = [get_features(course_doc) for course_doc in test_data]
y_test = [get_labels(course_doc) for course_doc in test_data]


tagger = pycrfsuite.Tagger()
tagger.open('ucla.model')
y_pred = [tagger.tag(xseq) for xseq in X_test] 

def report(y_test, y_pred):
    tp = 0
    fp = 0
    fn = 0
    for i in range(len(y_pred)):
        if y_pred[i][0] == y_pred[i][0]:
            tp += 1
        for j in range(1,len(y_pred[i])):
            prev,cur = y_test[i][j-1],y_test[i][j]
            prev_p,cur_p = y_pred[i][j-1],y_pred[i][j]
            if prev != cur:
                if prev == y_pred[i][j-1] and cur == y_pred[i][j]:
                    tp += 1
                elif prev != prev_p or cur != cur_p:
                    fn +=1
            if prev_p != cur_p:
                if prev != prev_p or cur != cur_p:
                    fp += 1 

            if j == len(y_pred[i])-1 and y_pred[i][j] == y_test[i][j]:
                tp += 1

    precision = float(tp)/(tp+fp)
    recall = float(tp)/(tp+fn)
    f1 = 2 * precision * recall / (precision + recall)
    print( "precision : ", precision)
    print( "recall : ",recall)
    print( "f1 : ",f1)
    
report(y_test,y_pred)




