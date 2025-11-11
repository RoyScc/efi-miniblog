# API REST: (EFI PP1 - Python)

# INTEGRANTES:
- Villaverde Anabella
- Roy Scheurer
- Alaniz Valentina

Este proyecto implementa una API REST segura para un miniblog, utilizando **Flask**, **Autenticación JWT**

---

## Requisitos e Instalación

### Requisitos Previos
* **Python 3.10** o superior.
* **Pip** (Administrador de paquetes de Python).
* Un servidor de base de datos **MySQL**.

### Pasos para Clonar y Correr el Proyecto

1.  **Clonar el repositorio:**
2.  **Crear y Activar el Entorno Virtual:**
3.  **Instalar Dependencias:**
    Todas las librerías necesarias están listadas en el archivo `requirements.txt`.
4.  **Configuración de la Base de Datos y Migraciones:**
5.  **Ejecutar el Servidor:**
    La API estará disponible en `http://127.0.0.1:5000/`.

---

## 📄 Documentación de Endpoints

### 1. Autenticación (Público)

| Método | Ruta | Roles Permitidos | Cuerpo (JSON) | Respuesta (Éxito 201/200) |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/register` | Público | `{"nombre": "...", "correo": "...", "password": "..."}` | `{"message": "Usuario creado", "user_id": 4}` |
| **POST** | `/api/login` | Público | `{"correo": "...", "password": "..."}` | `{"access_token": "eyJ0eXAiO..."}` |

### 2. Posts

| Método | Ruta | Roles Permitidos | Descripción / Requisitos |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/posts` | Público | Listar todos los posts publicados. |
| **GET** | `/api/posts/<id>` | Público | Ver un post específico. |
| **POST** | `/api/posts` | User+ | Crear un nuevo post. **Requiere:** `titulo`, `contenido`, `categoria_id`. |
| **PUT** | `/api/posts/<id>` | Autor / Admin | Editar solo el post propio. |
| **DELETE** | `/api/posts/<id>` | Autor / Admin | Eliminar el post (propio o cualquier post, si es Admin). |

#### **Ejemplo: POST /api/posts (Crear Post)**
| Tipo | Ejemplo JSON |
| :--- | :--- |
| **Request Body** | ```json\n{\n  "titulo": "Post de prueba",\n  "contenido": "Contenido del post nuevo.",\n  "categoria_id": 1\n}``` |

### 3. Comentarios

| Método | Ruta | Roles Permitidos | Descripción / Requisitos |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/posts/<id>/comments` | Público | Listar comentarios de un post. |
| **POST** | `/api/posts/<id>/comments` | User+ | Comentar en un post. **Requiere:** `texto`. |
| **DELETE** | `/api/comments/<id>` | Autor / Moderator / Admin | Eliminar cualquier comentario. (Prueba de Moderación) |

#### **Ejemplo: DELETE /api/comments/15 (Prueba de Moderación)**
* **Prueba de Rol:** Usar el token de un **`moderator`** para eliminar un comentario que **no le pertenece**.
* **Response (Éxito):** Estatus HTTP **204 No Content**.

### 4. Categorías

| Método | Ruta | Roles Permitidos | Requerimientos |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/categories` | Público | Listar todas las categorías. |
| **POST** | `/api/categories` | Moderator / Admin | Crear una nueva categoría. **Requiere:** `nombre`. |
| **PUT** | `/api/categories/<id>` | Moderator / Admin | Editar categoría. |
| **DELETE** | `/api/categories/<id>` | Solo Admin | Eliminar categoría. |

#### **Ejemplo: DELETE /api/categories/5 (Prueba de Rol Admin)**
* **Prueba de Rol:** Se requiere el token de **Admin**. Fallará si se usa un token de `Moderator` o `User` (error 403 Forbidden).
* **Response (Éxito):** Estatus HTTP **204 No Content**.

### 5. Usuarios y Administración

| Método | Ruta | Roles Permitidos | Requerimientos |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/users` | Solo Admin | Listar todos los usuarios. |
| **PATCH** | `/api/users/<id>/role` | Solo Admin | **Cambiar el rol** de un usuario. |
| **DELETE** | `/api/users/<id>` | Solo Admin | Desactivar (`is_active = False`) un usuario. |

#### **Ejemplo: PATCH /api/users/2/role (Cambiar Rol)**
* **Prueba de Rol:** Se requiere el token de **Admin**.
| Tipo | Ejemplo JSON |
| :--- | :--- |
| **Request Body** | ```json\n{\n  "role": "moderator"\n}``` |
| **Response (Éxito 200)** | ```json\n{\n  "message": "Rol de usuario ID 2 actualizado",\n  "new_role": "moderator"\n}``` |

### 6. Estadísticas

| Método | Ruta | Roles Permitidos | Descripción / Diferenciación |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/stats` | Moderator / Admin | El **Admin** debe ver métricas completas (incluyendo `posts_last_week`). |

---

##  Arquitectura del Proyecto

* **`src/models`**: Clases de SQLAlchemy.
* **`src/schemas`**: Schemas de Marshmallow para validación.
* **`src/repositories`**: Lógica de acceso a datos.
* **`src/services`**: Lógica de negocio principal.
* **`src/views`**: Controladores (MethodView).
* **`src/decorators`**: Decoradores personalizados para la verificación de roles