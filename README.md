# Reservation System - La Mesa Dorada

REST API to manage the reservation system for "La Mesa Dorada" restaurant, built with FastAPI and SQLite.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Create a virtual environment:
python -m venv .venv

2. Activate the virtual environment:
Windows
.venv\Scripts\activate
Linux/Mac
source .venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Create the database with sample data:
python app/database.py

## Running the project
uvicorn app.main:app --reload

The API will be available at: http://127.0.0.1:8000

- Interactive docs (Swagger): http://127.0.0.1:8000/docs
- Alternative docs (ReDoc): http://127.0.0.1:8000/redoc

## Project Structure
app/

├── main.py                  # Application entry point

├── database.py               # SQLite database configuration

├── models/                   # Pydantic models (Create, Update, Response)

│   ├── cliente.py

│   ├── mesa.py

│   └── reserva.py

├── routers/                  # Endpoints organized by resource

│   ├── clientes.py

│   ├── mesas.py

│   ├── reservas.py

│   └── estadisticas.py

├── services/                 # Business logic with SQLite access

│   ├── cliente_service.py

│   ├── mesa_service.py

│   ├── reserva_service.py

│   └── estadisticas_service.py

└── exceptions/                # Custom exceptions

└── custom_exceptions.py

data/

└── restaurante.db            # SQLite database (created by database.py)

## Main Endpoints

### Customers (/clientes/)

| Method | Endpoint           | Description                            |
|--------|----------------------|-----------------------------------------|
| GET    | /clientes/           | List all customers                      |
| GET    | /clientes/{id}        | Get a customer by ID                    |
| POST   | /clientes/            | Create a new customer                   |
| PUT    | /clientes/{id}        | Update customer data                    |
| DELETE | /clientes/{id}        | Delete a customer                       |
| GET    | /clientes/buscar/     | Search customers by name, email or phone |

### Tables (/mesas/)

| Method | Endpoint              | Description                                  |
|--------|--------------------------|------------------------------------------------|
| GET    | /mesas/                  | List all tables                                |
| GET    | /mesas/{id}               | Get a table by ID                              |
| POST   | /mesas/                  | Create a new table                             |
| PUT    | /mesas/{id}               | Update table data                              |
| DELETE | /mesas/{id}               | Delete a table                                 |
| GET    | /mesas/disponibles/       | Available tables for date/time and party size  |

### Reservations (/reservas/)

| Method | Endpoint                  | Description                       |
|--------|------------------------------|--------------------------------------|
| GET    | /reservas/                   | List reservations with filters       |
| GET    | /reservas/{id}                | Get a reservation by ID              |
| POST   | /reservas/                   | Create a new reservation             |
| PUT    | /reservas/{id}                | Update a reservation                 |
| DELETE | /reservas/{id}                | Cancel a reservation                 |
| PATCH  | /reservas/{id}/confirmar      | Confirm customer arrival             |
| PATCH  | /reservas/{id}/completar      | Mark reservation as completed        |

### Statistics (/estadisticas/)

| Method | Endpoint                          | Description                  |
|--------|---------------------------------------|----------------------------------|
| GET    | /estadisticas/ocupacion/diaria        | Daily occupancy                  |
| GET    | /estadisticas/ocupacion/semanal       | Weekly occupancy                 |
| GET    | /estadisticas/clientes-frecuentes     | Top 10 frequent customers        |
| GET    | /estadisticas/mesas-populares         | Most booked tables               |
| GET    | /estadisticas/resumen                 | General summary                  |

## Usage Examples

### Create a customer
POST /clientes/
{

"nombre": "Juan Perez",

"email": "juan@email.com",

"telefono": "612345678"

}

### Create a reservation
POST /reservas/
{

"cliente_id": 1,

"mesa_id": 5,

"fecha_hora_inicio": "2026-12-20T20:00:00",

"num_comensales": 2

}

## Sample Data

The database is created by running `python app/database.py` and includes:

- 10 sample customers
- 15 tables (5 for 2 people, 5 for 4 people, 3 for 6 people, 2 for 8 people)
- 20 reservations in different states and dates

## Author

Javier Montilla Arias - 2026

## Tech Stack

- FastAPI - Web framework
- Pydantic - Data validation
- SQLite - Database
- Uvicorn - ASGI server