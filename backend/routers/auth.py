from fastapi import APIRouter, HTTPException, status
from backend.core.db import get_db_connection, hash_password
from backend.schemas import UsuarioLogin, UsuarioCreate

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
async def login(usuario: UsuarioLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT ID_USUARIO, CORREO, CONTRASENA, ROL FROM USUARIO WHERE CORREO = ?",
            (usuario.correo,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
        stored_hash = row[2].strip() if row[2] else ""
        hashed_password = hash_password(usuario.contrasena)
        if stored_hash.lower() != hashed_password.lower():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
        return {"id_usuario": row[0], "correo": row[1], "rol": row[3], "message": "Login exitoso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/register")
async def register(usuario: UsuarioCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_USUARIO FROM USUARIO WHERE CORREO = ?", (usuario.correo,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        hashed_password = hash_password(usuario.contrasena)
        cursor.execute(
            "INSERT INTO USUARIO (CORREO, CONTRASENA, ROL) OUTPUT INSERTED.ID_USUARIO VALUES (?, ?, ?)",
            (usuario.correo, hashed_password, usuario.rol)
        )
        id_usuario = cursor.fetchone()[0]
        conn.commit()
        return {"id_usuario": id_usuario, "correo": usuario.correo, "rol": usuario.rol, "message": "Usuario registrado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

