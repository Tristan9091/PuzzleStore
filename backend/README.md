# PuzzleStore — E-commerce Fullstack

**Programación Web 1 · Prof. Kegovc**

Tienda en línea de cubos, rompecabezas y puzzles. El proyecto integra las cuatro
prácticas del curso en un solo sistema fullstack: un backend en FastAPI con
Arquitectura Hexagonal (P1), autenticación y autorización con JWT (P2), un chat
cliente–asistente en tiempo real con WebSockets (P3) y el frontend completo del
e-commerce con su panel administrativo (P4).

---

## Estructura del proyecto

```
project/
├── backend/                    # API en FastAPI (Arquitectura Hexagonal)
│   ├── app/
│   │   ├── domain/             # Entidades y puertos (contratos)
│   │   │   ├── entities/       # Producto, PerfilCompra, OrdenCompra, Usuario, MensajeChat, PreguntaFrecuente
│   │   │   └── ports/          # Interfaces de repositorios y del motor de respuestas
│   │   ├── application/        # Casos de uso (lógica de negocio)
│   │   ├── infrastructure/     # Implementaciones concretas
│   │   │   ├── database/       # Conexión y modelos SQLAlchemy
│   │   │   ├── repositories/   # Repositorios SQL (cumplen los puertos)
│   │   │   └── motores/        # Motor de FAQ (cumple el puerto del asistente)
│   │   ├── adapters/http/      # Routers (productos, auth, órdenes, perfiles, imágenes)
│   │   ├── realtime/           # WebSockets del chat y gestor de conexiones
│   │   ├── security/           # Generación y validación de JWT
│   │   └── main.py             # Punto de entrada (CORS, estáticos, routers)
│   └── uploads/                # Imágenes de productos (se llena al subir)
├── frontend/                   # Cliente en HTML + CSS + JS (Bootstrap por CDN)
│   ├── login.html              # Login / registro
│   ├── index.html              # Catálogo + carrito + chat
│   ├── checkout.html           # Resumen, compra, historial + chat
│   ├── admin.html              # Backoffice (productos, órdenes, chat del agente)
│   ├── css/styles.css
│   └── js/
│       ├── auth.js             # Sesión y token JWT
│       ├── api.js              # Llamadas al backend
│       ├── login.js            # Login / registro
│       ├── index.js            # Catálogo y carrito
│       ├── checkout.js         # Checkout e historial
│       ├── chat.js             # WebSocket del chat (compartido)
│       └── admin.js            # Backoffice
├── requirements.txt
└── README.md
```

---

## Requisitos y ejecución

**Requisitos:** Python 3.10+, MySQL en ejecución y conexión a internet (Bootstrap
se carga por CDN).

**1. Base de datos.** Crear la base en MySQL:

```sql
CREATE DATABASE puzzlestore;
```

La cadena de conexión está en `backend/app/infrastructure/database/base.py`. Ajustarla
si el usuario/contraseña de MySQL son distintos:

```
mysql+pymysql://root:root1234@127.0.0.1:3306/puzzlestore
```

**2. Backend.** Instalar dependencias y levantar el servidor desde la carpeta `backend/`:

```bash
pip install -r ../requirements.txt
cd backend
uvicorn app.main:app --reload
```

Queda en `http://127.0.0.1:8000`. Las tablas se crean solas al arrancar y se cargan
unas FAQs de ejemplo. La documentación interactiva está en `http://127.0.0.1:8000/docs`.

**3. Frontend.** Servirlo con un servidor estático desde la carpeta `frontend/`:

```bash
cd frontend
python -m http.server 5500
```

Abrir `http://127.0.0.1:5500/login.html`. Si `API_BASE` en `frontend/js/api.js` no
apunta a `http://127.0.0.1:8000`, ajustarlo.

**Roles disponibles:** al registrarse se puede elegir entre **cliente** (entra a la
tienda) y **administrador** (entra al backoffice). El sistema contempla además el rol
**operador** a nivel de backend.

---

