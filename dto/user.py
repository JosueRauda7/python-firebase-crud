from pydantic import BaseModel, EmailStr

class UsuarioDTO(BaseModel):
    nombre_completo: str
    correo: EmailStr
    telefono: str
    fotografia: str | None
