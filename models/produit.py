from .models import Model

class Produit(Model):
    def __init__(self, id, nom, prix, categorie_id):
        self.id           = id
        self.nom          = nom
        self.prix         = prix
        self.categorie_id = categorie_id