## Práctica 1 — E-commerce Hexagonal

**Objetivo:** construir un backend de e-commerce desacoplado y organizado siguiendo
Arquitectura Hexagonal.

**Cómo se cumple.** El backend separa responsabilidades en cuatro capas:

- **Dominio** (`domain/`): las entidades del negocio (`Producto`, `PerfilCompra`,
  `OrdenCompra` con sus `OrdenItem`) como clases puras, sin dependencias de framework,
  y los **puertos** (`ports/`), que son las interfaces que el dominio espera que alguien
  implemente.
- **Aplicación** (`application/use_cases/`): la lógica de negocio en casos de uso
  (crear producto, crear orden, listar órdenes por perfil, cancelar orden, etc.). Cada
  caso de uso recibe un repositorio por inyección de dependencias, así que no sabe nada
  de SQL.
- **Infraestructura** (`infrastructure/`): las implementaciones concretas con
  SQLAlchemy/MySQL. Los repositorios SQL cumplen los puertos del dominio.
- **Adaptadores** (`adapters/http/`): los routers de FastAPI que exponen los endpoints
  y traducen las peticiones HTTP a llamadas a los casos de uso.

**Entidades y flujo.** Las tres entidades mínimas están presentes: productos, perfiles
de compra y órdenes de compra. El flujo de una orden es: existe un producto en el
catálogo → el cliente tiene un perfil de compra → se crea una orden que referencia ese
perfil, lista sus items (con precio y cantidad) y calcula el total → la orden tiene un
estado que evoluciona (`pendiente`, `pagada`, `enviada`, `entregada`, `cancelada`).

**Endpoints principales:** CRUD de productos (`/productos`), perfiles (`/perfiles`) y
órdenes (`/ordenes`, crear/consultar/listar por perfil/cancelar).

**Para la defensa:** el valor de esta arquitectura es que el dominio no depende de
nada externo. Se podría cambiar MySQL por otra base de datos reescribiendo solo los
repositorios, sin tocar los casos de uso ni las entidades, porque ambos se comunican a
través de los puertos.

---

## Práctica 2 — Autenticación y Autorización (JWT)

**Objetivo:** proteger el backend con login, validación de usuarios y control de
acceso por roles, integrándolo a la arquitectura existente. Se eligió la **Opción 2
(OAuth 2 / JWT, hasta 100%)**.

**Cómo se cumple.**

- **Registro** (`POST /auth/register`): crea un usuario con su rol (`cliente`,
  `admin` u `operador`). La contraseña se guarda cifrada con bcrypt (passlib).
- **Login** (`POST /auth/login`): usa el estándar `OAuth2PasswordRequestForm` de
  FastAPI. Si las credenciales son correctas, devuelve un **access token** y un
  **refresh token** (JWT firmados con python-jose). Dentro del token viajan el correo
  (`sub`) y el `rol`.
- **Refresh** (`POST /auth/refresh`): permite obtener un nuevo access token a partir
  del refresh token, sin volver a pedir credenciales.
- **Protección de rutas** (`adapters/http/dependencies.py`): se implementan
  dependencias reutilizables que FastAPI inyecta en los endpoints:
  - `get_current_user`: valida el token y devuelve el usuario; rechaza si es inválido o
    expiró.
  - `require_admin`: solo deja pasar al rol `admin` (crear/eliminar productos, etc.).
  - `require_operador_o_admin`: deja pasar a `admin` u `operador` (editar productos,
    gestionar órdenes).

**Control de acceso aplicado.** El catálogo es público (cualquiera puede listar
productos), pero crear, editar o eliminar productos, gestionar órdenes y subir imágenes
requieren los roles adecuados. El frontend complementa esto redirigiendo a cada usuario
según su rol y mandando el token en el header `Authorization: Bearer ...`.

---

## Práctica 3 — Chat Cliente-Asistente con WebSockets

**Objetivo:** comunicación en tiempo real con WebSockets y un sistema de respuestas
automáticas a preguntas frecuentes, diseñado para poder evolucionar a IA.

