"""Build the coordinated concept brief, one-page decision brief and pricing scope."""
from pathlib import Path
import re,html
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle,SimpleDocTemplate,Spacer,KeepTogether
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
ROOT=Path(__file__).resolve().parent.parent
W,H=792,612
GREEN=HexColor('#173e35');CREAM=HexColor('#f5f2e9');INK=HexColor('#20362f');MUTED=HexColor('#67756a');LINE=HexColor('#d8dace');GOLD=HexColor('#b99b6b')
URL='https://meltckr.github.io/the-companion-room/?v=4'
class Brief:
 def __init__(self,name,total):
  self.c=canvas.Canvas(str(ROOT/name),pagesize=(W,H),pageCompression=1);self.total=total
  self.c.setTitle('The Companion Room | '+name.replace('.pdf','').replace('-',' '));self.c.setAuthor('Mel Tucker / AVC')
 def rect(self,x,y,w,h,color):self.c.setFillColor(color);self.c.rect(x,y,w,h,fill=1,stroke=0)
 def text(self,s,x,y,size=11,font='Helvetica',color=INK):self.c.setFillColor(color);self.c.setFont(font,size);self.c.drawString(x,y,s)
 def para(self,s,x,top,width,size=10,color=MUTED,leading=None):
  p=Paragraph(s,ParagraphStyle('p',fontName='Helvetica',fontSize=size,leading=leading or size*1.5,textColor=color));_,h=p.wrap(width,1000);p.drawOn(self.c,x,top-h);return top-h
 def photo(self,path,x,y,w,h):
  image=ImageReader(str(ROOT/path));iw,ih=image.getSize();scale=max(w/iw,h/ih);dw,dh=iw*scale,ih*scale
  self.c.saveState();p=self.c.beginPath();p.rect(x,y,w,h);self.c.clipPath(p,stroke=0,fill=0);self.c.drawImage(image,x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto');self.c.restoreState()
 def base(self,n,kicker,title):
  self.rect(0,0,W,H,CREAM);self.text('THE COMPANION ROOM',42,581,8,'Helvetica-Bold',GREEN);self.text('EAST LANSING / CONCEPT 03',530,581,7,'Helvetica',MUTED)
  self.c.setStrokeColor(LINE);self.c.line(42,568,750,568);self.text(kicker,42,531,8,'Helvetica-Bold',MUTED);self.text(title,42,486,30,'Times-Roman',GREEN)
  self.text('Mel Tucker / AVC | October 29, 2026 | Concept design',42,25,7,'Helvetica',MUTED);self.text(f'{n:02d} / {self.total:02d}',708,25,7,'Helvetica',MUTED)
 def table(self,data,x,y,widths,rowsize=29):
  t=Table(data,colWidths=widths,rowHeights=[rowsize]*len(data));t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),GREEN),('TEXTCOLOR',(0,0),(-1,0),CREAM),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('LINEBELOW',(0,1),(-1,-1),.4,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),9)]));t.wrap(sum(widths),500);t.drawOn(self.c,x,y)
 def link(self,label,x,y,url=URL):self.text(label,x,y,9,'Helvetica',GREEN);self.c.linkURL(url,(x,y-4,x+len(label)*5,y+12),relative=0)
 def page(self):self.c.showPage()
 def save(self):self.c.save()
def decision(d,n=1):
 d.base(n,'THE DEVELOPER DECISION','Two bays at opening. A plan for what follows.')
 d.para('A proposed amenity for one 300-500-unit East Lansing building, mostly studios, serving students and young professionals. The building floorplate and actual pet demand remain to be established.',42,455,708,11)
 d.photo(Path('assets/master-v4/hero.jpg'),42,178,360,225);y=407
 for title,body in [('Opening program','Two integrated wash/dry bays plus a separate low paw rinse. Resident use, compatible shampoo and towels included.'),('Preferred placement','Near a conditioned return route from outdoor pet access. Provide locked service storage and a separate finishing counter.'),('Space decision','Compact: 20 x 18 ft / 360 sq ft. Premium: 24 x 22 ft / 528 sq ft, with a reserved third-bay option.')]:
  d.text(title,429,y,12,'Helvetica-Bold',GREEN);y=d.para(body,429,y-13,321,10)-21
 d.rect(42,76,708,74,HexColor('#e5eadc'))
 d.para('<b>Equipment basis:</b> two Evolution mini units start at a published $24,500 before options, freight, tax and installation. <b>Construction:</b> quote required for both room options. The premium $120k-$220k total is an authored planning allowance, pending local validation.',55,137,680,10)
 d.link('Explore the room and compare both plans',42,52)
