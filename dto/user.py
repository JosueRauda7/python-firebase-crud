from pydantic import BaseModel, EmailStr, Field

class UsuarioDTO(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: str
    fotografia: str | None
