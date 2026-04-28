import os
import random
from flask import Flask, session, json, jsonify, request, send_from_directory, Response
from flask_cors import CORS
import requests
from ollamaClass import ollamaClass
import threading

m = ollamaClass("gemma3") # If inaccurate may need to swap back to gemma3:12b
m.updatekeepAlive("15m")

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "../client/dist"),
    static_url_path="/"
)
CORS(app, supports_credentials=True)

app.secret_key = os.urandom(32)

try:
    try:
        os.makedirs(os.path.join(os.path.dirname(__file__), "VectorStore1"))
        os.makedirs(os.path.join(os.path.dirname(__file__), "VectorStore2"))

    except Exception as e:
        print(e)

    for f in os.listdir(os.path.join(os.path.dirname(__file__), "VectorStore1")):
        os.remove((os.path.join(os.path.dirname(__file__), "VectorStore1", f)))

    for f in os.listdir(os.path.join(os.path.dirname(__file__), "VectorStore2")):
        os.remove((os.path.join(os.path.dirname(__file__), "VectorStore2", f)))     
except Exception as e:
    print(e)

global Running, thread
Running = False
thread = None

def updateTurn(turn, num):
    return (turn + 1) % num

def setModels(Profiles):
    models = []
    for profile in Profiles:
        model = ollamaClass(profile["modelName"])
        model.jsonExtract(profile)  
        models.append(model)

    return models

def getResponse(model):
    model.generateResponse()
    return model.getResponseMessage().content

def updateModels(turn, models, response):
    for i, model in enumerate(models):
        if turn != i:
            model.updateContent(f"{response}")
            model.updateContext(f"{model.role}: {response}")

def generate(profiles, turn=0, agentClass=["agent1Bubble", "agent2Bubble"]):
    models = setModels(profiles)
    while True:
        response = getResponse(models[turn])
        updateModels(turn, models, response)
        yield f"{json.dumps({'status':'Success','data':{'modelName':models[turn].modelName,'modelClass':agentClass[turn],'text':response}})}\n\n"
        turn = updateTurn(turn, len(agentClass))

def sim(profiles):
    return generate(profiles)

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/conversation", methods=['POST'])
def conversate():
    
    global Running, thread
    try:
        
        profiles = request.get_json()["profiles"]
        if Running and thread is not None:
            thread.join()
        thread = threading.Thread(target=sim, args=(profiles,))
        thread.start()
        Running = True
        if thread:
            return Response(generate(profiles), content_type='text/event-stream')
    except Exception as e:
        return jsonify({"status": "Failure", "data": str(e)}), 400


@app.route("/validJSONS", methods=['GET', 'POST']) 
def validateJSON():
    try:
        defaultProfile = {
            "modelName": "",
            "role": 'user',
            "prompt": '',
            "system": '',
            "suffix": 'Answer as a JSON Numerical values must be between 0.0 and 1.0.',
            "raw": True,
            "stream": False,
            "keepAlive": 5,
            "images": [],
            "context": '',

            "seed": 0,
            "temperature": 1.0,
            "topK": 50,
            "minP": 0.0,
            "maxP": 1.0,
            "stop": '',
            "numCTX": 0.0,
            "numPredict": 0.0,
            
            "format": [
                {
                "id": 0,
                "name": "",
                "min": 0,
                "max": 0
                }
            ]
        }
        
        modelCount = 1
        models = [
            "qwen3-vl",
            "qwen3.5",
            "glm-4.7-flash",
            "qwen3-next",
            "nemotron-3-nano",
            "gpt-oss-safeguard",
            "qwen3",
            "gpt-oss",
            "magistral",
            "deepseek-v3.1",
            "deepseek-r1"
        ]
        Profiles = request.get_json()["profiles"]
        for profile in Profiles:
            if 'modelName' not in profile.keys(): # Check if models are present
                return jsonify({"status": f"Failure model {modelCount}, No model", "data": False}), 400
            
            if not isinstance(profile['modelName'], str) or profile['modelName'] not in models: # Checks if models are present
                return jsonify({"status": f"Failure model {modelCount}, Invalid {profile['modelName']}", "data": False}), 400
            
            for key in profile.keys():
                if key not in defaultProfile.keys(): # Invalid key
                    return jsonify({"status": f"Failure model {modelCount}, Invalid Field {key}", "data": False}), 400
                if isinstance(profile[key], type(defaultProfile[key])):
                    continue
                elif isinstance(profile[key], (int, float)) and isinstance(defaultProfile[key], (int, float)):
                    continue
                else:
                    return jsonify({"status": "Invalid Json Key Datatype", "reason": f"Key {key} has wrong type"}), 422

            for field in profile['format']:
                if set(field) != set(defaultProfile['format'][0]): # Invalid field structure
                    return jsonify({"status": f"Failure model {modelCount}, Invalid Field {field} structure", "data": False}), 400
                
                for key in field.keys():
                    if field["name"] == "":
                        return jsonify({"status": f"Failure model {modelCount}, Empty Field {field} name", "reason": "Field keys mismatch"}), 400

                    if type(field[key]) != type(defaultProfile["format"][0][key]): # Field has invalid dataType
                        return jsonify({"status": f"Failure model {modelCount}, Invalid Field {field} dataType", "reason": "Field keys mismatch"}), 400
                    
            modelCount += 1
        return jsonify({"status": f"Success", "data": True}), 200
    except Exception as e:
        return jsonify({"status": f"Failure model {modelCount}", "data": False}), 400


