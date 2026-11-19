"""Sustentation deck (PPTX with speaker notes) and speaking script for Corte 3.

The deck and Guion_Sustentacion.md come from the same SLIDES specification, so
times, speakers and notes cannot drift apart. Numbers come from corte3_data.
"""
import subprocess
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from corte3_data import COLORS, FIGURES, GROUP_NUMBER, RESERVE, es, pct

TOTAL_MINUTES = 30
QA_MINUTES = 5
W, H = Inches(13.333), Inches(7.5)
FONT = "Calibri"


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color.lstrip("#"))


NAVY, TEAL, AMBER, RED = rgb(COLORS["navy"]), rgb(COLORS["teal"]), rgb(COLORS["amber"]), rgb(COLORS["red"])
GRAY, LIGHT, INK, WHITE = rgb(COLORS["gray"]), rgb(COLORS["light"]), rgb(COLORS["ink"]), RGBColor(255, 255, 255)


# ---------------------------------------------------------------- primitives
def text(slide, x, y, w, h, content, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, font=FONT):
    """content: str or list of str / (str, dict) for paragraphs."""
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    paragraphs = content if isinstance(content, list) else [content]
    for i, item in enumerate(paragraphs):
        para_text, opts = (item, {}) if isinstance(item, str) else item
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = opts.get("align", align)
        p.space_after = Pt(opts.get("space", 6))
        bullet = opts.get("bullet", False)
        run = p.add_run()
        run.text = ("•  " if bullet else "") + para_text
        run.font.name = opts.get("font", font)
        run.font.size = Pt(opts.get("size", size))
        run.font.bold = opts.get("bold", bold)
        run.font.color.rgb = opts.get("color", color)
    return box


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    return s


def header(slide, title, kicker, number):
    rect(slide, 0, 0, Inches(0.18), H, NAVY)
    text(slide, Inches(0.55), Inches(0.28), Inches(11.5), Inches(0.35), kicker.upper(), size=12,
         color=TEAL, bold=True)
    text(slide, Inches(0.55), Inches(0.58), Inches(12.3), Inches(1.0), title, size=28, color=NAVY,
         bold=True)
    text(slide, Inches(0.55), Inches(7.05), Inches(9), Inches(0.3),
         "DataForge Consulting · FinBank S.A. · GMAC-FB-2026-01 · Corte 3", size=9, color=GRAY)
    text(slide, Inches(12.2), Inches(7.05), Inches(0.8), Inches(0.3), str(number), size=9, color=GRAY,
         align=PP_ALIGN.RIGHT)


def tag(slide, x, y, label, color):
    s = rect(slide, x, y, Inches(1.9), Inches(0.3), color, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tf = s.text_frame
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(10), True, WHITE, FONT


def kpi(slide, x, y, w, value, label, color=NAVY, h=Inches(1.45), value_size=34):
    rect(slide, x, y, w, h, rgb("#F3F4F6"))
    rect(slide, x, y, Inches(0.08), h, color)
    text(slide, x + Inches(0.2), y + Inches(0.08), w - Inches(0.3), Inches(0.75), value,
         size=value_size, color=color, bold=True)
    text(slide, x + Inches(0.2), y + Inches(0.8), w - Inches(0.3), h - Inches(0.85), label, size=12,
         color=INK)


def table(slide, x, y, w, rows, widths, header_fill=NAVY, size=11, row_h=Inches(0.34),
          highlight=None):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), x, y, w, row_h * len(rows))
    tbl = shape.table
    total = sum(widths)
    for i, width in enumerate(widths):
        tbl.columns[i].width = Emu(int(w * width / total))
    for r, row in enumerate(rows):
        tbl.rows[r].height = row_h
        for c, value in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if r == 0:
                cell.fill.fore_color.rgb = header_fill
            elif highlight and highlight(r, row):
                cell.fill.fore_color.rgb = rgb("#FDF2E9")
            else:
                cell.fill.fore_color.rgb = WHITE if r % 2 else rgb("#F7F8FA")
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = str(value)
            run.font.name = FONT
            run.font.size = Pt(size)
            run.font.bold = r == 0
            run.font.color.rgb = WHITE if r == 0 else INK
    return tbl


def picture(slide, name, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(FIGURES / f"{name}.png"), x, y, width=w, height=h)


# ---------------------------------------------------------------- slides
def s_cover(s, m, ev):
    rect(s, 0, 0, W, H, NAVY)
    rect(s, Inches(0.7), Inches(2.0), Inches(0.12), Inches(2.6), TEAL)
    text(s, Inches(1.05), Inches(1.0), Inches(10), Inches(0.5), "DATAFORGE CONSULTING · FINBANK S.A.",
         size=14, color=rgb("#9FD8CF"), bold=True)
    text(s, Inches(1.05), Inches(1.95), Inches(11.5), Inches(1.6),
         "Cierre del Programa de Analítica Predictiva", size=44, color=WHITE, bold=True)
    text(s, Inches(1.05), Inches(3.45), Inches(11), Inches(1.2),
         "Mora temprana y churn de crédito: qué entregamos, cuánto costó y qué decisión necesita FinBank",
         size=22, color=rgb("#D1D5DB"))
    text(s, Inches(1.05), Inches(5.2), Inches(11.5), Inches(1.2), [
        ("Daniel Felipe Martínez Hernández · Líder de proyecto", {"size": 16, "color": WHITE}),
        ("Rafael Alejandro Baracaldo Doikov · Product Owner", {"size": 16, "color": WHITE}),
        ("Oscar Santiago Merino Suárez · Scrum Master", {"size": 16, "color": WHITE}),
    ])
    text(s, Inches(1.05), Inches(6.75), Inches(11.5), Inches(0.4),
         f"GMAC · Corte 3 · Grupo {GROUP_NUMBER} · Escuela Colombiana de Ingeniería Julio Garavito · 20 de noviembre de 2026",
         size=12, color=rgb("#9CA3AF"))


