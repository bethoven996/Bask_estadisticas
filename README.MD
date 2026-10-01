# Basquet Stats — API

Backend de una plataforma de gestión y análisis de estadísticas de básquet. Permite cargar equipos, jugadores y partidos, calcular estadísticas de rendimiento, comparar jugadores/equipos y exportar reportes.

🔗 **Demo en vivo:** https://basquet-stats-frontend.vercel.app/
🔗 **API:** https://bask-estadisticas.onrender.com

## Stack

- **FastAPI** — framework del API
- **SQLAlchemy** — ORM
- **PostgreSQL** (producción, alojado en [Neon](https://neon.tech)) / **SQLite** (desarrollo local)
- **JWT + bcrypt** — autenticación
- **Pandas** — procesamiento del dataset de estadísticas reales de la NBA

## Funcionalidades

- CRUD de equipos, jugadores, partidos y estadísticas
- Autenticación con JWT: lectura pública, escritura protegida
- Subida de fotos de perfil de jugadores
- Carga masiva de datos reales de la NBA (30 equipos, ~1000 jugadores, promedios de carrera) desde un dataset público

## Correr en local

```bash
git clone https://github.com/bethoven996/Bask_estadisticas.git
cd Bask_estadisticas
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Creá un archivo `.env` en la raíz con:
SECRET_KEY=una-clave-larga-y-random
DATABASE_URL=sqlite:///./basquet.db
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

Levantá el servidor:

```bash
uvicorn app.main:app --reload
```

La documentación interactiva de la API queda disponible en `http://localhost:8000/docs`.

### Crear un usuario admin

```bash
python crear_admin.py
```

### Cargar datos de ejemplo (estadísticas reales de la NBA)

Requiere el dataset `all_seasons.csv` de [NBA Players (Kaggle)](https://www.kaggle.com/datasets/justinas/nba-players-data) en la raíz del proyecto.

```bash
python seed.py
```

## Endpoints principales

| Método | Ruta                   | Descripción          | Requiere login |
| ------ | ---------------------- | -------------------- | -------------- |
| GET    | `/equipos`             | Listar equipos       | No             |
| GET    | `/jugadores`           | Listar jugadores     | No             |
| GET    | `/partidos`            | Listar partidos      | No             |
| GET    | `/estadisticas`        | Listar estadísticas  | No             |
| POST   | `/login`               | Iniciar sesión       | No             |
| POST   | `/jugadores`           | Crear jugador        | Sí             |
| POST   | `/partidos`            | Crear partido        | Sí             |
| DELETE | `/jugadores/{id}`      | Eliminar jugador     | Sí             |
| POST   | `/jugadores/{id}/foto` | Subir foto de perfil | Sí             |

## Autor

Norberto Narváez — [LinkedIn](https://www.linkedin.com/in/betonarvaez)
