from itertools import islice
import sys

from convokit import Corpus, Speaker, Utterance, download
from sentence_transformers import SentenceTransformer, util
import os, json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def transition(inputDir, file):
    """Transitions generated conversations into a easily understood format

    Args:
        inputDir (string): Folderpath
        file (string): Filename

    Returns:
        ConvoKit corpus (object): An object that contains a formatted conversation
    """
    utterances = []
    uttId = 0
    filePath = os.path.join(inputDir, file)

    with open(filePath, "r", encoding="utf-8") as f:
        conversation = json.load(f)

    speakers = {name: Speaker(id=name) for name in conversation.keys()}

    messages = []
    for m1, m2 in zip(conversation["model1"], conversation["model2"]):
        messages.append(("model1", m1))
        messages.append(("model2", m2))

    for speakerId, msg in messages:
        utterances.append(
            Utterance(
                id=str(uttId),
                speaker=speakers[speakerId],
                text=msg,
                conversation_id=file,
                reply_to=None if uttId == 0 else str(uttId - 1)
            )
        )
        uttId += 1

    return Corpus(utterances=utterances)


def score(cxt, history):
    """Scores how likely the response is corresponding to the given contex

    Args:
        cxt (Current utterance): The current utterance in a conversation
        history (Previous utterance compounded): All previous utterances 

    Returns:
        score (float): A scale of 0 - 1 of how likely the response is corresponding to the given contex # https://huggingface.co/microsoft/DialogRPT-human-vs-rand
    """
    histTokens = tokenizer.encode(history)
    cxtTokens = tokenizer.encode(cxt)

    maxHistLen = MAX_LEN - len(cxtTokens) - 1

    if maxHistLen < 0:
        cxtTokens = cxtTokens[:MAX_LEN - 1]
        histTokens = []
    else:
        histTokens = histTokens[-maxHistLen:]

    inputIds = histTokens + [tokenizer.eos_token_id] + cxtTokens
    inputIds = torch.tensor([inputIds])

    with torch.no_grad():
        result = model(inputIds, return_dict=True)

    return torch.sigmoid(result.logits).item()


def semanticScore(cur, prev):
    """ Scores how simmilar the response is corresponding to the given contex

    Args:
        cur (string): Current Utterance
        prev (string): Previous Utterance

    Returns:
        score (float): A scale of 0 - 1 of how likely the response is corresponding to the given contex # https://github.com/huggingface/sentence-transformers
    """
    emb1 = semanticsModel.encode(cur, convert_to_tensor=True)
    emb2 = semanticsModel.encode(prev, convert_to_tensor=True)
    return util.cos_sim(emb1, emb2).item()


def evaluateConversation(corpus):
    """Evaluates each utterance in a conversation

    Args:
        ConvoKit corpus (Object): A convoKit object that contains formatted conversations

    Returns:
        conversationScores (dict): A formatted score of [Pragmatic Score, Semantic Score, utterance]
    """
    conversationScores = {}
    
    for count, conversationName in enumerate(islice(corpus.conversations.keys(), len(corpus.conversations.keys())), 1):
        progress = count / len(corpus.conversations.keys())
        bar = "#" * int(progress * 40)
        sys.stdout.write(f"\r[{bar:<40}] {progress:.1%}")
        sys.stdout.flush()
        
        conv = corpus.get_conversation(conversationName)
        utteranceIds = conv.get_utterance_ids()
        messageScores = []
        history = ""

        firstText = conv.get_utterance(utteranceIds[0]).text
        messageScores.append([None, None, firstText])
        history += " " + firstText
        prevText = firstText

        for i in range(1, len(utteranceIds)):
            uid = utteranceIds[i]
            currentText = conv.get_utterance(uid).text

            pragScore = score(currentText, history)
            semScore = semanticScore(currentText, prevText)

            messageScores.append([pragScore, semScore, currentText])

            history += " " + currentText
            prevText = currentText

        conversationScores[conversationName] = messageScores
    return conversationScores


def writeConvo(convo, outputDir, filename):
    """_summary_

    Args:
        convo (dict): A dictionary containg evaluated data
        outputDir (string): An output Folder
        filename (string): A filename
    """
    filePath = os.path.join(outputDir, filename)
    with open(filePath, "w", encoding="utf-8") as f:
        json.dump(convo, f, indent=4)



# Ask user for folder path
basePath = input("Enter the folder location containing the JSON files: ").strip()
# Ask user for output filename
f = input("Enter output filename (e.g., results.json): ").strip()

# pragmatics model
modelName = "microsoft/DialogRPT-human-vs-rand"
tokenizer = AutoTokenizer.from_pretrained(modelName)
model = AutoModelForSequenceClassification.from_pretrained(modelName)
MAX_LEN = 1024

# semantics model
semanticsModel = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Validate folder
while not os.path.isdir(basePath):
    print("Invalid folder. Please try again.")
    basePath = input("Enter the folder location containing the JSON files: ").strip()
allScores = {}

for filename in os.listdir(basePath):
    fullPath = os.path.join(basePath, filename)

    # Skip non-files
    if not os.path.isfile(fullPath):
        continue

    corpus = transition(basePath, filename)  # Format
    conversationScores = evaluateConversation(corpus)  # Evaluate
    allScores.update(conversationScores)

writeConvo(
    allScores,
    os.path.dirname(os.path.abspath(__file__)),
    f
)