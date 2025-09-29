from fastapi import FastAPI, UploadFile, File, status
from firebase_admin import credentials, initialize_app, firestore, storage
from dto.user import UsuarioDTO

app = FastAPI()

# CONFIGURACIÓN FIREBASE
cred = credentials.Certificate("config/parcial2-ufg-firebase-adminsdk-fbsvc-a90c7842a9.json")
firebase_app = initialize_app(cred, {
    'storageBucket': 'parcial2-ufg.firebasestorage.app'
})

db = firestore.client()
bucket = storage.bucket()

# RUTAS
@app.get("/usuarios")
def get_users():
    coleccion = db.collection("usuarios")
    registros = coleccion.stream()
    usuarios = []
    for registro in registros:
        usuario = registro.to_dict()
        usuario["id"] = registro.id
        usuarios.append(usuario)
    return {"usuarios": usuarios}

@app.get("/usuarios/{user_id}")
def get_user(user_id: str):
    usuario_ref = db.collection("usuarios").document(user_id)
    usuario = usuario_ref.get()
    if usuario.exists:
        usuario_encontrado = usuario.to_dict()
        usuario_encontrado["id"] = usuario.id
        return {"usuario": usuario_encontrado}
    return {"error": "Usuario no encontrado"}, 404

@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
def create_user(usuario: UsuarioDTO):
    nuevo_usuario = {
        "nombre_completo": usuario.nombre,
        "correo": usuario.correo,
        "telefono": usuario.telefono,
        "fotografia": usuario.fotografia
    }
    coleccion = db.collection("usuarios")
    coleccion.add(nuevo_usuario)
    nuevo_usuario["id"] = coleccion.document().id
    return {"usuario": nuevo_usuario}

@app.put("/usuarios/{user_id}")
def update_user(user_id: str, usuario: UsuarioDTO):
    usuario_encontrado = db.collection("usuarios").document(user_id)
    if usuario_encontrado.get().exists:
        usuario_encontrado.update({
            "nombre_completo": usuario.nombre,
            "correo": usuario.correo,
            "telefono": usuario.telefono,
            "fotografia": usuario.fotografia
        })
        return {"usuario": usuario}
    return {"error": "Usuario no encontrado"}, 404

@app.delete("/usuarios/{user_id}")
def delete_user(user_id: str):
    usuario_encontrado = db.collection("usuarios").document(user_id)
    if usuario_encontrado.get().exists:
        usuario_encontrado.delete()
        return {"message": "Usuario eliminado"}
    return {"error": "Usuario no encontrado"}, 404

@app.post("/usuarios/{user_id}/upload", status_code=status.HTTP_201_CREATED)
def upload_file(user_id: str, archivo: UploadFile = File(...)):
    usuario = db.collection("usuarios").document(user_id)
    if not usuario.get().exists:
        return {"error": "Usuario no encontrado"}, 404

    if archivo.content_type not in ["image/jpg", "image/jpeg", "image/png"]:
        return {"error": "Tipo de archivo no permitido. Solo se permite imagen JPG, JPEG o PNG"}, 400

    blob = bucket.blob(f"usuarios/{user_id}/{archivo.filename}")
    blob.upload_from_file(archivo.file, content_type=archivo.content_type)
    blob.make_public()

    url_fotografia = blob.public_url
    usuario.update({"fotografia": url_fotografia})

    return {"url_fotografia": url_fotografia}