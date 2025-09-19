from models.produit import Produits
from models.categorie import Categories
import urllib.parse
from datetime import datetime
import locale

class ProduitController(object):
    @staticmethod
    async def __load(send, filename, dico=None):
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
        
        if dico:
            for key, value in dico.items():
                placeholder = "{{ " + str(key) + " }}"
                html = html.replace(placeholder, str(value))
        
        await send({
            'type' : 'http.response.start',
            'status' : 200,
            'headers' : [(b'content-type', b'text/html')]
        })

        await send({
            'type' : 'http.response.body',
            'body' : html.encode()
        })



    @staticmethod
    async def index(scope, receive, send):
        # last = Produit.lastId() + 1
        # dics = {"numero" : last}
        locale.setlocale(locale.LC_TIME, 'french')
        date_sys = datetime.today()
        aujourd_hui = date_sys.strftime('%A %d %B %Y')
        produit = Produits.getAllJoin(
            joins=[("categories", "produits.categorie_id = categories.id_categories")],
            colonne=[("produit.nom", "produit.prix", "produits.nom as nomC", "produits.id_produits")]
        )

        countProduit = Produits.count()[0]
        countCategorie = Categories.count()[0]
        list_produit = ""
        for p in produit:
            list_produit += f"""
                <tr>
                    <td>{p['id_produits']}</td>
                    <td>{p['nomP']}</td>
                    <td>{p['prix']} Ariary</td>
                    <td>{p['nom']} </td>
                </tr>
            """
        context = {
            "aujourd_hui" : aujourd_hui,
            "countProduit" : countProduit,
            "countCategorie" : countCategorie,
            "produit" : list_produit
        }
        await __class__.__load(send, "views/dashboard.html", context)
    

    @staticmethod
    async def error404(scope, receive, send):
        await __class__.__load(send, "views/error404.html")
        # assert scope['type'] == 'http'

        # with open("views/error404.html", "r", encoding="utf-8") as f:
        #     html = f.read()
        
        # await send({
        #     'type' : 'http.response.start',
        #     'status' : 200,
        #     'headers' : [(b'content-type', b'text/html')]
        # })

        # await send({
        #     'type' : 'http.response.body',
        #     'body' : html.encode()
        # })
    
    @staticmethod
    async def opInsert(scope, receive, send):
        event = await receive()
        body = event.get("body", b'')
        dico = urllib.parse.parse_qs(body.decode())

        nom    = dico.get("nom", [""])[0]
        prix    = dico.get("prix", [""])[0]
        categorie = dico.get("categorie", [""])[0]
        Produits.insert(nom, prix, categorie)

        await send({
            "type": "http.response.start",
            "status": 302,
            "headers": [(b"Location", b"/listProduit")]
        })
        await send({
            "type": "http.response.body",
            "body": b""
        })
        
    
    @staticmethod
    async def produitInsert(scope, receive, send):
        last_id = Produits.lastId() + 1
        categorie = Categories.getAll()
        options = ""

        for c in categorie:
            options += f'<option value="{c["id_categories"]}">{c["nom"]}</option>'
        context = {
            "last_id" : last_id,
            "options_categorie": options,
            }
        await __class__.__load(send, "views/produit/insert.html", context)
    
    @staticmethod
    async def listProduit(scope, receive, send):
        produit = Produits.getAllJoin(
            joins=[("categories", "produits.categorie_id = categories.id_categories")],
            colonne=[("produit.nom", "produit.prix", "produits.nom as nomC", "produits.id_produits")]
        )

        list_produit = ""
        for p in produit:
            list_produit += f"""
                <tr>
                    <td>{p['id_produits']}</td>
                    <td>{p['nomP']}</td>
                    <td>{p['prix']} Ariary</td>
                    <td>{p['nom']} </td>
                    <td width = 200 class="action">
                        <form action="/opdeleteProduit" method="post">
                            <input type="hidden" name="id" id="" value="{p['id_produits']}">
                            <button type="submit">Supprimer</button>
                        </form>
                        <button class="editBtn"
                                data-id="{p['id_produits']}"
                                data-nom="{p['nomP']}"
                                data-prix="{p['prix']}">
                            Modifier
                        </button>
                    </td>
                </tr>
            """
        context = {"list_produit" : list_produit}
        await __class__.__load(send, "views/produit/read.html", context)
    
    @staticmethod
    async def deleteProduit(scope, receive, send):
        try:
            event = await receive()
            body = event.get("body", b'')
            dico = urllib.parse.parse_qs(body.decode())

            id    = dico.get("id", b"")
            Produits.delete(id)

            await send({
                "type": "http.response.start",
                "status": 302,
                "headers": [(b"Location", b"/listProduit")]
            })
            await send({
                "type": "http.response.body",
                "body": b""
            })
        except Exception as e:
            # Si une erreur arrive -> afficher un message au lieu d'un 500 silencieux
            print("Erreur suppression :", e)
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"text/plain; charset=utf-8")]
            })
            await send({
                "type": "http.response.body",
                "body": f"Erreur lors de la suppression : {e}".encode()
            })
    
    async def updateProduit(scope, receive, send):
        
        categorie = Categories.getAll()
        options = ""

        for c in categorie:
            options += f'<option value="{c["id_categories"]}">{c["nom"]}</option>'
        context = {
            "options_categorie": options,
            }
        
        await __class__.__load(send, "views/produit/update.html", context)


    @staticmethod
    async def opUpdate(scope, receive, send):
        event = await receive()
        body = event.get("body", b'')
        dico = urllib.parse.parse_qs(body.decode())
        
        colonne = ["nomP", "prix", "categorie_id"]
        id        = int(dico.get("id", ["0"])[0])
        nom       = dico.get("nom", [""])[0]
        prix      = dico.get("prix", [""])[0]
        categorie = dico.get("categorie", [""])[0]

        values = (nom, prix, categorie)
        Produits.update(id, colonne , *values)

        await send({
            "type": "http.response.start",
            "status": 302,
            "headers": [(b"Location", b"/listProduit")]
        })
        await send({
            "type": "http.response.body",
            "body": b""
        })