import json
import csv
from TextCleanUtils import clean_text
import pickle
import logging
import pprint
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import preprocessing
from sklearn.linear_model import SGDClassifier

'''
=========== Configure Logger ===========
'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('areaclassifier.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

'''
=========== INTIATIZE APP ===========
'''

app = Flask(__name__)

'''
=========== REST APIS ===========
'''
@app.route("/similar", methods=['POST'])
def similar_wits():
    queryString = request.json['text']
    logger.info("Method:POST , Route:/area , Request:" + queryString)
    queryString = request.json['text']
    result = mlpipeline(queryString)
    logger.info("Route :/similar Response:+" + result)
    ##TODO : This is pending item....
    return "pending"

@app.route("/area", methods=['POST'])
def area():
    pprint.pprint(request)
    queryString = request.json['text']
    logger.info("Method:POST , Route:/area , Request:"+queryString)
    cleantext = mlpipeline(queryString)
    result = get_top5(cleantext).toJSON()
    logger.info("Route :/area Response:+"+result)
    return result

'''
=========== REST APIS ===========
'''

def mlpipeline(text):
    return clean_text(text, True)

with open('vso_tfidf.pickle1gram', 'rb') as fw:
    tfidf = pickle.load(fw)

with open('vso_label_encoder', 'rb') as fw:
    le = pickle.load(fw)

with open('sgd-all.pickle', 'rb') as fw:
    model = pickle.load(fw)

def get_top5(text):
    probs = model.predict_proba(tfidf.transform([text]))
    args = probs.argsort()[0][-5:][::-1]
    areas, probs = le.classes_[model.classes_[args]], probs[0][args]
    predictions = Areapathpredictions()
    for i in range(5):
        x = Areapathprediction(areas[i], probs[i])
        predictions.predictions.append(x)
    return predictions

'''
===========  Data Contract for area path =========== 
'''
class Areapathprediction:
    def __init__(self, areapathname, probability):
        self.areapathname = areapathname
        self.probability = probability

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Areapathpredictions:
    def __init__(self):
        self.predictions = []

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

'''
=========== Data Contract for workitem =========== 
'''
class Workitemprediction:
    def __init__(self, workitemid, probability):
        self.workitemid = workitemid
        self.probability = probability

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class Workitempredictions:
    def __init__(self):
        self.predictions = []

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

'''
To be removed methods.


def getDummyWorkItemPrediction():
    workitempredictions = Workitempredictions()
    prediction1 = Workitemprediction(2, 0.75)
    prediction2 = Workitemprediction(1, 0.65)
    workitempredictions.predictions.append(prediction1)
    workitempredictions.predictions.append(prediction2)
    return workitempredictions

def getDummyAreaPathPrediction():
    areapathprediction = Areapathpredictions()
    apred1 = Areapathprediction("sample", 0.75)
    apred2 = Areapathprediction("sample", 0.9)
    areapathprediction.predictions.append(apred1)
    areapathprediction.predictions.append(apred2)
    return areapathprediction
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0')