main=Brief('The-Companion-Room-Concept-Brief.pdf',6)
main.rect(0,0,W,H,GREEN);main.photo(Path('assets/master-v4/hero.jpg'),0,260,W,352);main.rect(0,0,W,260,GREEN)
main.text('THE COMPANION ROOM',42,224,9,'Helvetica-Bold',HexColor('#c8d2bf'));main.text('A better place for muddy paws.',42,176,36,'Times-Roman',CREAM)
main.para('A considered resident pet spa for downtown East Lansing. Integrated washing and drying, essential supplies included, and two room footprints to evaluate.',43,149,680,12,HexColor('#d2dccb'))
for x,big,small in [(43,'2 + 1','INTEGRATED BAYS + PAW RINSE'),(298,'360 / 528','TWO CONCEPTUAL ROOM AREAS, SQ FT'),(557,'Included','SELF-SERVICE RESIDENT AMENITY')]:main.text(big,x,74,25,'Times-Roman',CREAM);main.text(small,x,53,7,'Helvetica',HexColor('#becdb6'))
main.text('Mel Tucker / AVC | Concept 03 | October 2026',43,22,7,'Helvetica',HexColor('#becdb6'));main.text('Open the room tour',646,22,8,'Helvetica',CREAM);main.c.linkURL(URL,(640,15,755,35),relative=0);main.page()
decision(main,2);main.page()
main.base(3,'01 / THE SPACE TRADEOFF','Two footprints. The same essential service.')
main.table([['','Compact','Premium + expansion'],['Illustrative envelope','20 x 18 ft','24 x 22 ft'],['Interior area','360 sq ft','528 sq ft'],['Opening program','2 wash/dry + 1 rinse','2 wash/dry + 1 rinse'],['Finishing counter','Compact','Separate counter'],['Reserved third bay','No reserved alcove','Space reserved'],['Retail niche','Omit or locate elsewhere','Optional built-in niche'],['Construction price','Quotation required','Quotation required']],42,187,[210,249,249],30)
main.para('The compact option saves 168 square feet. Both are schematic fit studies. Equipment operation, accessibility, service panels and final circulation require review against the actual building and current supplier submittals. The rendered tour shows the premium room.',42,158,708,11)
main.para('<b>Recommendation:</b> reserve the premium envelope if the floorplate supports it and expansion flexibility has value. Use the compact program where space is constrained, with a separate plan for higher demand.',42,96,708,10);main.page()
main.base(4,'02 / THE ROUTINE & CAPACITY','Keep the full wash-and-dry routine in one bay.')
main.photo(Path('assets/master-v4/closeup.jpg'),42,208,340,235)
main.para('All current stills, tour views and browser geometry derive from the same detailed master scene. Equipment remains a generic reference concept.',42,195,340,8)
main.para('<b>Included:</b> compatible shampoo, clean towels and used-towel return, waste bags, hooks and a phone shelf. Staff own checks, restocking and equipment service.<br/><br/><b>Four seasons:</b> paw rinsing and entry cleanup after snow or mud; conditioned indoor washing, ventilation and towel turnover through the year.<br/><br/><b>Optional:</b> a compact retail niche for brushes or take-home products. Supplier/service terms and fit-out are separate.',414,443,336,10)
main.rect(42,65,708,91,HexColor('#e5eadc'))
main.para('<b>Capacity:</b> two bays are the opening concept. At 400 apartments, 25% dog households and one bath/month, a 45-minute cycle models 100 washes/month. A concentrated 500-unit higher-demand case calls for three bays; the same case with 60-minute occupancy calls for four at the chosen 80% utilization ceiling. All inputs are assumptions. Quick-rinse traffic and queue behavior are excluded.',54,144,684,10);main.page()
main.base(5,'03 / THE COST EVIDENCE','Separate published prices from the room allowance.')
main.text('$24,500',42,414,42,'Times-Roman',GREEN);main.para('Published starting price for two Evolution mini integrated units, checked October 29, 2026. Options, freight, tax, installation, paw rinse and room construction are additional.',42,391,330,11)
main.para('<b>Supplier comparison</b><br/>Groomer\'s Best lists two component tubs at $6,492 total; separate drying, dispensing and plumbing prevent a like-for-like comparison. APW and iClean alternatives require current quotations.<br/><br/><b>Construction evidence</b><br/>A local contractor quotation has not been obtained. Compact construction stays unpriced. Compare complete bids using the same base-building assumptions.',414,445,336,10)
main.table([['Premium allowance snapshot','Low','High'],['Subtotal','$101,000','$182,000'],['20% concept contingency','$20,200','$36,400'],['Total authored allowance','$121,200','$218,400']],42,176,[420,144,144],30)
main.para('The premium total includes the equipment allowance and overlaps the published equipment pair price; do not add them together. Excludes land, shell, tax, financing, structural work, major service relocation, third unit and retail fit-out. Reconcile permits, shared MEP and future provisions in bids.',42,149,708,9)
main.link('Download the prepared supplier and construction pricing scope',42,68,'https://meltckr.github.io/the-companion-room/Procurement-Scope.pdf');main.page()
main.base(6,'04 / SOURCES & NEXT DECISIONS','Bring the concept to the project team.')
sources=[('Evolution mini - current price and included functions','https://evolutiondogwash.com/models-and-pricing/models/mini-series/','Reference integrated equipment; supplier products affect warranty.'),('Evolution mini - linked March 2024 manual','https://evolutiondogwash.com/wp-content/uploads/2024/03/mini-Owners-Manual-final-March-2024-R-4.1-.pdf','Free Mode and 7 x 7 ft operating footprint. Obtain current submittals and connection details.'),("Groomer's Best - component tub benchmark",'https://www.groomersbest.com/product/ada-walk-through-bathing-tub/','Published component price; not the full integrated scope.'),('All Paws TUB-Amenity','https://allpawspetwash.com/apw-option-c.html','Free resident-use alternative; quotation required.'),('iClean XL - manufacturer catalog','https://icleandogwash.com/gfx/pdf/iClean_Dog_Wash_Catalog.pdf','Larger integrated alternative; confirm complete footprint and US support.'),('East Lansing - Building Information','https://www.cityofeastlansing.com/648/Building-Information','Building and trade-permit pathways; project team establishes applicable submissions.')]
y=455
for title,url,body in sources:y=main.para(f'<link href="{url}" color="#173e35"><b>{title}</b></link><br/>{body}',42,y,439,9)-14
main.rect(520,142,230,307,HexColor('#e5eadc'));main.text('RESOLVE BEFORE COMMITMENT',535,426,8,'Helvetica-Bold',GREEN);y=405
for text in ['Confirm the actual floorplate and pet-return route.','Approve equipment, free-use setup, access and service clearances.','Coordinate water, drainage, ventilation, acoustics and electrical work.','Set staff ownership, supplies, laundry and booking policy.','Compare complete supplier and local construction quotations.']:
 main.text('•',535,y-9,10,'Helvetica',GOLD);y=main.para(text,549,y,185,9)-16
