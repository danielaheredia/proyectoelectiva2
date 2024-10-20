from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from core.conexion import conexion
from models.user import User 

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:5500",    
]

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta para login
@app.post("/login")
async def login(user: User):
    cursor = conexion.cursor()
    query = "SELECT * FROM usuarios WHERE Username = %s AND Password = %s"
    values = (user.Username, user.Password)

    cursor.execute(query, values)
    resultado = cursor.fetchone()

    if resultado:   
        return {"success": True}
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

#Ruta Obtener Usuarios
@app.get('/users')
async def get_users():
    cursor = conexion.cursor(dictionary=True)
    query = "SELECT * FROM Usuarios"

    try:
        cursor.execute(query)
        Usuarios = cursor.fetchall()
        return Usuarios
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al conectar con MySQL: {err}")
    finally:
        cursor.close()
        

#Ruta Crear Usuarios
@app.post('/user')
async def create_user(user: User):
    cursor = conexion.cursor()
    query = "INSERT INTO usuarios(Username, Password) VALUES(%s,%s)"    
    values = (user.Username, user.Password)

    try:
        cursor.execute(query, values)
        conexion.commit()
        return {"message": "Usuario creado correctamente"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al guardar usuario: {err}")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=f"Error al guardar el usuario: {e}")
    finally:
        cursor.close()

# Ruta Eliminar Usuario
@app.delete("/user/{user_id}")
async def delete_user(user_id: int):    
    cursor = conexion.cursor()
    query = "DELETE FROM usuarios WHERE id = %s"  # Asegúrate de que 'id' sea el nombre correcto
    values = (user_id,)

    try:
        cursor.execute(query, values)
        conexion.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"message": "Usuario eliminado correctamente"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {err}")
    finally:
        cursor.close()

# Ruta Actualizar Usuario
@app.put("/user/{username}")
async def update_user(username: str, user: User):
    print(f"Actualizando usuario: {username} con nuevo Username: {user.Username} y Password: {user.Password}")
    cursor = conexion.cursor()

     #Verificar si el usuario existe
    check_query = "SELECT * FROM usuarios WHERE Username = %s"
    cursor.execute(check_query, (username,)) 
    existing_user = cursor.fetchone()
    
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    new_username = user.Username

    if new_username != username:
      check_new_query = "SELECT * FROM usuarios WHERE Username = %s"
      cursor.execute(check_new_query, (new_username, username))
      if cursor.fetchone():
        raise HTTPException(status_code=400, detail="El nuevo nombre de usuario ya está en uso")
      
     # Actualizar el usuario
    query = "UPDATE usuarios SET Username = %s, Password = %s WHERE Username = %s"
    values = (user.Username, user.Password, username)

    try:
        cursor.execute(query, values)
        conexion.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"message": "Usuario actualizado correctamente"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {err}")
    finally:
        cursor.close()

        #python -m uvicorn main:app --reload  