def s_decision(s, m, ev):
    rect(s, Inches(0.55), Inches(1.75), Inches(12.2), Inches(1.3), rgb("#E8F5F3"))
    text(s, Inches(0.8), Inches(1.85), Inches(11.8), Inches(1.1), [
        ("Proponemos cerrar con transferencia condicionada", {"size": 26, "bold": True, "color": NAVY}),
        ("Los modelos, la regla de decisión y el piloto están listos. Solo falta la firma del acta, que espera "
         "la auditoría de protección de datos.", {"size": 16}),
    ])
    w = Inches(2.9)
    kpi(s, Inches(0.55), Inches(3.35), w, f"{m['s6_done']}/{m['s6_committed']}",
        "puntos del Sprint 6 que cumplen la DoD", TEAL)
    kpi(s, Inches(3.65), Inches(3.35), w, pct(m["cost_deviation"]),
        f"desviación de costo frente a la base\n(límite 5 %, reserva intacta)", NAVY)
    kpi(s, Inches(6.75), Inches(3.35), w, "Semana 12", "hito final a tiempo;\nM2 +3 y M4 +1 absorbidos", NAVY)
    kpi(s, Inches(9.85), Inches(3.35), w, es(m["pilot_metrics"]["auc_out_of_time_default_30d"], 2),
        "AUC fuera de tiempo, mora 30 d\n(prototipo sintético; meta 0,75)", AMBER)
    text(s, Inches(0.55), Inches(5.1), Inches(12.2), Inches(1.8), [
        ("Le pedimos tres cosas:", {"bold": True, "size": 17, "color": NAVY}),
        ("Aceptar el cierre con la condición de la firma, sin costo adicional ni extensión.", {"bullet": True}),
        ("Que Finanzas ratifique la regla de churn: priorizar recall ≥ 0,60 (O2) sobre el máximo beneficio (O3).",
         {"bullet": True}),
        ("Programar la validación con el extracto real, siguiendo el runbook.", {"bullet": True}),
    ], size=16)


def s_problem(s, m, ev):
    kpi(s, Inches(0.55), Inches(1.8), Inches(3.9), "COP 58.800 M", "exposición por mora sin alerta temprana",
        RED, value_size=30)
    kpi(s, Inches(0.55), Inches(3.4), Inches(3.9), "COP 18.200 M", "pérdidas por churn no anticipado",
        RED, value_size=30)
    kpi(s, Inches(0.55), Inches(5.0), Inches(3.9), "≈ 18 %", "de la cartera de COP 420.000 M está en juego",
        NAVY, value_size=30)
    rows = [["Obj.", "Compromiso del Charter", "Medida", "Sem."],
            ["O1", "Modelo de mora a 30/60 días", "AUC ≥ 0,75 fuera de tiempo", "6"],
            ["O2", "Modelo de churn a 3 meses", "Recall ≥ 0,60 al umbral", "8"],
            ["O3", "Umbral de máximo beneficio", "Aprobado por Finanzas", "10"],
            ["O4", "Transferir el marco de gestión", "Aceptación del patrocinador", "12"],
            ["O5", "Dentro del sobre", "Desviación ≤ 5 %", "12"]]
    table(s, Inches(4.8), Inches(1.8), Inches(8.0), rows, [0.6, 3, 2.6, 0.6], size=13, row_h=Inches(0.48))
    text(s, Inches(4.8), Inches(5.0), Inches(8.0), Inches(1.6), [
        ("Línea base fija: 12 semanas · 6 sprints · COP 180 M (169,2 por rubros + 10,8 de reserva).",
         {"size": 15}),
        ("El obstáculo no eran los datos sino la falta de un método para planear, controlar y cerrar.",
         {"size": 15, "color": GRAY}),
    ])


def s_journey(s, m, ev):
    picture(s, "velocity", Inches(0.55), Inches(1.7), w=Inches(6.6))
    y = Inches(1.75)
    notes = [("S1", "16/16", "Gobierno y acceso legal (M1)", TEAL),
             ("S2", "15/20", "Calidad y diccionario; churn bloqueado por TI", RED),
             ("S3", "16/16", "Modelo de mora validado (M3); nace la DoR", TEAL),
             ("S4", "13/16", "Extracto de churn; M2 cierra en la semana 7", AMBER),
             ("S5", "16/16", "Churn validado (M4, +1 sem.); reglas con Finanzas (M5)", TEAL),
             ("S6", "12/15", "Piloto, monitoreo y transferencia (M6, condicionado)", AMBER)]
    for sprint, pts, label, color in notes:
        rect(s, Inches(7.45), y, Inches(0.7), Inches(0.62), color)
        text(s, Inches(7.45), y, Inches(0.7), Inches(0.62), sprint, size=16, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, Inches(8.25), y - Inches(0.02), Inches(4.7), Inches(0.66), [
            (f"{pts} puntos", {"bold": True, "size": 13, "space": 0}), (label, {"size": 12})])
        y += Inches(0.8)
    text(s, Inches(0.55), Inches(5.75), Inches(6.6), Inches(1.2), [
        (f"{m['points_done_total']} puntos en 6 sprints. Media S1–S5: {es(m['velocity_avg_s1_s5'])}.",
         {"bold": True, "size": 15, "color": NAVY}),
        ("De S3 a S6, solo S6 respetó la media previa. S3–S5 comprometieron 16 puntos cada uno.",
         {"size": 13, "color": GRAY}),
    ])