@app.route("/ImageUpload", methods=['POST']) 
def imageParse():
        try:
            # Source - https://stackoverflow.com/a
            # Posted by robru, modified by community. See post 'Timeline' for change history
            # Retrieved 2025-12-26, License - CC BY-SA 3.0
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), request.files['imageUpload'].filename)
            request.files['imageUpload'].save(path)

            return jsonify({"status": "Success", "data": path}), 200
        except Exception as e:
            return jsonify({"status": "Failure", "reason": str(e)}), 400

@app.route('/JSONParse', methods=['POST'])
def jsonParse():
    #A valid Default profile
    profile = {
            "modelName": "",
            "role": 'user',
            "prompt": '',
            "system": '',
            "suffix": 'Answer as a JSON Numerical values must be between 0.0 and 1.0.',
            "raw": True,
            "stream": False,
            "keepAlive": 5,
            "images": [],
            "context": '',

            "seed": 0,
            "temperature": 1.0,
            "topK": 50,
            "minP": 0.0,
            "maxP": 1.0,
            "stop": '',
            "numCTX": 0.0,
            "numPredict": 0.0,

            "format": [
                {
                "id": 0,
                "name": "",
                "min": 0,
                "max": 0
                }
            ]
    }
    
    if 'jsonFile' not in request.files:
        return jsonify({"status": "Failure", "reason": "No file uploaded"}), 404

    file = request.files['jsonFile']

    try:
        #Should allow JSONs with missing fields:
            #Not Allowed
            #Improper fields
            #Invalid field types
        
        jsonData = json.load(file.stream)
        # Check all keys are legal
        for key, value in jsonData.items():
            if key not in profile:
                return jsonify({"status": "Invalid Json Field", "reason": f"Unexpected key: {key}"}), 422
            if isinstance(value, type(profile[key])):
                continue
            elif isinstance(value, (int, float)) and isinstance(profile[key], (int, float)):
                continue
            else:
                return jsonify({"status": "Invalid Json Key Datatype", "reason": f"Key {key} has wrong type"}), 422
        
        #if fields are included
        if "format" in jsonData.keys():
            # for each field check the set of the field is a valid format
            for field in jsonData["format"]:
                if set(field.keys()) == set(profile["format"][0].keys()):
                    #check if the fields fields datatypes are equivalent
                    for key in field.keys():
                        if type(field[key]) != type(profile["format"][0][key]):
                            return jsonify({"status": "Invalid Json Field Datatype", "reason": "Field keys mismatch"}), 422
                else:
                    return jsonify({"status": "Invalid Json Field", "reason": f"Field {key} has wrong type"}), 422

        return jsonify({"status": "Success", "data": jsonData}), 200
    except Exception as e:
        return jsonify({"status": "Failure", "reason": str(e)}), 401
    
