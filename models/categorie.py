from .models import Model

class Categorie(Model):
    def __init__(self, id, nom):
        self.id = id
        self.nom = nom