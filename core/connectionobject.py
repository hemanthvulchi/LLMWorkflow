class PinConnectionObject():
    def __init__(self):
        self.msg = None
        self.response = None
        self.thread = None
        self.JSONdata = None

    def set_data(self, pJSONdata):
        self.JSONdata = pJSONdata
    
    def get_data(self):
        return self.JSONdata