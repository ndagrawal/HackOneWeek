from flask import Flask, request, jsonify
import json
#import csv
#from Query_Syntactical_Title import loadPickledModels, getsimilar
from area_classifier.area_classifier import  predict_area
import logging

logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('logs.csv')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
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
    return json.dumps("deprecated")

import pprint
@app.route("/area", methods=['POST'])
def area():
    pprint.pprint(request)
    queryString = request.json['text']
    prediction = to_full_area_path(predict_area(queryString))
    logger.info(", "+prediction+", "+queryString)
    response = {"area":prediction}
    return json.dumps(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0')