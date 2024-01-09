import json

class LineFlexMessage:
    def __init__(self): pass
    # 
    def json(self, filename):
        with open(f"tmpelates/{filename}.json") as f:
            return json.load(f)
    # 
    def iWantAppointment(self):
        data = self.json('iWantAppointment')