def s_board(s, m, ev):
    cols = [("Backlog", GRAY), ("Ready", TEAL), ("In Progress", AMBER), ("Blocked", RED),
            ("Review", NAVY), ("Done", rgb("#006B75"))]
    rules = ["Priorizado por el PO; pedidos nuevos entran aquí (R6)",
             "Cumple DoR: criterios, puntos, dueño de negocio, sin dependencia externa pendiente",
             "WIP máximo 3", "Causa y responsable escritos; escalación en 24 h",
             "PR abierto + CI verde + revisión de un par", "PR fusionado y DoD completa"]
    x = Inches(0.55)
    for (name, color), rule in zip(cols, rules):
        rect(s, x, Inches(1.8), Inches(1.95), Inches(0.55), color)
        text(s, x, Inches(1.8), Inches(1.95), Inches(0.55), name, size=15, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        rect(s, x, Inches(2.35), Inches(1.95), Inches(1.45), rgb("#F7F8FA"))
        text(s, x + Inches(0.08), Inches(2.42), Inches(1.8), Inches(1.35), rule, size=11.5)
        x += Inches(2.05)
    text(s, Inches(0.55), Inches(4.05), Inches(6.2), Inches(2.8), [
        ("Definition of Done (Charter + Corte 2)", {"bold": True, "size": 16, "color": NAVY}),
        ("Reproducible desde el repositorio", {"bullet": True}),
        ("Documentada", {"bullet": True}),
        ("Pruebas en verde en CI", {"bullet": True}),
        ("PR aprobado por un integrante distinto del autor", {"bullet": True}),
        ("Validada por el responsable de negocio", {"bullet": True}),
        ("Demostrada en la Sprint Review", {"bullet": True}),
    ], size=14)
    text(s, Inches(7.0), Inches(4.05), Inches(5.8), Inches(2.8), [
        ("Dónde vive el tablero", {"bold": True, "size": 16, "color": NAVY}),
        ("Issues #10–#15 con etiquetas estado:* y milestone «Corte 3 · S6».", {"bullet": True}),
        ("Vista reproducible: TABLERO.md, generada desde la API de GitHub.", {"bullet": True}),
        ("Separamos tres cosas: integrado (GitHub), Done del escenario y aceptación real del negocio.",
         {"bullet": True}),
        ("Antecedente: Trello del Corte 1 (PMBOK + Kanban).", {"bullet": True, "color": GRAY}),
    ], size=14)


def s_story(s, m, ev):
    steps = [("Backlog", "US-07 lista semanal\n(pronóstico de S3)", GRAY),
             ("Ready", "S6-01 · 5 pts · DoR\nissue #10", TEAL),
             ("In Progress", "Pairing Rafael/Oscar\nrama c3/s6/s6-01-piloto", AMBER),
             ("Blocked", "D3–D5: ambiente de TI\nescalado en D4", RED),
             ("Review", "PR #17 · CI verde\nrevisión por un par", NAVY),
             ("Done (esc.)", "D8: Cobranza valida\ndemo en la Review", rgb("#006B75"))]
    x = Inches(0.55)
    for i, (col, body, color) in enumerate(steps):
        rect(s, x, Inches(1.85), Inches(1.95), Inches(0.5), color, shape=MSO_SHAPE.CHEVRON if i else
             MSO_SHAPE.PENTAGON)
        text(s, x + Inches(0.15), Inches(1.85), Inches(1.7), Inches(0.5), col, size=13, color=WHITE,
             bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, x, Inches(2.45), Inches(1.95), Inches(0.9), body, size=11.5, align=PP_ALIGN.CENTER)
        x += Inches(2.05)
    pm = m["pilot_metrics"]
    text(s, Inches(0.55), Inches(3.6), Inches(6.2), Inches(3.2), [
        ("Criterios de aceptación (Dado / Cuando / Entonces)", {"bold": True, "size": 15, "color": NAVY}),
        ("Lista con clave seudonimizada, sin columnas personales.  ✔ prueba automática", {"bullet": True}),
        ("Métricas rotuladas como prototipo sintético.  ✔ pilot_metrics.csv", {"bullet": True}),
        ("Dos corridas idénticas.  ✔ hashes iguales", {"bullet": True}),
        ("Validación de Cobranza.  ✔ escenario · ✘ real pendiente", {"bullet": True}),
    ], size=13.5)
    rect(s, Inches(7.0), Inches(3.6), Inches(5.8), Inches(3.1), rgb("#F7F8FA"))
    text(s, Inches(7.2), Inches(3.7), Inches(5.5), Inches(2.9), [
        ("Evidencia en GitHub", {"bold": True, "size": 15, "color": NAVY}),
        ("La issue #10 registra los criterios y el cierre.", {"bullet": True}),
        ("PR #17: 33 pruebas y ejecución del piloto en CI.", {"bullet": True}),
        ("PR #17 aprobado e integrado en main.", {"bullet": True}),
        (f"Paquete de cierre: {ev['tests_passed']} pruebas.", {"bullet": True}),
        (f"AUC {es(pm['auc_out_of_time_default_30d'], 4)} · {m['ew_flagged']} de {m['ew_total']} "
         "clientes en la lista", {"size": 13, "color": GRAY}),
    ], size=13.5)


def s_sprint6(s, m, ev):
    text(s, Inches(0.55), Inches(1.65), Inches(12.2), Inches(0.9), [
        ("Objetivo: el piloto opera en el segmento controlado y el paquete de transferencia queda listo para la "
         "firma (M6).", {"size": 17, "bold": True, "color": NAVY}),
        (f"Capacidad: media S1–S5 = {es(m['velocity_avg_s1_s5'])} → compromiso de {m['s6_committed']} "
         "puntos (regla de la retrospectiva de S2). Compromiso publicado en GitHub antes de empezar.",
         {"size": 14, "color": GRAY}),
    ])
    rows = [["ID", "Historia", "Pts", "Responsable", "Dependencia", "Issue / PR", "Estado (esc.)"]]
    items = {it["id"]: it for it in m["s6_items"]}
    prs = {g["id"]: g["pr"] for g in m["github"]}
    for b in m["s6_backlog"]:
        rows.append([b["id"], b["item"], b["points"], b["owner"], b["dependency"],
                     f"#{int(items[b['id']]['github_issue'])} / #{prs.get(b['id']) or '—'}", b["state"]])
    table(s, Inches(0.55), Inches(2.75), Inches(12.2), rows, [0.8, 4.2, 0.5, 1.5, 2.6, 1.2, 2.1], size=12,
          row_h=Inches(0.6), highlight=lambda r, row: "No terminado" in str(row[-1]))
    text(s, Inches(0.55), Inches(6.45), Inches(12.2), Inches(0.5),
         "Cambio de alcance en D5 (Retención pidió explicaciones por cliente): pasó al Product Backlog como "
         "US-10 y no entró al sprint (R6).", size=13, color=GRAY)


def s_burndown(s, m, ev):
    picture(s, "burndown_s6", Inches(0.55), Inches(1.65), w=Inches(7.6))
    rows = [["Métrica", "Valor"],
            ["Velocidad S6", f"{m['s6_done']} de {m['s6_committed']} pts"],
            ["Throughput", f"{m['throughput']} ítems"],
            ["Tiempo de ciclo medio", f"{es(m['cycle_avg'], 2)} días"],
            ["Días bloqueados", f"{m['blocked_days']} (S6-01)"],
            ["WIP máximo", f"{m['wip_max']} de 3"],
            ["Cambios de alcance", "1, fuera del sprint"]]
    table(s, Inches(8.5), Inches(1.75), Inches(4.3), rows, [2.2, 1.8], size=13, row_h=Inches(0.45))
    text(s, Inches(8.5), Inches(5.1), Inches(4.3), Inches(1.8), [
        ("Lectura", {"bold": True, "color": NAVY, "size": 15}),
        ("Los puntos bajan solo cuando el ítem cumple la DoD. Los 3 pendientes son S6-04: un acto externo, no "
         "un exceso de compromiso como en S2.", {"size": 13}),
    ])


def s_impediments(s, m, ev):
    rows = [["Impedimento", "Días", "Respuesta", "Efecto"],
            ["S2–S3 · Credencial de TI para el extracto de churn (R1)", "9",
             "Blocked el D6, escalación el D7, reordenación del sprint. No se usaron los COP 4,2 M de la reserva",
             "M2 +3 sem., M4 +1 sem. → nace la Definition of Ready"],
            ["S6 · Ambiente de piloto sin cuenta de servicio", "3",
             "Escalación en menos de 24 h; el PO adelantó S6-02; la demo siguió sobre la réplica sintética",
             "Sin efecto en el hito"],
            ["S6 · Auditoría de protección de datos: sal de demostración", "D10",
             "Hallazgo registrado; cierre condicionado sin costo",
             "3 pts pendientes; firma del acta en espera"],
            ["S6 · Pedido nuevo de Retención (US-10)", "D5", "Al Product Backlog, no al sprint",
             "Objetivo del sprint protegido"]]
    table(s, Inches(0.55), Inches(1.75), Inches(12.2), rows, [3.4, 0.6, 4.6, 3.2], size=12.5,
          row_h=Inches(0.85))
    text(s, Inches(0.55), Inches(6.2), Inches(12.2), Inches(0.7),
         "Patrón: las causas estuvieron fuera del equipo; la respuesta siguió reglas que el equipo ya había "
         "escrito. El límite: un acto de cumplimiento que llega el último día no se puede reordenar.",
         size=14, color=NAVY, bold=True)


def s_pilot(s, m, ev):
    pm = m["pilot_metrics"]
    tag(s, Inches(0.55), Inches(1.65), "PROTOTIPO SINTÉTICO", AMBER)
    kpi(s, Inches(0.55), Inches(2.1), Inches(3.0), es(pm["auc_out_of_time_default_30d"], 4),
        "AUC fuera de tiempo, mora 30 d (meta 0,75)", TEAL)
    kpi(s, Inches(3.75), Inches(2.1), Inches(3.0), es(pm["auc_out_of_time_default_60d"], 4),
        "AUC fuera de tiempo, mora 60 d", TEAL)
    kpi(s, Inches(0.55), Inches(3.8), Inches(3.0), f"{m['ew_flagged']}",
        f"de {es(m['ew_total'], 0)} clientes del segmento andino en la lista semanal", NAVY)
    kpi(s, Inches(3.75), Inches(3.8), Inches(3.0), es(pm["cutoff_delinquency_threshold"], 2),
        "umbral de mora con máximo beneficio neto", NAVY)
    text(s, Inches(7.1), Inches(1.75), Inches(5.7), Inches(4.8), [
        ("Qué hace el piloto (S6-01)", {"bold": True, "size": 16, "color": NAVY}),
        ("Entrena con las 18 variables del diccionario y valida con una cohorte posterior independiente.",
         {"bullet": True}),
        ("Lista para Cobranza: clave SHA-256 con sal, probabilidad, decil y acción. Sin datos personales.",
         {"bullet": True}),
        ("Corre en CI en cada push; dos corridas dan los mismos hashes.", {"bullet": True}),
        ("Qué no prueba todavía", {"bold": True, "size": 16, "color": RED}),
        ("Desempeño con datos reales de FinBank: el runbook (sección 6) explica cómo cambiar el generador "
         "por el extracto.", {"bullet": True}),
    ], size=14)
    text(s, Inches(0.55), Inches(5.55), Inches(6.2), Inches(1.2),
         f"Validación fuera de tiempo sobre {es(m['pilot_samples']['auc_out_of_time_default_30d'], 0)} "
         f"clientes con observación; tasa de mora a 30 d de {pct(m['pilot_rates']['auc_out_of_time_default_30d'])}.",
         size=12, color=GRAY)


def s_churn(s, m, ev):
    pm = m["pilot_metrics"]
    picture(s, "churn_tradeoff", Inches(0.55), Inches(1.65), w=Inches(7.4))
    diff = (pm["net_benefit_cop_at_cost_only_threshold"] - pm["net_benefit_cop_at_operating_threshold"]) / 1e6
    rows = [["Umbral", "Recall", "Precisión", "Beneficio neto"],
            [f"Operativo {es(pm['cutoff_operating_threshold'], 2)}", es(pm["recall_at_operating_threshold"], 3),
             es(pm["precision_at_operating_threshold"], 3),
             f"COP {es(pm['net_benefit_cop_at_operating_threshold'] / 1e6, 2)} M"],
            [f"Solo costo {es(pm['cutoff_cost_only_threshold'], 2)}", es(pm["recall_at_cost_only_threshold"], 3),
             es(pm["precision_at_cost_only_threshold"], 3),
             f"COP {es(pm['net_benefit_cop_at_cost_only_threshold'] / 1e6, 2)} M"]]
    table(s, Inches(8.25), Inches(1.8), Inches(4.6), rows, [1.6, 0.9, 1.0, 1.4], size=12, row_h=Inches(0.5))
    text(s, Inches(8.25), Inches(3.5), Inches(4.6), Inches(3.3), [
        ("La decisión para Finanzas", {"bold": True, "size": 16, "color": NAVY}),
        ("El umbral de máximo beneficio incumple O2: identifica solo a 4 de cada 10 clientes que se van.",
         {"bullet": True}),
        (f"Cumplir O2 cuesta COP {es(diff, 2)} M de beneficio en la cohorte sintética.", {"bullet": True}),
        ("Proponemos el umbral operativo: mayor beneficio entre los que cumplen recall ≥ 0,60.",
         {"bullet": True, "bold": True}),
        ("Matriz de costos: parámetros del escenario, no montos aprobados.", {"size": 12, "color": GRAY}),
    ], size=13.5)


def s_demo(s, m, ev):
    rect(s, Inches(0.55), Inches(1.7), Inches(7.3), Inches(4.9), rgb("#111827"))
    lines = [ln for ln in ev["pilot_output"].splitlines() if ln.strip()][:20]
    text(s, Inches(0.7), Inches(1.8), Inches(7.1), Inches(4.7),
         [("$ python scripts/run_pilot.py", {"color": rgb("#9FD8CF"), "space": 2})]
         + [(ln, {"space": 0}) for ln in lines], size=10.5, color=rgb("#E5E7EB"), font="Consolas")
    text(s, Inches(8.15), Inches(1.75), Inches(4.7), Inches(4.9), [
        ("Guion de la demo (2,5 min)", {"bold": True, "size": 16, "color": NAVY}),
        ("1. pytest -q → todas en verde.", {"size": 14}),
        ("2. python scripts/run_pilot.py → métricas, lista y hashes.", {"size": 14}),
        ("3. Abrir early_warning_list.csv: solo clave, probabilidad, decil y acción.", {"size": 14}),
        ("4. python scripts/run_monitoring.py. Semana 4: score en vigilar (0,243) y bureau_score en alerta (0,396). "
         "Semana 5: marca de reentrenamiento.", {"size": 14}),
        ("Respaldo", {"bold": True, "size": 15, "color": RED}),
        ("Si falla la red o el equipo: esta salida es la ejecución registrada (docs/corte3/evidence/) y la "
         "diapositiva B2 muestra el monitoreo.", {"size": 13}),
    ])


def s_monitoring(s, m, ev):
    picture(s, "monitoring", Inches(0.55), Inches(1.65), w=Inches(7.6))
    text(s, Inches(0.55), Inches(4.85), Inches(7.6), Inches(1.9), [
        ("PSI estable < 0,10 · vigilar desde 0,10 · alerta desde 0,25.", {"size": 13}),
        ("En la semana 4 coinciden la alerta de bureau_score y la caída del AUC.", {"size": 13}),
        ("Se marca reentrenamiento si el AUC o el recall cae más de 0,05 frente a su base durante dos "
         "semanas seguidas. En la demo se activa en la semana 5 por AUC.", {"size": 13, "color": GRAY}),
    ])
    rows = [["Paquete de transferencia (S6-04)", "Estado"],
            ["Tablero, backlog, DoR y DoD", "Entregado"],
            ["Modelos y regla de decisión", "Prototipo · Finanzas pendiente"],
            ["Plan de monitoreo y runbook (S6-03)", "Entregado"],
            ["Capacitación: 3 sesiones", "Escenario D8 · real pendiente"],
            ["Auditoría de protección de datos", "Hallazgo: sal propia"],
            ["Acta de entrega", "Firma real pendiente"]]
    table(s, Inches(8.5), Inches(1.75), Inches(4.3), rows, [2.4, 1.9], size=11.5, row_h=Inches(0.55),
          highlight=lambda r, row: "pendiente" in row[1].lower() or "Hallazgo" in row[1])


def s_milestones(s, m, ev):
    picture(s, "milestones", Inches(0.55), Inches(1.65), w=Inches(7.9))
    text(s, Inches(8.7), Inches(1.8), Inches(4.1), Inches(4.9), [
        ("Cronograma", {"bold": True, "size": 16, "color": NAVY}),
        ("Hito final en la semana 12: desviación de 0 semanas.", {"bullet": True}),
        ("M2 (+3) y M4 (+1): misma causa, el extracto de churn.", {"bullet": True}),
        ("Ningún trabajo de churn se dio por terminado sin el extracto.", {"bullet": True}),
        ("M3, M5 y M6 en su semana. M6 está condicionado a la firma.", {"bullet": True}),
        ("Calendarios", {"bold": True, "size": 16, "color": NAVY}),
        ("Escenario: agosto a octubre de 2026. Académico: entrega el 18 y sustentación el 20 de noviembre.",
         {"size": 13, "color": GRAY}),
    ], size=14)


def s_budget(s, m, ev):
    picture(s, "budget_cumulative", Inches(0.55), Inches(1.65), w=Inches(7.4))
    rows = [["COP millones", "Base", "Gasto", "Desv."]]
    for b in m["budget_by_item"]:
        rows.append([b["item"], es(b["base"]), es(b["actual"]), pct(b["deviation"], 1)])
    rows.append(["Total sin reserva", es(m["base_total"]), es(m["actual_total"]), pct(m["cost_deviation"])])
    rows.append(["Reserva (no liberada)", es(RESERVE), "0,0", "—"])
    table(s, Inches(8.2), Inches(1.75), Inches(4.65), rows, [2.4, 0.8, 0.8, 0.8], size=11,
          row_h=Inches(0.42))
    text(s, Inches(8.2), Inches(5.3), Inches(4.65), Inches(1.6), [
        (f"Pronóstico al iniciar S6: {es(m['eac_at_s6_start'])}. Cierre: {es(m['actual_total'])}.",
         {"size": 13, "bold": True, "color": NAVY}),
        ("Gestión superó su base un 4,8 % por las escalaciones y la auditoría. Validación quedó por debajo y "
         "compensó sin tocar la reserva.", {"size": 12}),
    ])


def s_retro(s, m, ev):
    cols = [("Empezar", ["Pedir la auditoría de protección de datos en la Planning",
                         "Cuenta de servicio del ambiente de piloto dentro de la DoR"], TEAL),
            ("Dejar de", ["Leer «integrado en GitHub» como «aceptado por el negocio»",
                          "Dejar los actos de cumplimiento para la Review"], RED),
            ("Continuar", ["Limitar el compromiso a la media previa, como en S6",
                           "Escalar en menos de 24 h y reordenar con el PO",
                           "Pruebas y PR revisado por un par en cada historia"], NAVY)]
    x = Inches(0.55)
    for title, items, color in cols:
        rect(s, x, Inches(1.75), Inches(3.95), Inches(0.5), color)
        text(s, x, Inches(1.75), Inches(3.95), Inches(0.5), title, size=16, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        rect(s, x, Inches(2.25), Inches(3.95), Inches(2.1), rgb("#F7F8FA"))
        text(s, x + Inches(0.1), Inches(2.35), Inches(3.75), Inches(2.0),
             [(i, {"bullet": True}) for i in items], size=13)
        x += Inches(4.12)
    text(s, Inches(0.55), Inches(4.6), Inches(12.2), Inches(2.3), [
        ("Aprendizajes de liderazgo y coordinación", {"bold": True, "size": 16, "color": NAVY}),
        ("Daniel: el patrocinador supo de cada problema antes de que se volviera desviación.", {"bullet": True}),
        ("Rafael: decir «no en este sprint» (US-10) protegió el objetivo sin perder el pedido.", {"bullet": True}),
        ("Oscar: escribir las reglas del tablero hizo que cada bloqueo tuviera dueño y plazo.", {"bullet": True}),
        ("Separar los roles (líder, PO, SM) evitó que una sola persona decidiera alcance y plazo a la vez.", {"bullet": True}),
    ], size=14)


def s_close(s, m, ev):
    rect(s, Inches(0.55), Inches(1.7), Inches(12.2), Inches(1.15), rgb("#E8F5F3"))
    text(s, Inches(0.8), Inches(1.78), Inches(11.8), Inches(1.0), [
        ("Decisión de la Review de S6 (escenario): cierre con transferencia condicionada",
         {"size": 20, "bold": True, "color": NAVY}),
        ("Firma del acta en 5 días hábiles, después de la auditoría. Sin costo adicional, sin extensión, sin "
         "liberar la reserva.", {"size": 14}),
    ])
    rows = [["Pendiente real (no simulado)", "Quién lo resuelve"],
            ["Firma del acta de entrega (O4)", "Patrocinador, tras el oficial de protección de datos"],
            ["Regla de churn: O2 sobre O3", "Finanzas"],
            ["O1 y O2 con el extracto real", "VP de Riesgo y TI (runbook, sección 6)"],
            ["Aprobación e integración de los PR del Corte 3", "Daniel o Rafael, en los PR que no escribieron"],
            ["Validación de Cobranza y capacitación reales", "Gerencia de Cobranza · VP de Riesgo"]]
    table(s, Inches(0.55), Inches(3.1), Inches(12.2), rows, [5, 5], size=13, row_h=Inches(0.5))
    text(s, Inches(0.55), Inches(6.25), Inches(12.2), Inches(0.6),
         "Continuar, redirigir o cerrar: la recomendación es cerrar. El marco queda en manos de FinBank.",
         size=16, bold=True, color=NAVY)


def s_qa(s, m, ev):
    rect(s, 0, 0, W, H, NAVY)
    text(s, Inches(0.9), Inches(2.4), Inches(11.5), Inches(1.2), "Preguntas", size=54, color=WHITE, bold=True)
    text(s, Inches(0.9), Inches(3.6), Inches(11.5), Inches(1.6), [
        ("Sitio: oscarsantiagomerino.github.io/DataForge-Consulting", {"size": 20, "color": WHITE, "bold": True}),
        ("Repositorio: github.com/OscarSantiagoMerino/DataForge-Consulting", {"size": 18, "color": rgb("#D1D5DB")}),
        ("Informe Final, registro de aceptación y evidencia en docs/corte3/", {"size": 18, "color": rgb("#D1D5DB")}),
    ])


def s_backup_github(s, m, ev):
    rows = [["ID", "Issue", "Columna", "PR", "CI", "Aprobación", "Merge"]]
    for g in m["github"]:
        rows.append([g["id"], f"#{g['issue']}", g["board_column"], f"#{g['pr']}" if g["pr"] else "—",
                     g["ci"].lower() or "—", g["approved_by"] or "pendiente", g["merge_sha"] or "pendiente"])
    top, row_height = Inches(1.75), Inches(0.42)
    table(s, Inches(0.55), top, Inches(12.2), rows, [1, 0.8, 1.2, 0.8, 1, 1.6, 1.4], size=12,
          row_h=row_height)
    text(s, Inches(0.55), top + len(rows) * row_height + Inches(0.2), Inches(12.2), Inches(0.75),
         f"Leído de la API de GitHub con scripts/github_snapshot.py. Integración con merge commit, en orden, "
         f"después de la aprobación de un par. Commit de esta compilación: {ev['sha']}.", size=13, color=GRAY)


def s_backup_monitor(s, m, ev):
    rows = [["Semana", "PSI score", "Estado", "Variable (PSI)", "AUC 30 d", "Caída AUC",
             "Recall 30 d", "Caída recall", "Reentrenar"]]
    for r in m["monitoring"]:
        rows.append([r["week"], es(r["psi_score"], 3), r["psi_score_status"],
                     f"{r['top_variable']} ({es(r['psi_top_variable'], 3)})", es(r["auc_30d"], 3),
                     es(r["auc_drop"], 3), es(r["recall_30d"], 3), es(r["recall_drop"], 3),
                     "sí" if r["retraining_flag"] else "no"])
    table(s, Inches(0.55), Inches(1.75), Inches(12.2), rows, [0.8, 1, 1, 2.5, 1, 1, 1, 1.2, 1.2], size=12,
          row_h=Inches(0.5), highlight=lambda r, row: row[-1] == "sí")
    text(s, Inches(0.55), Inches(5.5), Inches(12.2), Inches(1.2),
         "Salida registrada de python scripts/run_monitoring.py (docs/corte3/evidence/monitoring.txt). "
         "Datos sintéticos con un cambio inyectado desde la semana 4.", size=13, color=GRAY)


def s_backup_budget(s, m, ev):
    rows = [["Sprint", "Base", "Gasto", "Base acum.", "Gasto acum.", "Desv. acum.", "Rótulo"]]
    for b in m["budget_by_sprint"]:
        rows.append([b["sprint"], es(b["base"]), es(b["actual"]), es(b["cum_base"]), es(b["cum_actual"]),
                     pct(b["deviation"]), b["label"]])
    table(s, Inches(0.55), Inches(1.75), Inches(12.2), rows, [0.7, 0.8, 0.8, 1, 1, 1, 2.8], size=13,
          row_h=Inches(0.5))
    text(s, Inches(0.55), Inches(5.6), Inches(12.2), Inches(1.2),
         "Desviación acumulada = (gasto acum. − base acum.) / base acum. S2 (54,8 frente a 56,4) es el dato "
         "histórico del Corte 2. La reserva de COP 10,8 M no se asigna a ningún sprint.", size=13, color=GRAY)


# (key, title, kicker, speaker, minutes, builder, notes)
SLIDES = [
    ("portada", "", "", "Daniel", 0.5, s_cover,
     f"Buenos días. Somos DataForge Consulting, Grupo {GROUP_NUMBER}. FinBank quiere anticipar la mora y "
     "la cancelación de créditos para que Cobranza y Retención puedan actuar a tiempo. Presentaremos el "
     "piloto sobre datos sintéticos y el balance de las doce semanas. Luego revisaremos qué debe ocurrir "
     "para que FinBank pueda operar el programa. Transición: empiezo por nuestra recomendación."),
    ("decision", "La decisión que necesita FinBank hoy", "Recomendación", "Daniel", 2.0, s_decision,
     "Nuestra recomendación es cerrar con transferencia condicionada. El sprint final terminó 12 de 15 puntos. "
     "Los 3 que faltan son la firma del acta, que espera la auditoría de protección de datos. El costo cerró "
     "0,12 % por debajo de la base y la reserva está intacta. El hito final llegó en la semana 12. Los modelos "
     "cumplen las metas, pero sobre datos sintéticos: lo decimos desde ahora. Pedimos tres decisiones. "
     "Transición: Para entender por qué importan, volvamos al problema."),
    ("problema", "COP 77.000 millones se pierden por enterarse tarde", "Problema y alcance", "Daniel", 1.5,
     s_problem,
     "FinBank registraba la mora cuando el pago ya se había perdido y la cancelación cuando el cliente ya se "
     "había ido. El Charter fijó cinco objetivos medibles y una base que no se mueve: 12 semanas y 180 "
     "millones. Transición: Oscar cuenta cómo recorrimos esas doce semanas."),
    ("trayectoria", "S6 ajustó el compromiso a la velocidad anterior", "Trayectoria S1–S6", "Oscar",
     2.0, s_journey,
     "S1 y S2 vienen del Corte 2. En S2 comprometimos 20 y cerramos 15 porque el extracto de churn dependía de "
     "una credencial de TI. De ahí salió la Definition of Ready. Por eso la credencial, que llegó el día 2 de "
     "S3, no entró a ese sprint. S4 cerró 13 porque la validación de churn necesitaba tres meses de "
     "observación. S3, S4 y S5 comprometieron 16 puntos frente a medias previas de 15,5, 15,7 y 15,0. "
     "S6 comprometió 15 frente a 15,2 y cumplió el límite. Transición: así se veía el tablero."),
    ("tablero", "El tablero hace visible cada bloqueo y cada aceptación", "Gestión del flujo", "Oscar", 2.0,
     s_board,
     "Seis columnas con reglas escritas. WIP máximo de 3. Un bloqueo se escribe con su causa y se escala en "
     "24 horas. Algo importante: separamos tres estados que se suelen confundir: integrado en GitHub, Done del "
     "escenario y aceptado por el negocio. Transición: Rafael sigue una historia de punta a punta."),
    ("historia", "S6-01: una historia trazable de punta a punta", "Trazabilidad", "Rafael", 2.5, s_story,
     "La lista semanal nació como US-07 en el pronóstico de S3 y se convirtió en S6-01. Entró a Ready con 5 "
     "puntos y criterios Dado/Cuando/Entonces, se trabajó en pairing y se bloqueó tres días por el ambiente de "
     "TI. La issue #10 quedó cerrada y el PR #17 está integrado. Las 33 pruebas del PR corresponden al "
     "piloto. La validación con datos reales queda pendiente. Transición: veamos el sprint completo."),
    ("sprint6", "Sprint 6: 15 puntos comprometidos según la velocidad demostrada", "Sprint final", "Rafael", 1.5,
     s_sprint6,
     "El objetivo era doble: el piloto operando y el paquete listo para la firma. Cinco historias. La única "
     "que no cumple la DoD es S6-04, y la marcamos así. El pedido nuevo de Retención no entró: está en el "
     "Product Backlog. Transición: Oscar muestra el burndown."),
    ("burndown", "Burndown: 12 de 15 puntos, y el faltante no es de capacidad", "Métricas", "Oscar", 2.0,
     s_burndown,
     "Los puntos bajan solo cuando el ítem cumple la DoD. La curva queda plana tres días por el bloqueo y se "
     "recupera desde el día 6. Velocidad, throughput, tiempo de ciclo y WIP son métricas distintas y por eso "
     "las mostramos por separado. Transición: ¿qué nos frenó?"),
    ("impedimentos", "Los impedimentos vinieron de fuera; la respuesta, de nuestras reglas", "Impedimentos",
     "Oscar", 1.5, s_impediments,
     "Cuatro eventos. El de TI en S2 cambió el plan del proyecto. El de S6 no movió el hito. La auditoría es "
     "la lección principal: llegó el último día. Transición: Rafael, los resultados."),
    ("piloto", "El piloto produce la lista semanal con un AUC de 0,80", "Resultados (prototipo)", "Rafael", 1.5,
     s_pilot,
     "Subrayo que es un prototipo sobre datos sintéticos con semilla fija. Prueba que el método funciona de "
     "punta a punta y deja todo listo para cambiar el generador por el extracto. No presentamos ninguna cifra "
     "que el código no produzca. Transición: el hallazgo más interesante fue el de churn."),
    ("churn", "Churn: cumplir O2 cuesta beneficio y la decisión es de Finanzas", "Regla de decisión", "Rafael",
     2.0, s_churn,
     "El umbral que maximiza beneficio deja escapar a 6 de cada 10 clientes que se van, y eso incumple O2. "
     "Cumplir O2 cuesta 8,5 millones en la cohorte sintética. Proponemos el umbral operativo y pedimos que "
     "Finanzas lo ratifique. Transición: vamos a la demo."),
    ("demo", "Demo: del repositorio a la lista en un comando", "Demo breve", "Rafael", 2.5, s_demo,
     "Corro pytest, luego el piloto, abro la lista y corro el monitoreo. Si algo falla, esta salida es la "
     "ejecución registrada y la diapositiva B2 tiene el monitoreo. Transición: Oscar, monitoreo y transferencia."),
    ("monitoreo", "El monitoreo detectó el cambio en la semana 4", "Operación y transferencia", "Oscar",
     1.5, s_monitoring,
     "En la semana 4, el score quedó en vigilar, bureau_score activó una alerta y el AUC bajó. "
     "El control evalúa rachas independientes de AUC y recall, y en la demo marca reentrenamiento "
     "en la semana 5 por la segunda caída de AUC. El paquete de transferencia está completo, salvo lo que depende de actos "
     "reales. Transición: Daniel, el balance."),
    ("hitos", "Hitos: el final en la semana 12; dos desplazamientos absorbidos", "Cronograma", "Daniel", 1.5,
     s_milestones,
     "M2 y M4 se desplazaron por la misma causa. El resto llegó en su semana. Distinguimos la cronología del "
     "escenario de las fechas académicas. Transición: el dinero."),
    ("presupuesto", "Presupuesto: 169,0 frente a 169,2 millones, sin tocar la reserva", "Costo", "Daniel", 2.0,
     s_budget,
     "Base aprobada, gasto, pronóstico y reserva por separado. En S2 íbamos 2,8 % por debajo. Cerramos 0,12 % "
     "por debajo. Gestión superó su rubro por las escalaciones, pero el total queda dentro del límite. "
     "Transición: lo que aprendimos."),
    ("retro", "Lo que aprendimos como equipo y como líderes", "Retrospectiva", "Oscar", 2.0, s_retro,
     "Oscar abre y cada uno dice su aprendizaje en una frase. Daniel: comunicación temprana con el "
     "patrocinador. Rafael: decir que no en este sprint. Oscar: reglas escritas. Transición: Daniel cierra."),
    ("cierre", "Recomendamos cerrar; estos pendientes tienen dueño", "Decisión de cierre", "Daniel", 1.5,
     s_close,
     "La decisión del escenario es el cierre condicionado. Los pendientes reales no los simulamos: cada uno "
     "tiene dueño. Gracias. Abrimos preguntas."),
    ("preguntas", "", "", "Todos", QA_MINUTES, s_qa, "Cinco minutos de preguntas. Ver respuestas preparadas."),
    ("backup_github", "B1 · Evidencia de GitHub", "Respaldo", "Oscar", 0, s_backup_github,
     "Respaldo si preguntan por las aprobaciones o el CI."),
    ("backup_monitor", "B2 · Salida del monitoreo", "Respaldo de la demo", "Rafael", 0, s_backup_monitor,
     "Respaldo si falla la demo en vivo."),
    ("backup_budget", "B3 · Presupuesto por sprint", "Respaldo", "Daniel", 0, s_backup_budget,
     "Respaldo si preguntan por la fórmula de desviación."),
]

QA = [
    ("¿Los modelos cumplen O1 y O2?", "Rafael",
     "En el prototipo sí: AUC fuera de tiempo de 0,7959 y recall de 0,6203 al umbral operativo, sobre datos "
     "sintéticos. Con datos de FinBank no está acreditado; la sección 6 del runbook dice cómo hacerlo."),
    ("¿Por qué no usar el umbral de máximo beneficio?", "Rafael",
     "Porque incumple O2: su recall es de 0,41. La regla propuesta toma el mayor beneficio entre los umbrales "
     "con recall ≥ 0,60. La última palabra es de Finanzas."),
    ("¿Se gastó la reserva?", "Daniel",
     "No. La solicitud de COP 4,2 M de S2 nunca se activó porque la credencial llegó antes de los 10 días. "
     "El gasto cerró en 169,0 frente a 169,2."),
    ("¿Por qué S6-04 no está en Done si todo está entregado?", "Oscar",
     "Porque la DoD exige la validación del responsable de negocio, y el acta requiere la firma real tras la "
     "auditoría. Marcarla Done habría inflado la velocidad."),
    ("¿Los PR están aprobados?", "Oscar",
     "Están abiertos con el CI en verde y la revisión pedida a Daniel y Rafael. El autor no se aprueba a sí "
     "mismo, y no damos nada por integrado hasta el merge."),
    ("¿Qué cambió frente al Corte 1 y al Corte 2?", "Oscar",
     "Corte 1: PMBOK y Kanban, métricas de flujo. Corte 2: Scrum y XP, velocidad y DoD con pruebas. Corte 3: "
     "el mismo marco hasta el cierre, más la separación entre el Done técnico y la aceptación del negocio."),
    ("¿Qué pasa si el piloto se degrada?", "Rafael",
     "El monitoreo marca reentrenamiento tras dos semanas con caída > 0,05. El runbook asigna la decisión a la "
     "VP de Riesgo, con un plazo de 10 días hábiles."),
    ("¿Cómo protegen los datos personales?", "Daniel",
     "Muestra anonimizada desde S1, listas con clave SHA-256 con sal y la sal bajo custodia del oficial de "
     "protección de datos. Ese fue justamente el hallazgo de la auditoría."),
]


def build(m: dict, ev: dict, path: Path) -> Path:
    total = sum(sl[4] for sl in SLIDES if sl[0] != "preguntas")
    assert total <= TOTAL_MINUTES, f"Presentation runs {total} min, limit {TOTAL_MINUTES}"
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    blank = prs.slide_layouts[6]
    for number, (key, title, kicker, speaker, minutes, builder, notes) in enumerate(SLIDES, start=1):
        slide = prs.slides.add_slide(blank)
        if title:
            header(slide, title, kicker, number)
        builder(slide, m, ev)
        timing = f"{es(minutes)} min" if minutes else "respaldo"
        slide.notes_slide.notes_text_frame.text = f"[{speaker} · {timing}] {notes}"
    prs.core_properties.title = "Cierre del Programa de Analítica Predictiva · FinBank"
    prs.core_properties.author = "DataForge Consulting"
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)
    return path


def export_pdf(pptx: Path, pdf: Path) -> Path:
    """Export with PowerPoint (Windows COM) so the PDF matches the editable deck."""
    script = (
        "$ErrorActionPreference='Stop';"
        "$pp = New-Object -ComObject PowerPoint.Application;"
        f"$p = $pp.Presentations.Open('{pptx.resolve()}', -1, 0, 0);"
        f"$p.SaveAs('{pdf.resolve()}', 32);"
        "$p.Close(); $pp.Quit()"
    )
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], check=True,
                   capture_output=True, text=True)
    return pdf


