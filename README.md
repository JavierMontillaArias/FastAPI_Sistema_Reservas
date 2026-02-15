# Sistema de Reservas - La Mesa Dorada

API REST para gestionar el sistema de reservas del restaurante "La Mesa Dorada", desarrollada con FastAPI y SQLite.

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalacion

1. Crear un entorno virtual:
```bash
python -m venv .venv
```

2. Activar el entorno virtual:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Crear la base de datos con datos de prueba:
```bash
python app/database.py
```

## Ejecucion

```bash
uvicorn app.main:app --reload
```

La API estara disponible en: http://127.0.0.1:8000

- Documentacion interactiva (Swagger): http://127.0.0.1:8000/docs
- Documentacion alternativa (ReDoc): http://127.0.0.1:8000/redoc

## Estructura del Proyecto

```
app/
├── main.py                  # Punto de entrada de la aplicacion
├── database.py              # Configuracion de la base de datos SQLite
├── models/                  # Modelos Pydantic (Create, Update, Response)
│   ├── cliente.py
│   ├── mesa.py
│   └── reserva.py
├── routers/                 # Endpoints organizados por recurso
│   ├── clientes.py
│   ├── mesas.py
│   ├── reservas.py
│   └── estadisticas.py
├── services/                # Logica de negocio con acceso a SQLite
│   ├── cliente_service.py
│   ├── mesa_service.py
│   ├── reserva_service.py
│   └── estadisticas_service.py
└── exceptions/              # Excepciones personalizadas
    └── custom_exceptions.py
data/
└── restaurante.db           # Base de datos SQLite (se crea con database.py)
```

## Endpoints Principales

### Clientes (/clientes/)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | /clientes/ | Listar todos los clientes |
| GET | /clientes/{id} | Obtener un cliente por ID |
| POST | /clientes/ | Crear un nuevo cliente |
| PUT | /clientes/{id} | Actualizar datos de un cliente |
| DELETE | /clientes/{id} | Eliminar un cliente |
| GET | /clientes/buscar/ | Buscar clientes por nombre, email o telefono |

### Mesas (/mesas/)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | /mesas/ | Listar todas las mesas |
| GET | /mesas/{id} | Obtener una mesa por ID |
| POST | /mesas/ | Crear una nueva mesa |
| PUT | /mesas/{id} | Actualizar datos de una mesa |
| DELETE | /mesas/{id} | Eliminar una mesa |
| GET | /mesas/disponibles/ | Mesas disponibles para fecha/hora y comensales |

### Reservas (/reservas/)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | /reservas/ | Listar reservas con filtros |
| GET | /reservas/{id} | Obtener una reserva por ID |
| POST | /reservas/ | Crear una nueva reserva |
| PUT | /reservas/{id} | Modificar una reserva |
| DELETE | /reservas/{id} | Cancelar una reserva |
| PATCH | /reservas/{id}/confirmar | Confirmar llegada del cliente |
| PATCH | /reservas/{id}/completar | Marcar reserva como completada |

### Estadisticas (/estadisticas/)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | /estadisticas/ocupacion/diaria | Ocupacion por dia |
| GET | /estadisticas/ocupacion/semanal | Ocupacion semanal |
| GET | /estadisticas/clientes-frecuentes | Top 10 clientes frecuentes |
| GET | /estadisticas/mesas-populares | Mesas mas reservadas |
| GET | /estadisticas/resumen | Resumen general |

## Ejemplos de Uso

### Crear un cliente
```json
POST /clientes/

{
    "nombre": "Juan Perez",
    "email": "juan@email.com",
    "telefono": "612345678"
}
```

### Crear una reserva
```json
POST /reservas/

{
    "cliente_id": 1,
    "mesa_id": 5,
    "fecha_hora_inicio": "2026-12-20T20:00:00",
    "num_comensales": 2
}
```

## Datos de Prueba

La base de datos se crea ejecutando `python app/database.py` e incluye:
- 10 clientes de ejemplo
- 15 mesas (5 de 2 personas, 5 de 4 personas, 3 de 6 personas, 2 de 8 personas)
- 20 reservas en diferentes estados y fechas

## Autor

Javier Montilla Arias - 2026

## Tecnologias

- FastAPI - Framework web
- Pydantic - Validacion de datos
- SQLite - Base de datos
- Uvicorn - Servidor ASGI
