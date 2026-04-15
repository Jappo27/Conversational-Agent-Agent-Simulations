import json
import logging
import os
from ollama import chat
from ollama import ChatResponse
import ollama
from pydantic import BaseModel, confloat, create_model

class Options(BaseModel):
    #https://docs.ollama.com/api/generate#body-suffix
    
    seed: int | None # Random seed used for reproducible outputs

    temperature: float | None  # Controls randomness in generation (higher = more random)
    top_k: int | None # Limits next token selection to the K most likely
    top_p: float | None  #Cumulative probability threshold for nucleus sampling
    min_p: float | None  # Minimum probability threshold for token selection
    stop: str | None  #Stop sequences that will halt generation
    num_ctx: int | None  #Context length size (number of tokens)
    num_predict: int | None  # Maximum number of tokens to generate


class Format(BaseModel):
    response: str #The prompt sent to the opposing agent

    def addField(self, fieldName, upperBound, lowerBound):
        fieldName: confloat(ge=upperBound, le=lowerBound) # pyright: ignore[reportInvalidTypeForm]

    
class ollamaClass():
    #https://docs.ollama.com/api#generate-a-completion
    def __init__(self, model):
        self.model = self.updateModel(model) # (required) the model name
        self.modelName = model
        self.role = 'user' # the role of the message, either system, user, assistant, or tool
        self.prompt = None #the prompt to generate a response for
        self.suffix = None # the text after the model response
        self.images = None # (optional) a list of base64-encoded images (for multimodal models such as llava)
        self.tool_calls = None # (optional): a list of tools in JSON that the model wants to use
        
        #self.tools = None
        self.format = None # the format to return a response in. Format can be json or a JSON schema
        self.options = Options.model_json_schema() # additional model parameters listed in the documentation for the Modelfile such as temperature
        self.system = None # system message to (overrides what is defined in the Modelfile)
        self.template = None # the prompt template to use (overrides what is defined in the Modelfile)
        self.stream = False # if false the response will be returned as a single response object, rather than a stream of objects
        self.raw = False #  if true no formatting will be applied to the prompt. You may choose to use the raw parameter if you are specifying a full templated prompt in your request to the API
        self.keepAlive = '5m' # controls how long the model will stay loaded into memory following the request (default: 5m)
        self.context = [] #  (deprecated): the context parameter returned from a previous request to /generate, this can be used to keep a short conversational memory
                
        self.response = None
        
    def dictify(self):
        #Convert object attributes to a dictionary.
        return self.__dict__
        
    def jsonExtract(self, json):
        #fill fields from JSON
        try:
            # Really ugly but works
            # Refactor should include updating each field by key name, and options being a su directory maybe?

            #Super ugly but i will totally refactor later
            if "modelName" in json.keys():
                self.updateModel(json["modelName"])
            if "role" in json.keys():
                self.updateRole(json["role"])
            if "prompt" in json.keys():
                self.updateContent(json["prompt"])
            if "system" in json.keys():
                self.updateSystem(json["system"])
            if "suffix" in json.keys():
                self.updateSuffix(json["suffix"])
            if "raw" in json.keys():
                self.updateRaw(json["raw"])
            if "stream" in json.keys():
                self.updateStream(json["stream"])
            if "keepAlive" in json.keys():
                self.updatekeepAlive(json["keepAlive"])
            if "images" in json.keys():
                self.updateImages(json["images"])
            if "context" in json.keys():
                self.updateContext(json["context"])

            if "seed" in json.keys():
                self.updateOptionsSeed(json["seed"])
            if "temperature" in json.keys():
                self.updateOptionsTemperature(json["temperature"])
            if "topK" in json.keys():
                self.updateOptionsTopK(json["topK"])
            if "minP" in json.keys():
                self.updateOptionsTopP(json["minP"])
            if "maxP" in json.keys():
                self.updateOptionsMinP(json["maxP"])
            if "stop" in json.keys():
                self.updateOptionsStop(json["stop"])
            if "numCTX" in json.keys():
                self.updateOptionsNumCtx(json["numCTX"])
            if "numPredict" in json.keys():
                self.updateOptionsNumPredict(json["numPredict"])

            if "format" in json.keys():
                self.updateFormat(json["format"])

            return True
        except:
            return False


    def jsonify(self, filename):
        #Export object as JSON string.
        if filename:
            with open(filename, "w") as f:
                json.dump(self.dictify(), f, indent=4)


    def generateResponse(self):
        # Generates a response if a valid model is loaded
        if self.model is not None and self.prompt is not None:
            response = chat(
                model=self.model,
                messages=[
                    {"role": self.role, "content": self.system},
                    {"role": self.role, "content": self.prompt},
                ],
                options=self.options,
            )
            self.response = response

    def updateSuffix(self, suffix):
        #If suffix is a str update suffix
        if type(suffix) == str:
            self.suffix = suffix
            return suffix
        return None
            
    def updateModel(self, model='None'):
        #Attempts to establish a connection with models
        try:
            ollama.chat(model)
            return model
        except ollama.ResponseError as e:
            print('Error:', e.error)
            if e.status_code == 404:
                try:
                    ollama.pull(model)
                    return model
                except ollama.ResponseError as e:
                    print('Error:', e.error)
        return None
    
    def updateContent(self, prompt):
        #If prompt is a str update Prompt
        if type(prompt) == str:
            self.prompt = prompt
            return prompt
        return None
    
    def updateImages(self, Images):
        #Checks if Images is in a list and all elements area string, then updates object
        if type(Images) == list:
            for image in Images:
                if type(image) != str:
                    return None
        self.images = Images
            
    """def updateTools(self, file_path):
        return self.loadJsonFile(file_path)"""
        
    def updateFormat(self, FormatList):
        #Updates Format
        format = {}
        for field in FormatList:
            format[field["name"]] = (confloat(ge=field["min"], le=field["max"]), ((field["max"]-field["min"])//2))

        Format = create_model('Foo', **format)
        self.format = Format.model_json_schema()
    
    def updateOptions(self):
        #Updates Options
        self.options = Options.model_json_schema()

    def updateOptionsSeed(self, seed):
        if self.options and type(seed) == int:
            self.options["properties"]["seed"] = seed # Random seed used for reproducible outputs

    def updateOptionsTemperature(self, temperature):
        if self.options and type(temperature) == float and 2 > temperature > 0:
            self.options["properties"]["temperature"] = temperature # Controls randomness in generation (higher = more random)

    def updateOptionsTopK(self, top_k):
        if self.options and type(top_k) == int and 100 > top_k > 0:
            self.options["properties"]["top_k"] = top_k # Limits next token selection to the K most likely

    def updateOptionsTopP(self, top_p):
        if self.options and type(top_p) == float and 1 > top_p > 0:
            self.options["properties"]["top_p"] = top_p # Cumulative probability threshold for nucleus sampling

    def updateOptionsMinP(self, min_p):
        if self.options and type(min_p) == float and 1 > min_p > 0:
            self.options["properties"]["min_p"] = min_p # Minimum probability threshold for token selection

    def updateOptionsStop(self, stop):
        if self.options and type(stop) == str:
            self.options["properties"]["stop"] = stop # Stop sequences that will halt generation

    def updateOptionsNumCtx(self, num_ctx):
        if self.options and type(num_ctx) == int and 8192 > num_ctx > 2048:
            self.options["properties"]["num_ctx"] = num_ctx # Context length size (number of tokens)

    def updateOptionsNumPredict(self, num_predict):
        if self.options and type(num_predict) == int:
            self.options["properties"]["num_predict"] = num_predict # Maximum number of tokens to generate

    def updateSystem(self, Instruction):
        #Checks if System is in a valid format and updates object
        if type(Instruction) == str:
            self.system = Instruction
            return Instruction
        return None
            
    def updateTemplate(self, str):
        #Updates template
        if str:
            self.template = str
    
    def updateRole(self, role):
        #Checks if role is in a valid choice and updates object 
        #Models can support specialised roles in agent creation (This is not currently Supported)
        if role in ['system', 'user', 'assistant', 'tool']:
            self.role = role
            return role
        return None

    def updateStream(self, state):
        #Checks if state is in a valid format and updates object
        if type(state) == bool:
            self.stream =  state
            return state
        return None
        
    def updateRaw(self, state):
        #Checks if state is in a valid format and updates object
        if type(state) == bool:
            self.raw =  state
            return state
        return None
            
    def updatekeepAlive(self, time):
        #Checks if time is in a valid format and updates object
        try:
            if time == 0:
                self.keepAlive = time
                return time
            if (type(int(time[:-1])) == int and time[-1:] == 'm'):
                self.keepAlive = time
                return time
        except:
            return None
            
            
    def updateContext(self, context):
        if type(context) == list:
            self.context = context
            return context
        return None

    def getModel(self):
        return self.model
    
    def getPrompt(self):
        return self.prompt
    
    def getSuffix(self):
        return self.suffix
    
    def getImages(self):
        return self.images
    
    def getFormat(self):
        return self.format
    
    def getOptions(self):
        return self.options
    
    def getSystem(self):
        return self.system
    
    def getTemplate(self):
        return self.template
    
    def getStream(self):
        return self.stream
    
    def getRaw(self):
        return self.raw
    
    def getKeepAlive(self):
        return self.keepAlive
    
    def getContext(self):
        #an encoding of the conversation used in this response, this can be sent in the next request to keep a conversational memory
        return self.context
    
    def getReseponse(self):
        #empty if the response was streamed, if not streamed, this will contain the full response
        return self.response
    
    def getResponseMessage(self):
        #contains response data
        return self.response['message']
    
    def getFormattedResponse(self):
        if self.format:
            return Format.model_validate_json(self.response.message.content)
    
    def getTotalDuration(self):
        #time spent generating the response
        return self.response.total_duration
    
    def getLoadDuration(self):
        #time spent in nanoseconds loading the model
        return self.response.load_duration
    
    def getPromptEvalCount(self):
        #number of tokens in the prompt
        return self.response.prompt_eval_count
    
    def getEvalCount(self):
        #number of tokens in the response
        return self.response.eval_count
    
    def getPromptEvalDuration(self):
        #time in nanoseconds spent generating the response
        return self.response.eval_duration
    
    def getCreatedAt(self):
        #time agent was created
        return self.response.created_at
    
    def getDone(self):
        #returns boolean if response is returned
        return self.response.done
    
    def getList():
        #List models that are available locally.
        ollama.list()
    
    def getModelInfo(self):
        #Show information about a model including details, modelfile, template, parameters, license, system prompt.
        ollama.show(self.model)
    