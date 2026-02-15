from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routers import clientes, mesas, reservas, estadisticas
from app.database import crear_base_datos, inicializar_datos_prueba, obtener_conexion
import os
from pathlib import Path

app = FastAPI(
    title="Sistema de Reservas - La Mesa Dorada",
    description="API REST para gestionar reservas de restaurante con SQLite",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(clientes.router)
app.include_router(mesas.router)
app.include_router(reservas.router)
app.include_router(estadisticas.router)


@app.on_event("startup")
async def startup_event():
    """Crear la base de datos y cargar datos de prueba si es necesario"""
    db_path = Path(__file__).parent.parent / "data" / "restaurante.db"
    
    # Siempre crear las tablas (IF NOT EXISTS evita errores)
    crear_base_datos()
    
    # Comprobar si ya hay datos
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM clientes")
    count = cursor.fetchone()["count"]
    conn.close()
    
    if count == 0:
        print("Base de datos vacía. Insertando datos de prueba...")
        inicializar_datos_prueba()
        print("Datos de prueba insertados correctamente")
    else:
        print(f"Base de datos encontrada con {count} clientes")


@app.get("/", include_in_schema=False)
async def root():
    """Redirigir a la documentación"""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    return {
        "status": "ok",
        "service": "Sistema de Reservas - La Mesa Dorada",
        "version": "1.0.0",
        "database": "SQLite"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)