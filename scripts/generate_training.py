import json


def get_entities(args,text):
    
    found = False
    entities = []
    for arg in args:
        entity = dict()
        if arg['key'] == "dst_city":
            entity['entity'] = "To"
        elif arg['key'] == "or_city":
            entity["entity"] = "From"
        elif arg['key'] == "budget":
            entity["entity"] = "budget"
        elif arg['key'] == "str_date":
            entity["entity"] = "datetimeV2"
        elif arg['key'] == "end_date":
            entity["entity"] = "datetimeV2"


        if arg['key'] in ["dst_city","or_city","budget","str_date","end_date"] and 'val' in arg.keys():
            startPos, endPos = get_location(text,arg["val"])
            #print("Searching ",arg['val'])
            entity["startPos"] = startPos
            entity["endPos"] = endPos
            #print("Start pos",startPos, " end pos ",endPos)
            if startPos != -1 and endPos !=-1:
                found = True
                entities.append(entity)

    if not found:
        return []

    return entities

def get_location(text,needle):

    start = text.find(needle)
    end = start + len(needle)-1

    return start,end

def parse_file(filename):
    
    print("Reading :",filename)
    turn_processed = 0

    with open(filename) as json_file:
        data = json.load(json_file)
        for user in data:
            #print('user_id: ' + user['user_id'])
            for turn in user['turns']:
                
                labels = turn['labels']
                acts = labels['acts']
                
                intent_found = False
                entities = []
                intent = "None"
                for act in acts:
                    args = act['args']

                    entities = get_entities(args,turn['text'])
                    
                    for arg in args:
                        if arg['key']=='intent':
                            turn_processed +=1
                            intent_found = True

                            #if arg['val']=='book':
                            
                
                if intent_found:
                    if len(entities)>0:
                        intent = "BookFlight"
                    else:
                        intent = "None"
                    """if turn_processed == 24:
                        print(turn_processed," ",turn['text'])
                        print(turn)
                        print(entities)
                        exit()                    """
                    turn_obj = dict()
                    turn_obj['text'] = turn['text']
                    turn_obj['entities'] = entities
                    turn_obj['intent'] = intent
                    turn_list.append(turn_obj)

                #if turn_processed>3:
                #    return turn_list
    return turn_list

def get_luis_header():
    header = dict()
    header['luis_schema_version'] = "3.2.0"
    header['versionId'] = "0.1"
    header['name'] = "FlightBooking"
    header['desc'] = "Luis Model for CoreBot"
    header['culture'] = "en-us"
    header['tokenizerVersion'] = "1.0.0"

    return header

def write_result(filename,data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def get_utterances(turns):

    utterances = list()

    for i,turn in enumerate(turns):

        utterance = dict()
        utterance["text"] = turn['text']
        utterance["intent"] = turn['intent']
        utterance["entities"] = turn['entities']
        utterance["index"] = i

        utterances.append(utterance)

    return utterances

def get_intents():

    intents = list()
    intent_names = ['BookFlight','None']
    #,'Cancel','None','Welcome'
    for name in intent_names:

        intent = dict()
        intent["name"] = name

        intents.append(intent)

    return intents


turn_list = []


filename = '../data/frames.json'
turns = parse_file(filename)
intents = get_intents()
utterances = get_utterances(turns)
header = get_luis_header()

obj = header
obj["intents"] = intents

obj["entities"] = [
    {"name":"budget","role":[],"features":"price,number"},
    {"name":"startDate","role":[],"features":"datetimeV2"},
    {"name":"endDate","role":[],"features":"datetimeV2"}
]
obj["composites"] = [
    {"name":"From","children":["Airport"],"roles":[]},
    {"name":"To","children":["Airport"],"roles":[]}
]

sublists = [
    {
        "canonicalForm": "Paris",
        "list": [
        "paris",
        "cdg"
        ]
    },
    {
        "canonicalForm": "London",
        "list": [
        "london",
        "lhr"
        ]
    },
    {
        "canonicalForm": "Berlin",
        "list": [
        "berlin",
        "txl"
        ]
    },
    {
        "canonicalForm": "New York",
        "list": [
        "new york",
        "jfk"
        ]
    },
    {
        "canonicalForm": "Seattle",
        "list": [
        "seattle",
        "sea"
        ]
    }
]

obj["closedLists"] = [{"name":"Airport","subLists":sublists,"roles":[]}]
obj["patternAnyEntities"] = []
obj["regex_entities"] = []
obj["prebuiltEntities"] = [
    {"name":"datetimeV2","roles":[]},
    {"name":"number","roles":[]},
    {"name":"money","roles":[]}]
obj["model_features"] = []
obj["regex_features"] = []
obj["patterns"] = []
obj["utterances"] = utterances
obj["settings"] = []

write_result('../cognitiveModels/Booking4Luis.json',obj)

