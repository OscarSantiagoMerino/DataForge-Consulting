"""Build the four-page executive report from the versioned JSON source."""
from pathlib import Path
import argparse
import csv
import json
import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

ROOT = Path(__file__).resolve().parents[1]
W, H = A4
M = 42
CW = W - 2*M
NAVY, TEAL, INK, MUTED, PALE, LINE = map(colors.HexColor, ['#14344A','#087F8C','#213747','#587080','#F0F5F7','#D3E0E6'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/report/Reporte_Sprints_Corte2.pdf')
    args = parser.parse_args()
    source = json.loads((ROOT/'docs/report/report_content.json').read_text(encoding='utf-8'))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    system = Path('C:/Windows/Fonts')
    bundled = Path(reportlab.__file__).parent/'fonts'
    regular = system/'segoeui.ttf' if (system/'segoeui.ttf').exists() else bundled/'Vera.ttf'
    bold = system/'segoeuib.ttf' if (system/'segoeuib.ttf').exists() else bundled/'VeraBd.ttf'
    pdfmetrics.registerFont(TTFont('Body', str(regular)))
    pdfmetrics.registerFont(TTFont('BodyBold', str(bold)))
    pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold', italic='Body', boldItalic='BodyBold')
    styles = {name:ParagraphStyle(name, fontName='Body', fontSize=size, leading=lead, textColor=color) for name,size,lead,color in [('body',9.7,13.2,INK),('small',8.4,11,MUTED),('table',9,11.5,INK),('compact',8.6,10.8,INK),('head',9.1,11.5,colors.white)]}
    c = canvas.Canvas(str(args.output), pagesize=A4)
    c.setTitle('FinBank - Reporte de Sprints del Corte 2')
    c.setAuthor('DataForge Consulting - Daniel Martínez, Rafael Baracaldo y Oscar Merino')
    c.setSubject('Cierre S1/S2 del caso académico e incremento integrado por PR #8; 16 de octubre de 2026')

    def para(text, x, y, width=CW, style='body'):
        item=Paragraph(text, styles[style]); _,height=item.wrap(width,1000)
        item.drawOn(c,x,y-height)
        return y-height

    def table(block, y):
        style='compact' if block.get('compact') else 'table'
        rows=[[Paragraph('<b>'+str(x)+'</b>',styles['head']) for x in block['headers']]]
        rows += [[Paragraph(str(x),styles[style]) for x in row] for row in block['rows']]
        item=Table(rows,colWidths=[CW*x for x in block['widths']])
        pad=5 if block.get('compact') else 7
        item.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad),('LINEBELOW',(0,0),(-1,-1),.4,LINE)]))
        _,height=item.wrap(CW,1000); item.drawOn(c,M,y-height)
        return y-height-12

    def chart(x,y,width,values,title):
        c.setFillColor(NAVY);c.setFont('BodyBold',10);c.drawString(x,y,title)
        px=x+24;py=y-126;pw=width-32;ph=101
        for tick in (0,5,10,15,20):
            yy=py+ph*tick/20;c.setStrokeColor(LINE);c.setLineWidth(.4);c.line(px,yy,px+pw,yy)
            c.setFont('Body',7.5);c.setFillColor(MUTED);c.drawRightString(px-5,yy-2,str(tick))
        for day in (0,2,4,6,8,10):
            c.drawCentredString(px+pw*day/10,py-11,str(day))
        c.drawRightString(px+pw,py-22,'Día hábil')
        c.setDash(3,3);c.setStrokeColor(MUTED);c.setLineWidth(.9)
        c.line(px,py+ph*values[0]/20,px+pw,py);c.setDash()
        c.setStrokeColor(TEAL);c.setLineWidth(1.7)
        for day in range(10):
            x1=px+pw*day/10;x2=px+pw*(day+1)/10;y1=py+ph*values[day]/20;y2=py+ph*values[day+1]/20
            c.line(x1,y1,x2,y1);c.line(x2,y1,x2,y2)
        c.setFillColor(TEAL)
        for day,value in enumerate(values):c.circle(px+pw*day/10,py+ph*value/20,1.4,fill=1,stroke=0)

    for number,page in enumerate(source['pages'],1):
        c.setFillColor(NAVY);c.rect(0,H-18,W,18,fill=1,stroke=0)
        c.setFillColor(TEAL);c.setFont('BodyBold',9);c.drawString(M,H-43,'DATAFORGE CONSULTING / FINBANK S.A.')
        c.setFillColor(NAVY);c.setFont('BodyBold',23);c.drawString(M,H-77,page['title'])
        y=para(page['subtitle'],M,H-91,style='small')-19
        c.setStrokeColor(LINE);c.line(M,40,W-M,40)
        c.setFont('Body',8);c.setFillColor(MUTED);c.drawString(M,27,'GMAC-FB-2026-01 | Corte 2 | '+source['updated']);c.drawRightString(W-M,27,f'{number} / 4')
        for block in page['blocks']:
            kind=block['type']
            if kind in ('paragraph','small'):
                y=para(block['text'],M,y,style='small' if kind=='small' else 'body')-12
            elif kind=='section':
                c.setFillColor(NAVY);c.setFont('BodyBold',13);c.drawString(M,y,block['text']);y-=21
            elif kind=='box':
                item=Paragraph(block['text'],styles['body']);_,height=item.wrap(CW-22,1000)
                c.setFillColor(PALE);c.roundRect(M,y-height-20,CW,height+20,6,fill=1,stroke=0)
                item.drawOn(c,M+11,y-height-10);y-=height+32
            elif kind=='table':y=table(block,y)
            elif kind=='metrics':
                gap=10;width=(CW-2*gap)/3
                for i,(value,label,detail) in enumerate(block['items']):
                    x=M+i*(width+gap);c.setFillColor(PALE);c.roundRect(x,y-65,width,65,6,fill=1,stroke=0)
                    c.setFillColor(TEAL);c.setFont('BodyBold',22);c.drawString(x+10,y-25,value)
                    para('<b>'+label+'</b>',x+10,y-33,width-20,'table');para(detail,x+10,y-49,width-20,'small')
                y-=80
            elif kind=='charts':
                width=(CW-20)/2;chart(M,y,width,block['s1'],'Sprint 1: 16 a 0');chart(M+width+20,y,width,block['s2'],'Sprint 2: 20 a 5');y-=162
            else:raise ValueError(kind)
            if y<49:raise ValueError(f'Contenido fuera de página {number}: y={y:.1f}')
        print(f'Page {number}: bottom {y:.1f}')
        c.showPage()
    c.save()
    with (ROOT/'docs/evidence/sprint_burndown.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.writer(handle);writer.writerow(['sprint','day','remaining_points','ideal_points','closed_items'])
        for sprint,values,closures in [('S1',[16,16,16,13,13,8,8,5,5,5,0],{3:'US-04',5:'US-03',7:'US-01',10:'US-02'}),('S2',[20,20,20,18,18,15,15,15,8,8,5],{3:'T-05.0',5:'T-05.6',8:'T-05.1|T-05.4',10:'T-05.2'})]:
            for day,value in enumerate(values):writer.writerow([sprint,day,value,round(values[0]*(1-day/10),1),closures.get(day,'')])
    print(args.output)


if __name__=='__main__':main()