@app.route('/TXTParse', methods=['POST'])
def textParse():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "Failure", "reason": "No file part in request"}), 400

        file = request.files['file']
        text = file.read().decode("utf-8")
        lines = text.split('\n')
    
        return jsonify({"status": "Success", "data": lines}), 200
    except Exception as e:
        return jsonify({"status": "Failure", "reason": str(e)}), 401
    
@app.route('/JSONTXTParse', methods=['POST'])
def jsontxtParse():
    if 'jsonFile' not in request.files:
        return jsonify({"status": "Failure", "reason": "No file uploaded"}), 404

    file = request.files['jsonFile']

    try:
        TXTjson = json.load(file.stream)
        for key, element in TXTjson.items():
            if set(TXTjson[key].keys()) != set(["name", "value", "fieldType", "options"]):
                return jsonify({"status": "Failure", "reason": "Error in JSON Keys"}), 400
            if (TXTjson[key]["name"] is not None
                and TXTjson[key]["value"] is not None
                and TXTjson[key]["fieldType"] in ("Text", "Drop")
                and (TXTjson[key]["options"] is None or isinstance(TXTjson[key]["options"], list))):
                pass
            else:
                return jsonify({"status": "Failure", "reason": "Error in JSON fields"}), 400
        return jsonify({"status": "Success", "data": TXTjson}), 200
    except Exception as e:
        return jsonify({"status": "Failure", "reason": str(e)}), 400
    
@app.route('/PDFCheck1', methods=['POST'])
def PDFCheck1():
    try:
        if 'Pdf' not in request.files:
            return jsonify({"status": "Failure", "reason": "No file uploaded"}), 404

        path = os.path.join(os.path.dirname(__file__), "VectorStore1", request.files['Pdf'].filename)

        if path.endswith(".txt") or path.endswith(".pdf") or path.endswith(".PDF"):
            request.files['Pdf'].save(path)
            return jsonify({"status": "Success", "data": str(request.files['Pdf'].filename)}), 200
        else:
            return jsonify({"status": "Failure", "reason": "Invlaid"}), 400

    except Exception as e:
        return jsonify({"status": "Failure", "reason": str(e)}), 400
    
@app.route('/PDFCheck2', methods=['POST'])
def PDFCheck2():
    try:
        if 'Pdf' not in request.files:
            return jsonify({"status": "Failure", "reason": "No file uploaded"}), 404
        
        path = os.path.join(os.path.dirname(__file__), "VectorStore2", request.files['Pdf'].filename)

        if path.endswith(".txt") or path.endswith(".pdf") or path.endswith(".PDF"):
            request.files['Pdf'].save(path)
            return jsonify({"status": "Success", "data": str(request.files['Pdf'].filename)}), 200
        else:
            return jsonify({"status": "Failure", "reason": str(e)}), 400
 
    except Exception as e:
        return jsonify({"status": "Failure", "reason": str(e)}), 400

@app.route('/promptBuild', methods=['POST'])
def promptBuild():
    try:
        if 'prompt' not in request.files:
            return jsonify({"status": "Failure", "reason": "No file uploaded"}), 404

        data = request.files['prompt']
        file = json.load(data)
        model="gemma3:12b"
        m = ollamaClass(model)

        prompt = """
        You are to take any information I provide and rewrite it as a user persona.

        Then rewrite it into a natural-language persona sentence using the same fields.
                        
        Example 
        Name:David, Age:42 -> You are a user named David, you are 42.

        Rules:
        - Do not add extra formatting.
        - Do not add explanations.
        - Only output the persona sentence with all the input.
        - Do not add extra details or values.

        Input:
        """
        if len(file.keys()) <= 0:
            return jsonify({"status": "Failure", "reason": "No Fields"}), 404
        
        for key in file.keys():
            prompt = f"{prompt}\n {file[key]["name"]}:{file[key]["value"]}"
        
        m.updateContent(prompt)
        m.generateResponse()
        response = m.getResponseMessage()["content"]
        
        return jsonify({"status": "Success", "data": response}), 200
    except Exception as e:
        return jsonify({"status": "Failure", "reason": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