main.para('Concept 03 is prepared for discussion. Building facts are supplied by the user. No surveyed floorplate, approved equipment submittal or local contractor quote has been supplied. Visuals share one master scene and remain conceptual. Professional architectural and engineering design is required before construction. Research checked October 29, 2026.',42,101,708,8.5)
main.page();main.save()
one=Brief('Developer-Decision-Brief.pdf',1);decision(one);one.page();one.save()
def inline(value):
 value=html.escape(value);value=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#173e35">\1</link>',value)
 return re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',value)
styles={'title':ParagraphStyle('title',fontName='Times-Roman',fontSize=27,leading=31,textColor=GREEN,spaceAfter=17),'h':ParagraphStyle('h',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=GREEN,spaceBefore=16,spaceAfter=7),'p':ParagraphStyle('p',fontName='Helvetica',fontSize=9.5,leading=14,textColor=INK,spaceAfter=9),'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=8.2,leading=11,textColor=INK)}
story=[];lines=(ROOT/'PROCUREMENT-BRIEF.md').read_text().splitlines();i=0
while i<len(lines):
 line=lines[i].strip()
 if not line:i+=1;continue
 if line.startswith('|'):
  data=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   row=lines[i].strip();i+=1
   if re.fullmatch(r'[|\s:\-]+',row):continue
   data.append([Paragraph(inline(cell.strip()),styles['cell']) for cell in row.strip('|').split('|')])
  t=Table(data,colWidths=[65,126,190,147],repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e5eadc')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),.5,LINE),('INNERGRID',(0,0),(-1,-1),.4,LINE),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));story.extend([t,Spacer(1,13)]);continue
 if line.startswith('# '):story.append(Paragraph('The Companion Room',styles['title']));story.append(Paragraph('Supplier and construction pricing scope',styles['h']));i+=1;continue
 if line.startswith('## '):story.append(Paragraph(inline(line[3:]),styles['h']));i+=1;continue
 paragraph=[line];i+=1
 while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')):paragraph.append(lines[i].strip());i+=1
 story.append(KeepTogether([Paragraph(inline(' '.join(paragraph)),styles['p'])]))
def procurement_page(c,doc):
 c.setFillColor(GREEN);c.setFont('Helvetica-Bold',8);c.drawString(42,766,'THE COMPANION ROOM / AVC');c.setFillColor(MUTED);c.setFont('Helvetica',7);c.drawString(42,25,'Draft pricing scope | Prepared October 29, 2026 | Not issued');c.drawRightString(570,25,str(doc.page))
doc=SimpleDocTemplate(str(ROOT/'Procurement-Scope.pdf'),pagesize=letter,rightMargin=42,leftMargin=42,topMargin=52,bottomMargin=45,title='The Companion Room | Supplier and Construction Pricing Scope',author='Mel Tucker / AVC')
doc.build(story,onFirstPage=procurement_page,onLaterPages=procurement_page)
print('Updated concept brief, one-page decision brief and procurement scope PDFs.')
