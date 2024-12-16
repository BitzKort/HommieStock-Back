def reporteSerializer(reporte) -> dict:
    return {
        "id": str(reporte["_id"]),
        "datos": reporte["datos"]
    }

def listReporteSerializer(reportes) -> list:
    return [reporteSerializer(reporte) for reporte in reportes]