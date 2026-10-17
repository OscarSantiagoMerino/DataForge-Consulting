"""Build the timed PDF and Markdown speech from review_content.json."""
from pathlib import Path
import json
import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/review'
W,H=A4; M=44; CW=W-2*M
NAVY=colors.HexColor('#14344A'); TEAL=colors.HexColor('#087F8C'); PALE=colors.HexColor('#F0F5F7'); MUTED=colors.HexColor('#587080')


def main():
    data=json.loads((OUT/'review_content.json').read_text(encoding='utf-8'))
    assert len(data)==15 and sum(row['secs'] for row in data)==900
    windows=Path('C:/Windows/Fonts'); bundled=Path(reportlab.__file__).parent/'fonts'
    pdfmetrics.registerFont(TTFont('S',str(windows/'segoeui.ttf' if (windows/'segoeui.ttf').exists() else bundled/'Vera.ttf')))
    pdfmetrics.registerFont(TTFont('SB',str(windows/'segoeuib.ttf' if (windows/'segoeuib.ttf').exists() else bundled/'VeraBd.ttf')))
    pdfmetrics.registerFontFamily('S',normal='S',bold='SB',italic='S',boldItalic='SB')
    styles={name:ParagraphStyle(name,fontName=font,fontSize=size,leading=lead,textColor=color) for name,font,size,lead,color in [('body','S',10.8,14.5,NAVY),('small','S',9.2,12,MUTED),('title','SB',14,18,NAVY)]}
    c=canvas.Canvas(str(OUT/'Speech_FinBank_Corte2.pdf'),pagesize=A4)
    c.setTitle('FinBank - Guion de la Sprint Review del Corte 2')
    c.setAuthor('DataForge Consulting - Daniel Martínez, Rafael Baracaldo y Oscar Merino')
    c.setSubject('Quince minutos; versión del 16 de octubre de 2026, alineada al PR #8')
    def p(text,y,style='body',x=M,width=CW):
        item=Paragraph(text,styles[style]);_,height=item.wrap(width,1000);item.drawOn(c,x,y-height);return y-height
    def time(seconds):return f'{seconds//60:02d}:{seconds%60:02d}'
    elapsed=0
    md=['# Guion de la Sprint Review del Corte 2','','Actualización: 16 de octubre de 2026. Duración prevista: 15:00, incluidos 150 s de demo y 60 s de preguntas.','','Daniel: Project Leader; Rafael: Business Analyst y PO; Oscar: Scrum Facilitator y SM. Los tres participan como Developers.','']
    for page in range(5):
        c.setFillColor(NAVY);c.rect(0,H-18,W,18,fill=1,stroke=0)
        c.setFillColor(TEAL);c.setFont('SB',9);c.drawString(M,H-43,'DATAFORGE CONSULTING / FINBANK S.A.')
        c.setFillColor(NAVY);c.setFont('SB',22);c.drawString(M,H-77,'Guion de la Sprint Review')
        y=p('16 de octubre de 2026 | 15 diapositivas | Preparación de sustentación',H-92,'small')-20
        if page==0:y=p('Los tiempos incluyen explicación visual, cambios de pantalla y la demostración. El equipo comprobará la duración mediante ensayo conjunto.',y,'small')-17
        for row in data[page*3:page*3+3]:
            start,end=elapsed,elapsed+row['secs'];elapsed=end
            timing=f'{time(start)}-{time(end)} | {row["secs"]} s | {row["who"]}'
            c.setFillColor(TEAL);c.setFont('SB',9);c.drawString(M,y,timing);y-=11
            y=p(f'{row["n"]:02d}. {row["title"]}',y,'title')-9
            y=p(row['speech'],y)-8
            action=Paragraph('<b>En escena.</b> '+row['action'],styles['small']);_,height=action.wrap(CW-20,1000)
            c.setFillColor(PALE);c.roundRect(M,y-height-16,CW,height+16,5,fill=1,stroke=0);action.drawOn(c,M+10,y-height-8);y-=height+32
            md += [f'## {row["n"]:02d} {row["title"]}',timing,'',row['speech'],'','**En escena:** '+row['action'],'']
        if y<50:raise ValueError(f'Página {page+1} excedida: {y}')
        c.setStrokeColor(colors.HexColor('#D3E0E6'));c.line(M,40,W-M,40)
        c.setFillColor(MUTED);c.setFont('S',8);c.drawString(M,27,'GMAC-FB-2026-01 | Guion para ensayo | 15:00 minutos');c.drawRightString(W-M,27,f'{page+1} / 5')
        print(f'Speech page {page+1}: bottom {y:.1f}')
        c.showPage()
    c.save()
    (OUT/'Speech_editable.md').write_text('\n'.join(md).rstrip()+'\n',encoding='utf-8')


if __name__=='__main__':main()
