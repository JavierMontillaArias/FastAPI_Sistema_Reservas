import sqlite3
from pathlib import Path

# Ruta a la base de datos
DATABASE_PATH = Path(__file__).parent.parent / "data" / "restaurante.db"


def crear_base_datos():
    # Asegurar que existe el directorio data
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Tabla de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefono TEXT NOT NULL,
            notas TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de mesas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER UNIQUE NOT NULL,
            capacidad INTEGER NOT NULL CHECK(capacidad IN (2, 4, 6, 8)),
            ubicacion TEXT NOT NULL CHECK(ubicacion IN ('interior', 'terraza', 'privado')),
            activa BOOLEAN DEFAULT 1
        )
    """)
    
    # Tabla de reservas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            mesa_id INTEGER NOT NULL,
            fecha_hora_inicio TIMESTAMP NOT NULL,
            fecha_hora_fin TIMESTAMP NOT NULL,
            num_comensales INTEGER NOT NULL,
            estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'confirmada', 'completada', 'cancelada')),
            notas TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (mesa_id) REFERENCES mesas(id)
        )
    """)
    
    # Índices para mejorar rendimiento
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reservas_fecha 
        ON reservas(fecha_hora_inicio)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reservas_mesa 
        ON reservas(mesa_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reservas_cliente 
        ON reservas(cliente_id)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Base de datos creada en: {DATABASE_PATH}")


def obtener_conexion():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_datos_prueba():
    from datetime import datetime, timedelta
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # cursor.execute("SELECT COUNT(*) as count FROM clientes")
    # if cursor.fetchone()["count"] > 0:
    #     print("La base de datos ya contiene datos")
    #     conn.close()
    #     return
    
    print("Insertando datos de prueba...")
    
    clientes = [
        ("María García López", "maria.garcia@email.com", "612345678", "Alérgica al marisco"),
        ("Juan Martínez Ruiz", "juan.martinez@email.com", "623456789", "Prefiere mesa cerca de la ventana"),
        ("Ana Fernández Soto", "ana.fernandez@email.com", "634567890", None),
        ("Carlos López Díaz", "carlos.lopez@email.com", "645678901", "Vegetariano"),
        ("Laura Sánchez Gil", "laura.sanchez@email.com", "656789012", None),
        ("Pedro Rodríguez Vega", "pedro.rodriguez@email.com", "667890123", "Cliente VIP"),
        ("Isabel Moreno Ramos", "isabel.moreno@email.com", "678901234", None),
        ("Miguel Álvarez Torres", "miguel.alvarez@email.com", "689012345", "Prefiere terraza"),
        ("Carmen Jiménez Ortiz", "carmen.jimenez@email.com", "690123456", "Intolerancia al gluten"),
        ("Francisco Romero Castro", "francisco.romero@email.com", "601234567", None)
    ]
    
    cursor.executemany(
        "INSERT INTO clientes (nombre, email, telefono, notas) VALUES (?, ?, ?, ?)",
        clientes
    )
    
    mesas = [
        (1, 2, "interior", 1),
        (2, 2, "interior", 1),
        (3, 2, "terraza", 1),
        (4, 2, "terraza", 1),
        (5, 2, "privado", 1),

        (6, 4, "interior", 1),
        (7, 4, "interior", 1),
        (8, 4, "terraza", 1),
        (9, 4, "terraza", 1),
        (10, 4, "privado", 1),

        (11, 6, "interior", 1),
        (12, 6, "terraza", 1),
        (13, 6, "privado", 1),

        (14, 8, "interior", 1),
        (15, 8, "terraza", 1),
    ]
    
    cursor.executemany(
        "INSERT INTO mesas (numero, capacidad, ubicacion, activa) VALUES (?, ?, ?, ?)",
        mesas
    )
    
    fecha_base = datetime.now()
    reservas = [
        (1, 1, fecha_base.replace(hour=20, minute=0), fecha_base.replace(hour=22, minute=0), 2, "pendiente", "Aniversario"),
        (2, 3, fecha_base.replace(hour=21, minute=0), fecha_base.replace(hour=23, minute=0), 2, "pendiente", None),
        (3, 6, fecha_base.replace(hour=20, minute=30), fecha_base.replace(hour=22, minute=30), 4, "confirmada", "Cumpleaños"),
        (4, 8, (fecha_base + timedelta(days=1)).replace(hour=20, minute=0), (fecha_base + timedelta(days=1)).replace(hour=22, minute=0), 3, "pendiente", "Vegetarianos"),
        (5, 11, (fecha_base + timedelta(days=1)).replace(hour=21, minute=0), (fecha_base + timedelta(days=1)).replace(hour=23, minute=0), 6, "confirmada", None),
        (6, 14, (fecha_base + timedelta(days=1)).replace(hour=20, minute=0), (fecha_base + timedelta(days=1)).replace(hour=22, minute=0), 8, "pendiente", "Cliente VIP"),
        (7, 2, (fecha_base + timedelta(days=2)).replace(hour=13, minute=0), (fecha_base + timedelta(days=2)).replace(hour=15, minute=0), 2, "pendiente", None),
        (8, 12, (fecha_base + timedelta(days=2)).replace(hour=13, minute=30), (fecha_base + timedelta(days=2)).replace(hour=15, minute=30), 6, "confirmada", "Reunión de trabajo"),
        (9, 9, (fecha_base + timedelta(days=2)).replace(hour=20, minute=0), (fecha_base + timedelta(days=2)).replace(hour=22, minute=0), 4, "pendiente", "Sin gluten"),
        (10, 15, (fecha_base + timedelta(days=2)).replace(hour=21, minute=0), (fecha_base + timedelta(days=2)).replace(hour=23, minute=0), 7, "confirmada", None),
        (1, 4, (fecha_base + timedelta(days=3)).replace(hour=20, minute=0), (fecha_base + timedelta(days=3)).replace(hour=22, minute=0), 2, "pendiente", None),
        (2, 7, (fecha_base + timedelta(days=3)).replace(hour=20, minute=30), (fecha_base + timedelta(days=3)).replace(hour=22, minute=30), 4, "confirmada", None),
        (3, 10, (fecha_base + timedelta(days=4)).replace(hour=13, minute=0), (fecha_base + timedelta(days=4)).replace(hour=15, minute=0), 4, "pendiente", None),
        (4, 13, (fecha_base + timedelta(days=4)).replace(hour=14, minute=0), (fecha_base + timedelta(days=4)).replace(hour=16, minute=0), 6, "confirmada", None),
        (5, 1, (fecha_base + timedelta(days=5)).replace(hour=20, minute=0), (fecha_base + timedelta(days=5)).replace(hour=22, minute=0), 2, "pendiente", None),
        (6, 6, (fecha_base + timedelta(days=5)).replace(hour=21, minute=0), (fecha_base + timedelta(days=5)).replace(hour=23, minute=0), 4, "completada", None),
        (7, 11, (fecha_base + timedelta(days=6)).replace(hour=20, minute=0), (fecha_base + timedelta(days=6)).replace(hour=22, minute=0), 5, "confirmada", None),
        (8, 14, (fecha_base + timedelta(days=6)).replace(hour=20, minute=30), (fecha_base + timedelta(days=6)).replace(hour=22, minute=30), 8, "pendiente", None),
        (9, 3, (fecha_base + timedelta(days=7)).replace(hour=13, minute=0), (fecha_base + timedelta(days=7)).replace(hour=15, minute=0), 2, "cancelada", None),
        (10, 8, (fecha_base + timedelta(days=7)).replace(hour=14, minute=0), (fecha_base + timedelta(days=7)).replace(hour=16, minute=0), 3, "confirmada", None),
    ]
    
    for reserva in reservas:
        cursor.execute(
            """INSERT INTO reservas 
            (cliente_id, mesa_id, fecha_hora_inicio, fecha_hora_fin, num_comensales, estado, notas) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            reserva
        )
    
    conn.commit()
    conn.close()
    
    print("Datos de prueba insertados correctamente")
    print(f"   - {len(clientes)} clientes")
    print(f"   - {len(mesas)} mesas")
    print(f"   - {len(reservas)} reservas")


if __name__ == "__main__":
    print("Inicializando base de datos...")
    crear_base_datos()
    inicializar_datos_prueba()
    print("Base de datos lista para usar")