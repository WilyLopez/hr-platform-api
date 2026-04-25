import io
import csv
from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from modules.auditoria.domain.entities.registro_auditoria import RegistroAuditoria


class ExportacionService:
    def generar_csv(self, registros: List[RegistroAuditoria]) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "ID", "Empresa", "Usuario", "Rol", "Evento",
            "Descripción", "IP", "Timestamp",
        ])
        for r in registros:
            writer.writerow([
                r.id,
                r.empresa_id or "",
                r.usuario_id or "",
                r.rol_usuario or "",
                r.tipo_evento,
                r.descripcion,
                r.ip_address or "",
                r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        return buffer.getvalue().encode("utf-8-sig")

    def generar_pdf(self, registros: List[RegistroAuditoria]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Reporte de Auditoría — SisRRHH", styles["Title"]))
        elements.append(Paragraph(
            f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        ))
        elements.append(Spacer(1, 12))

        headers = ["ID", "Empresa", "Usuario", "Evento", "Descripción", "Timestamp"]
        data = [headers]
        for r in registros:
            data.append([
                str(r.id),
                str(r.empresa_id or ""),
                str(r.usuario_id or ""),
                r.tipo_evento,
                r.descripcion[:60],
                r.timestamp.strftime("%Y-%m-%d %H:%M"),
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
        ]))
        elements.append(table)
        doc.build(elements)
        return buffer.getvalue()