
import json

class JsonDict(dict):
    def __str__(self):
        return json.dumps(self)

class JsonList(list):
    def __str__(self):
        return json.dumps(self)

