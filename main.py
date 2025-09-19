import os
from rooter import Router
from controllers.produit import ProduitController
from controllers.categorie import CategorieController
import uvicorn
# from test import Tour

routeur = Router()
routeur.add("/", ProduitController.index)
routeur.add("/insertCategorie", CategorieController.categorieInsert)
routeur.add("/insertProduit", ProduitController.produitInsert)
routeur.add("/opinsertProduit", ProduitController.opInsert)
routeur.add("/opupdateProduit", ProduitController.opUpdate)
routeur.add("/opdeleteProduit", ProduitController.deleteProduit)
routeur.add("/opinsertCategorie", CategorieController.opInsert)
routeur.add("/opupdateCategorie", CategorieController.opUpdateCategorie)
routeur.add("/opudeleteCategorie", CategorieController.deleteCategorie)
routeur.add("/listCategorie", CategorieController.listCategorie)
routeur.add("/listProduit", ProduitController.listProduit)
routeur.add("/updateCategorie", CategorieController.updateCategorie)
routeur.add("/updateProduit", ProduitController.updateProduit)


async def app(scope, receive, send):
    assert scope["type"] == 'http'
    path = scope["path"]

    BASE_DIR = os.path.dirname(__file__)
    STATIC_DIR = os.path.join(BASE_DIR, "views", "assets")

    if path.startswith("/assets/"):
        relative_path = path.replace("/assets/", "")
        file_path = os.path.join(STATIC_DIR, relative_path)
        print(file_path)
        if os.path.exists(file_path):
            if file_path.endswith(".css"):
                content_type = b'text/css'
            elif file_path.endswith(".js"):
                content_type = b'application/javascript'
            elif file_path.endswith(".png"):
                content_type = b'image/png'
            elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                content_type = b'image/jpeg'
            else:
                content_type = b'application/octet-stream'
            
            with open(file_path, "rb") as f:
                body = f.read()
            
            await send({
                'type' : 'http.response.start',
                'status' : 200,
                'headers' : [(b'content-type', content_type)]
            })

            await send({
                "type" : "http.response.body",
                "body" : body
            })
            return
        else:
            body = "404 NOT FOUND".encode("utf-8")
            await send({
                'type' : 'http.response.start',
                'status' : 404,
                'headers' : [(b'content-type', b'text/html; charset=utf-8')]
            })
            await send({
                "type" : "http.response.body",
                "body" : body
            })

    handler = routeur.resolve(path)

    if handler:
        await handler(scope, receive, send)
    else:
        # await TouristeController.error404()
        pass

if __name__ == '__main__':
    uvicorn.run("main:app", port= 8088, reload= True)


