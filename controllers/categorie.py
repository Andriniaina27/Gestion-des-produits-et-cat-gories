from models.produit import Produits
from models.categorie import Categories
import urllib.parse

class CategorieController(object):
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

        nom    = dico.get("nom", b"")
        Categories.insert(nom)

        await send({
            "type": "http.response.start",
            "status": 302,
            "headers": [(b"Location", b"/listCategorie")]
        })
        await send({
            "type": "http.response.body",
            "body": b""
        })
        
    
    @staticmethod
    async def categorieInsert(scope, receive, send):
        last_id = Categories.lastId() + 1
        context = {"last_id": last_id}
        await __class__.__load(send, "views/categorie/insert.html", context)
    
    @staticmethod
    async def listCategorie(scope, receive, send):
        categorie = Categories.getAll()

        list_categorie = ""
        for c in categorie:
            list_categorie += f"""
                <tr>
                    <td>{c['id_categories']}</td>
                    <td>{c['nom']}</td>
                    <td width = 200 class="action">
                        <form action="/opudeleteCategorie" method="post">
                            <input type="hidden" name="id" id="" value="{c['id_categories']}">
                            <button type="submit">Supprimer</button>
                        </form>
                        <button class="editBtn"
                                data-id="{c['id_categories']}"
                                data-nom="{c['nom']}">
                            Modifier
                        </button>
                    </td>
                </tr>
            """
        context = {"list_categorie" : list_categorie}
        await __class__.__load(send, "views/categorie/read.html", context)
    
    @staticmethod
    async def deleteCategorie(scope, receive, send):
        try:
            event = await receive()
            body = event.get("body", b'')
            dico = urllib.parse.parse_qs(body.decode())

            id    = dico.get("id", b"")
            Categories.delete(id)

            await send({
                "type": "http.response.start",
                "status": 302,
                "headers": [(b"Location", b"/listCategorie")]
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
    
    async def updateCategorie(scope, receive, send):
        
        await __class__.__load(send, "views/categorie/update.html")


    @staticmethod
    async def opUpdateCategorie(scope, receive, send):
        event = await receive()
        body = event.get("body", b'')
        dico = urllib.parse.parse_qs(body.decode())
        
        colonne = ["nom"]
        id    = int(dico.get("id", ["0"])[0])
        nom    = dico.get("nom", [""])[0]

        values = (nom)
        # print(id, colonne,nom)
        Categories.update(id, colonne , values)

        await send({
            "type": "http.response.start",
            "status": 302,
            "headers": [(b"Location", b"/listCategorie")]
        })
        await send({
            "type": "http.response.body",
            "body": b""
        })