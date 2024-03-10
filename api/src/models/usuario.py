class Usuario:
    
    def __init__(self, email):
        self.email = email
        self.note_list = []

    def getListaNotas(self):
        return self.note_list

    def to_dict (self):
        return {"email" : self.email, "pwd" : self.note_list } 