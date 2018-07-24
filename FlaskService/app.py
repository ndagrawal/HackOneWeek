from flask import Flask, request, jsonify
import json
import csv
from TextCleanUtils import clean_text
import pickle
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import preprocessing
from sklearn.linear_model import SGDClassifier

#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn import preprocessing
#from Query_Syntactical_Title import loadPickledModels, getsimilar
#from area_classifier.area_classifier import  predict_area


with open('vso_tfidf.pickle1gram', 'rb') as fw:
    tfidf = pickle.load(fw)

with open('vso_label_encoder', 'rb') as fw:
    le = pickle.load(fw)

with open('sgd-all.pickle', 'rb') as fw:
    model = pickle.load(fw)

logger = logging.getLogger('myapp')
#hdlr = logging.FileHandler('logs.csv')
#formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#hdlr.setFormatter(formatter)
#logger.addHandler(hdlr)

logger.setLevel(logging.INFO)

def loadTfidDict():
    reader = csv.reader(open("tfid.csv"))
    d = {}
    for row in reader:
        d[int(row[0])] = row[1]

    return d

#tfsid = loadTfidDict()
#model, tfidf = loadPickledModels()

app = Flask(__name__)


def to_full_area_path(name):
    if 'WIT' in name:
        return "VSOnline\\VSTS\\Agile\\"+name
    return "VSOnline\\VSTS\\"+name

#def buildItem(wit):
    #id = int(wit[1])
    #distance = wit[2]
    #assignedTo = '' if id not in tfsid else tfsid[id]
    #return {"id": id, "distance": distance, "assignedTo": assignedTo}

@app.route("/similar", methods=['POST'])
def similar_wits():
    #queryString = request.json['text'];
    #logger.info(print("requesting query: "+queryString))
    #similar, candidates = getsimilar(queryString,model, tfidf)
    #response = [buildItem(wit) for wit in similar.values]
    pprint.pprint(request)
    queryString = request.json['text']
    result = mlpipeline(queryString)
    #predictions = getDummyWorkItemPrediction()
    #return predictions.toJSON()

    return get_top5(result)

import pprint
@app.route("/area", methods=['POST'])
def area():
    pprint.pprint(request)
    queryString = request.json['text']
    result = mlpipeline(queryString)
    #print(areapath)
    #prediction = to_full_area_path(predict_area(queryString))
    #logger.info(", "+prediction+", "+queryString)
    #response = {"area":prediction}
    #prediction = getDummyAreaPathPrediction()
    #return prediction.toJSON()
    return get_top5(result)


'''
Machine Learning Pipeline
'''
def mlpipeline(text):
    return clean_text(text, True)

def get_top5(text):
    probs = model.predict_proba(tfidf.transform([text]))
    args = probs.argsort()[0][-5:][::-1]
    areas, probs = le.classes_[model.classes_[args]], probs[0][args]
    resultstring = ""
    for i in range(5):
        resultstring+=" "+str(areas[i])+" "+str(probs[i])
        resultstring+='\n'
    return resultstring

'''
Data Contract for area path
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
Data Contract for workitem.
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
'''
def getDummyWorkItemPrediction():
    workitempredictions = Workitempredictions()
    prediction1 = Workitemprediction(2, 0.75)
    prediction2 = Workitemprediction(1, 0.65)
    workitempredictions.predictions.append(prediction1)
    workitempredictions.predictions.append(prediction2)
    return  workitempredictions

def getDummyAreaPathPrediction():
    areapathprediction = Areapathpredictions()
    apred1 = Areapathprediction("sample", 0.75)
    apred2 = Areapathprediction("sample", 0.9)
    areapathprediction.predictions.append(apred1)
    areapathprediction.predictions.append(apred2)
    return areapathprediction

if __name__ == '__main__':
    app.run(host='0.0.0.0')