from pydantic import BaseModel, EmailStr
from datetime import date

class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str

class UsuarioCreate(BaseModel):
    correo: EmailStr
    contrasena: str
    rol: str = "usuario"

class VotanteCreate(BaseModel):
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    region: str
    distrito: str

class CandidatoPresidencialCreate(BaseModel):
    nombres: str
    apellidos: str

class CandidatoRegionalCreate(BaseModel):
    nombres: str
    apellidos: str

class CandidatoDistritalCreate(BaseModel):
    nombres: str
    apellidos: str

class VotoPresidencialCreate(BaseModel):
    id_votantes: int
    id_candidato: int

class VotoRegionalCreate(BaseModel):
    id_votantes: int
    id_candidato_regional: int
    region: str

class VotoDistritalCreate(BaseModel):
    id_votantes: int
    id_candidato_distrital: int
    distrito: str

class VotanteStatus(BaseModel):
    can_vote_presidencial: bool
    can_vote_regional: bool
    can_vote_distrital: bool
    has_all_votes: bool

class VotoNuloCreate(BaseModel):
    id_votantes: int
    dni: str

