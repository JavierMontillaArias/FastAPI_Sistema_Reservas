from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict


def obtener_ocupacion_diaria(reservas: list, mesas: list, fecha: str) -> Dict:
    reservas_dia = [
        r for r in reservas 
        if r["fecha_hora_inicio"].date().isoformat() == fecha
    ]
    
    total_reservas = len(reservas_dia)
    pendientes = len([r for r in reservas_dia if r["estado"] == "pendiente"])
    confirmadas = len([r for r in reservas_dia if r["estado"] == "confirmada"])
    completadas = len([r for r in reservas_dia if r["estado"] == "completada"])
    canceladas = len([r for r in reservas_dia if r["estado"] == "cancelada"])
    
    if reservas_dia:
        total_comensales = sum(r["num_comensales"] for r in reservas_dia)
        promedio_comensales = total_comensales / len(reservas_dia)
    else:
        promedio_comensales = 0.0
    
    mesas_activas = [m for m in mesas if m.get("activa", True)]
    total_mesas_activas = len(mesas_activas)
    
    if total_mesas_activas > 0:
        reservas_efectivas = total_reservas - canceladas
        tasa_ocupacion = (reservas_efectivas / total_mesas_activas) * 100
    else:
        tasa_ocupacion = 0.0
    
    return {
        "fecha": fecha,
        "total_reservas": total_reservas,
        "confirmadas": confirmadas,
        "canceladas": canceladas,
        "promedio_comensales": round(promedio_comensales, 1),
        "tasa_ocupacion": round(tasa_ocupacion, 1)
    }


def obtener_ocupacion_semanal(reservas: list, mesas: list, fecha_inicio: str) -> List[Dict]:
    fecha_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    resultados = []
    
    for i in range(7):
        fecha_actual = fecha_dt + timedelta(days=i)
        fecha_str = fecha_actual.date().isoformat()
        stats_dia = obtener_ocupacion_diaria(reservas, mesas, fecha_str)
        resultados.append({
            "fecha": fecha_str,
            "reservas": stats_dia["total_reservas"],
            "ocupacion": stats_dia["tasa_ocupacion"]
        })
    
    return resultados


def obtener_clientes_frecuentes(reservas: list, clientes: list) -> List[Dict]:
    conteo_por_cliente = defaultdict(int)
    
    for reserva in reservas:
        if reserva["estado"] != "cancelada":
            cliente_id = reserva["cliente_id"]
            conteo_por_cliente[cliente_id] += 1
    
    resultados = []
    for cliente_id, total_reservas in conteo_por_cliente.items():
        cliente = next((c for c in clientes if c["id"] == cliente_id), None)
        if cliente:
            resultados.append({
                "id": cliente_id,
                "nombre": cliente["nombre"],
                "email": cliente["email"],
                "total_reservas": total_reservas
            })
    
    resultados.sort(key=lambda x: x["total_reservas"], reverse=True)
    return resultados[:10]


def obtener_mesas_populares(reservas: list, mesas: list) -> List[Dict]:
    conteo_por_mesa = defaultdict(int)
    
    for reserva in reservas:
        if reserva["estado"] != "cancelada":
            mesa_id = reserva["mesa_id"]
            conteo_por_mesa[mesa_id] += 1
    
    resultados = []
    for mesa_id, veces_reservada in conteo_por_mesa.items():
        mesa = next((m for m in mesas if m["id"] == mesa_id), None)
        if mesa:
            resultados.append({
                "numero": mesa["numero"],
                "ubicacion": mesa["ubicacion"],
                "veces_reservada": veces_reservada
            })
    
    resultados.sort(key=lambda x: x["veces_reservada"], reverse=True)
    return resultados


def obtener_resumen_general(reservas: list, clientes: list, mesas: list) -> Dict:
    total_clientes = len(clientes)
    total_mesas = len(mesas)
    total_reservas = len(reservas)
    
    reservas_canceladas = len([r for r in reservas if r["estado"] == "cancelada"])
    
    ahora = datetime.now()
    reservas_activas = len([
        r for r in reservas 
        if r["estado"] in ["pendiente", "confirmada"] and r["fecha_hora_inicio"] > ahora
    ])
    
    if total_reservas > 0:
        tasa_cancelacion = (reservas_canceladas / total_reservas) * 100
    else:
        tasa_cancelacion = 0.0
    
    return {
        "total_clientes": total_clientes,
        "total_mesas": total_mesas,
        "total_reservas": total_reservas,
        "reservas_activas": reservas_activas,
        "tasa_cancelacion": round(tasa_cancelacion, 2)
    }