def write_script(m: dict, path: Path) -> Path:
    total = sum(sl[4] for sl in SLIDES if sl[0] != "preguntas")
    lines = [
        "# Guion de sustentación · Corte 3",
        "",
        f"Duración: **{es(total)} min de presentación + {QA_MINUTES} min de preguntas**. La clase del "
        "6-nov-2026 anunció 30 + 5; hay que confirmar si la consigna publica otra duración. Generado por "
        "`scripts/build_corte3.py` desde la misma especificación que el PPTX: las notas del orador repiten este "
        "texto.",
        "",
        "| # | Diapositiva | Quién | Min | Acumulado |",
        "|---:|---|---|---:|---:|",
    ]
    acc = 0.0
    for i, (key, title, kicker, speaker, minutes, _builder, _notes) in enumerate(SLIDES, start=1):
        if minutes and key != "preguntas":
            acc += minutes
        name = title or ("Portada" if key == "portada" else "Preguntas")
        lines.append(f"| {i} | {name} | {speaker} | {es(minutes) if minutes else 'resp.'} | "
                     f"{es(acc) if minutes and key != 'preguntas' else ''} |")
    per = {}
    for sl in SLIDES:
        if sl[0] != "preguntas":
            per[sl[3]] = per.get(sl[3], 0) + sl[4]
    lines += ["", "Tiempo por integrante: " + ", ".join(f"{k} {es(v)} min" for k, v in per.items()) + ".", ""]
    lines += ["## Texto por diapositiva", ""]
    for i, (key, title, kicker, speaker, minutes, _builder, notes) in enumerate(SLIDES, start=1):
        name = title or ("Portada" if key == "portada" else "Preguntas")
        lines += [f"**{i}. {name}**, {speaker}, {es(minutes) + ' min' if minutes else 'respaldo'}", "", notes, ""]
    lines += ["## Demo y respaldo", "",
              "1. `pytest -q` (todas en verde). 2. `python scripts/run_pilot.py`. 3. Abrir "
              "`reports/pilot/early_warning_list.csv`. 4. `python scripts/run_monitoring.py`.",
              "",
              "Respaldo: la diapositiva 12 muestra la salida registrada del piloto, B2 la del monitoreo y "
              "`docs/corte3/evidence/` las ejecuciones completas. Antes de la sustentación, correr la demo una "
              "vez en el equipo que se va a usar.", "",
              "## Preguntas previsibles", "", "| Pregunta | Responde | Respuesta corta |", "|---|---|---|"]
    lines += [f"| {q} | {who} | {a} |" for q, who, a in QA]
    lines += ["", "## Reglas para la sustentación", "",
              "- No presentar actos simulados (Review, firma, Finanzas) como aceptaciones reales.",
              "- Decir «prototipo sobre datos sintéticos» cada vez que se cite AUC o recall.",
              "- Si alguien pregunta por la aprobación de los PR, mostrar su estado real en GitHub (B1).", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