**Cómo se cumple.**

- **WebSockets** (`realtime/`): hay dos canales. `/ws/chat/{cliente_id}` para el
  cliente y `/ws/admin` para los agentes. Un `ConnectionManager` lleva el registro de
  las conexiones activas y permite enviar mensajes a un cliente específico o difundir a
  todos los administradores.
- **Respuestas automáticas (FAQ):** cuando llega un mensaje del cliente, el caso de uso
  `ProcesarMensajeCliente` consulta el **motor de respuestas**. El motor incluido
  (`MotorFaqSimple`) normaliza el texto (minúsculas y sin acentos) y puntúa cada FAQ
  según cuántas de sus palabras clave aparecen en el mensaje; devuelve la mejor
  coincidencia o `None`.
- **Escalamiento:** si el motor no encuentra respuesta (`None`), el mensaje se **escala**
  en vivo a todos los administradores conectados, y al cliente se le avisa que un agente
  lo atenderá. El agente responde desde el panel y el mensaje llega al cliente correcto.

**Diseño desacoplado y escalable.** La clave de esta práctica es el puerto
`MotorRespuestas` (`domain/ports/motor_respuestas.py`): es una interfaz que solo define
"recibe un texto, devuelve una respuesta o nada". El `MotorFaqSimple` es una
implementación, pero podría reemplazarse por un motor basado en **embeddings, RAG o un
LLM** sin tocar el WebSocket ni el caso de uso, porque todos dependen del puerto y no de
la implementación concreta.

---

## Práctica 4 — Frontend E-commerce y Backoffice Administrativo

**Objetivo:** desarrollar el frontend completo integrando las tres prácticas
anteriores, con operaciones reales de compra, administración y comunicación.

**Cómo se cumple.** El frontend está hecho en HTML, CSS y JavaScript con Bootstrap por
CDN, con la lógica separada por responsabilidades: `auth.js` (sesión/token), `api.js`
(consumo de la API), y un archivo por página. El estado del carrito se mantiene en
`localStorage` para sobrevivir el cambio entre el catálogo y el checkout.

- **Cliente:** catálogo con búsqueda, carrito, checkout con flujo completo de compra e
  historial de órdenes (con cancelación), todo integrado con la autenticación (login y
  token) y con la sección de chat en tiempo real.
- **Administrador (Backoffice):** CRUD de productos, gestión de órdenes con cambio de
  estado, y un panel de chat donde el agente responde en vivo las conversaciones
  escaladas.

**Manejo de imágenes (`multipart/form-data`).** Para cumplir este requisito se agregó
al backend el endpoint `POST /productos/upload-imagen`, que recibe el archivo como
`multipart/form-data`, lo valida (extensión, tipo MIME y tamaño máximo de 5 MB), lo
guarda físicamente en `backend/uploads/` con un nombre único y devuelve su URL. Esa URL
se persiste en el producto y se sirve como archivo estático en `/uploads`. En el
formulario del admin, la imagen se sube primero y luego se guarda el producto con la URL
resultante.

**Ajustes al backend para esta práctica:** se habilitó **CORS** (para que el navegador
pueda consumir la API), se montó la carpeta de imágenes estáticas, se agregó el endpoint
de subida de imágenes, y se añadieron dos endpoints para el backoffice: `GET /ordenes`
(listar todas las órdenes) y `PATCH /ordenes/{id}/estado` (cambiar el estado),
respetando la misma Arquitectura Hexagonal (puerto → repositorio → caso de uso → router).

---

## Notas finales

- El WebSocket del chat no va autenticado (así está diseñado el backend de la P3); es
  una mejora futura posible.
- Bootstrap se carga por CDN, por lo que se requiere internet al ejecutar el frontend.
- La relación entre el usuario autenticado y su perfil de compra se mantiene desde el
  frontend (se crea el perfil en la primera compra y se reutiliza su id), ya que el
  backend las maneja como entidades independientes.
