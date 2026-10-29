from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.utils import ImageReader
import math

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'The-Companion-Room-Concept-Brief.pdf'
W,H=792,612
GREEN=HexColor('#173e35'); CREAM=HexColor('#f5f2e9'); INK=HexColor('#20362f'); MUTED=HexColor('#67756a'); LINE=HexColor('#d8dace'); GOLD=HexColor('#b99b6b')
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('The Companion Room | East Lansing Pet Spa Concept')
c.setAuthor('Prepared for Mel Tucker / AVC')

def rect(x,y,w,h,fill,stroke=None):
    c.setFillColor(fill);c.setStrokeColor(stroke or fill);c.rect(x,y,w,h,fill=1,stroke=int(stroke is not None))
def text(s,x,y,size=11,font='Helvetica',color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,s)
def para(s,x,top,width,size=11,color=INK,leading=None,font='Helvetica'):
    p=Paragraph(s,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.55,textColor=color,spaceAfter=0))
    _,h=p.wrap(width,1000);p.drawOn(c,x,top-h);return top-h
def photo(path,x,y,w,h):
    image=ImageReader(str(path));iw,ih=image.getSize();scale=max(w/iw,h/ih);dw,dh=iw*scale,ih*scale
    c.saveState();p=c.beginPath();p.rect(x,y,w,h);c.clipPath(p,stroke=0,fill=0);c.drawImage(image,x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto');c.restoreState()
def base(number,kicker,title):
    rect(0,0,W,H,CREAM);text('THE COMPANION ROOM',42,H-31,8,'Helvetica-Bold',GREEN);text('EAST LANSING / CONCEPT STUDY',520,H-31,7,'Helvetica',MUTED)
    c.setStrokeColor(LINE);c.line(42,H-44,W-42,H-44)
    text(kicker,42,H-81,8,'Helvetica-Bold',MUTED);text(title,42,H-126,31,'Times-Roman',GREEN)
    text('Mel Tucker / AVC  |  October 29, 2026  |  Concept design',42,25,7,'Helvetica',MUTED);text(f'{number:02d} / 06',708,25,7,'Helvetica',MUTED)
def finish():c.showPage()
def bullet(s,x,top,width,size=10):
    text('•',x,top-10,size,'Helvetica',GOLD);return para(s,x+13,top,width-13,size,MUTED)-12

# 1 / Cover
rect(0,0,W,H,GREEN);photo(ROOT/'assets/spa-hero-v2.jpg',0,260,W,352)
rect(0,0,W,260,GREEN)
text('THE COMPANION ROOM',42,224,9,'Helvetica-Bold',HexColor('#c8d2bf'))
text('A better place for muddy paws.',42,176,36,'Times-Roman',CREAM)
para('A premium self-service pet spa concept for a proposed 300-500-unit building in downtown East Lansing. Resident use and essential supplies included.',43,149,680,12,HexColor('#d2dccb'))
for x,large,small in [(43,'2 + 1','INTEGRATED BAYS + PAW RINSE'),(298,'528 sq ft','ILLUSTRATIVE INTERIOR ENVELOPE'),(557,'Included','SELF-SERVICE RESIDENT AMENITY')]:
    text(large,x,74,25,'Times-Roman',CREAM);text(small,x,53,7,'Helvetica',HexColor('#becdb6'))
text('Prepared by Mel Tucker / AVC  |  Concept review  |  October 2026',43,22,7,'Helvetica',HexColor('#becdb6'))
text('Illustrative AI-generated concept artwork',520,279,7,'Helvetica',CREAM)
text('Open the interactive tour',620,22,8,'Helvetica',CREAM)
c.linkURL('https://meltckr.github.io/the-companion-room/',(616,15,755,35),relative=0)
finish()

# 2 / Layout
base(2,'01 / THE SPACE','One centralized spa, with room to adapt.')
photo(ROOT/'assets/room-overview.png',42,177,430,262)
text('24 ft x 22 ft  |  528 sq ft illustrative interior',51,158,9,'Helvetica',MUTED)
text('Shared layout intent across model and plan',51,140,8,'Helvetica',MUTED)
y=448
for s in ['<b>Two integrated bays:</b> washing, metered shampoo and powered drying in the same basin.','<b>Quick paw rinse:</b> near entry, separate from full baths.','<b>Finishing counter:</b> flat surface for towels and brushing; powered drying stays at each bay.','<b>Staff support:</b> locked cleaning storage, towel return and drain access.','<b>Expansion alcove:</b> preserve an option for a third bay.','<b>Optional retail niche:</b> compact take-home products; essentials stay included.']:
    y=bullet(s,500,y,245,10)
rect(42,63,708,54,HexColor('#e7ebde'))
para('Place the room near a conditioned return route from outdoor pet access. The project architect must establish the actual floorplate, equipment approach, clearances, wet-area design and building services. Equipment and animal-entry ramps are schematic; final access and service clearances remain open.',54,105,682,9,MUTED)
finish()

# 3 / Capacity
base(3,'02 / CAPACITY','Start with two bays. Test the third.')
para('No authoritative apartment-to-wash-bay ratio was identified. These scenarios make the assumptions visible; they are not measured resident demand.',42,455,670,11,MUTED)
data=[['Scenario','Apartments','Dog homes','Baths / month¹','Washes / month'],['Lower demand','300','15%','0.5','23'],['Working case','400','25%','1.0','100'],['Higher demand','500','35%','1.5','263']]
t=Table(data,colWidths=[145,105,115,120,173],rowHeights=[28,34,34,34])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),GREEN),('TEXTCOLOR',(0,0),(-1,0),CREAM),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),10),('TEXTCOLOR',(0,1),(-1,-1),INK),('LINEBELOW',(0,1),(-1,-1),.5,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),10)]));t.wrap(708,500);t.drawOn(c,42,266)
text('1. On-site baths per dog household each month. Shares and use frequency are assumptions.',43,249,8,'Helvetica',MUTED)
para('<b>Working operating assumptions</b><br/>45-minute occupied cycle including washing, drying and reset; 20 peak hours/week; 60% of washes during those hours; 90% equipment availability; 80% planning utilization ceiling. These choices are editable in the app.',42,219,320,10,MUTED)
para('<b>Stress case</b><br/>At 500 apartments, 35% dog households and 1.5 baths/month, concentrate 80% of washes into peak hours and reduce availability to 80%. Two bays reach about 113% effective peak utilization; three reduce that to about 76%. At a 60-minute cycle, the same stress case needs four bays at the chosen 80% ceiling.',414,219,336,10,MUTED)
para('Formula: monthly washes = units x dog-household share x monthly baths. Effective peak slots per bay = 4.345 x weekly peak hours x 60 / cycle minutes x availability. Recommended bays = peak washes / slots / chosen ceiling, rounded up, with a two-bay concept minimum.',42,107,708,8.5,MUTED)
para('Assumed 45-minute cycle: 15 wash + 20 dry + 10 arrival/reset. The model excludes quick-rinse traffic and does not predict queues or burst arrivals. Confirm pet policy and expected use; monitor booking delays after opening.',42,65,708,8.5,MUTED)
finish()

# 4 / Operations
base(4,'03 / THE RESIDENT EXPERIENCE','Keep the basics included. Plan for winter.')
photo(ROOT/'assets/spa-detail-v2.jpg',42,153,338,290)
para('Illustrative paw-rinse experience. Final equipment and access require professional design.',42,139,338,8,MUTED)
y=449
for s in ['<b>Included:</b> shampoo, waste bags and clean towels, with separate used-towel return.','<b>Winter:</b> warm rinse near the pet-return route, entry mats, snowmelt checks and drying before the lifts.','<b>Spring and fall:</b> mud and leaf capture, frequent strainer checks and wet-area cleanup.','<b>Summer:</b> conditioned indoor use, ventilation checks and water-temperature controls.','<b>Daily ownership:</b> designate staff for cleaning checks, laundry, supply replenishment and incident response.']:
    y=bullet(s,413,y,337,10)
rect(42,61,708,63,HexColor('#e7ebde'))
para('<b>Vending recommendation:</b> reserve a small built-in niche for optional brushes or take-home products. Confirm an operator, stocking, payment and service terms before purchase. A separate $3,000-$8,000 fit-out allowance is assumed; no supplier quote is in hand. Ordinary washing remains included.',54,113,682,9,MUTED)
finish()

# 5 / Investment
base(5,'04 / THE INVESTMENT','A preliminary budget to put in front of the team.')
data=[['Concept allowance (USD)','Low','High'],['Integrated wash/dry and rinse equipment','$30,000','$42,000'],['Plumbing, drainage and waterproofing','$20,000','$40,000'],['Finishes and partitions','$25,000','$45,000'],['Electrical, ventilation and acoustics','$10,000','$22,000'],['Cabinetry, storage and accessories','$8,000','$18,000'],['Design and commissioning','$8,000','$15,000'],['Subtotal','$101,000','$182,000'],['20% concept contingency','$20,200','$36,400'],['Total planning allowance','$121,200','$218,400']]
t=Table(data,colWidths=[269,85,85],rowHeights=[28]+[28]*9)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),GREEN),('TEXTCOLOR',(0,0),(-1,0),CREAM),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('LINEBELOW',(0,1),(-1,-1),.4,LINE),('BACKGROUND',(0,-1),(-1,-1),HexColor('#dce4d1')),('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),('ALIGN',(1,0),(-1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8)]));t.wrap(439,500);t.drawOn(c,42,162)
y=448
y=para('<b>Authored planning allowances</b><br/>No local contractor quotes have been obtained. The envelope is for a 528 sq ft two-bay concept within a new building.',512,y,238,10,MUTED)-18
y=para('<b>Current equipment reference [2]</b><br/>Evolution mini starts at $12,250 each. Two units start at $24,500 before options, freight, tax and installation. Allowance also reserves funds for paw rinse and accessories.',512,y,238,10,MUTED)-18
para('<b>Illustrative monthly operation</b><br/>Staff: 20 hours x $30 = $600.<br/>Supplies: $200. Laundry: $150.<br/>Utilities/service reserve: $150.<br/><b>Total: $1,100/month</b>, or $2.75 per apartment at 400 units. All operating inputs are assumptions.',512,y,238,10,MUTED)
para('Excluded: land, base-building shell, tax, financing, structural work, major service relocation, optional retail fit-out and the third bay. Architect/contractor to allocate permits, fire protection and shared building-system scope. No rent premium or return on investment is assumed.',42,128,708,9,MUTED)
para('Next cost action: obtain equipment proposals and a local cost plan with a documented scope split between the amenity and base building.',42,73,708,9,MUTED)
finish()

# 6 / References and status
base(6,'05 / REFERENCES & NEXT DECISIONS','Take the concept into design development.')
sources=[
('1. All Paws TUB-Amenity - alternate','https://allpawspetwash.com/apw-option-c.html','Free-use controls, dryer and hair straining. No quantified capture or drying-time promise is adopted.'),
('2. Evolution mini - current reference configuration','https://evolutiondogwash.com/models-and-pricing/models/mini-series/','Starts at $12,250. Integrated dryer, metered products and microbubble technology; supplier products are required under warranty terms.'),
('3. Evolution mini - March 2024 owner manual, Rev. 4.1','https://evolutiondogwash.com/wp-content/uploads/2024/03/mini-Owners-Manual-final-March-2024-R-4.1-.pdf','Documents factory Free Mode and a suggested 7 x 7 ft operating space. Current model dimensions, connections and access need supplier confirmation.'),
('4. iClean manufacturer catalog - XL alternative','https://icleandogwash.com/gfx/pdf/iClean_Dog_Wash_Catalog.pdf','Published XL overall footprint: 93.5 x 27.5 x 78.7 inches. Basin size is smaller. Confirm complete variant, ramp and service space.'),
('5. City of East Lansing - snow removal','https://www.cityofeastlansing.com/1013/Snow-Removal','Local snow/ice-management context for the proposed winter entry sequence.'),
('6. U.S. Access Board - clear floor and turning space','https://www.access-board.gov/ada/guides/chapter-3-clear-floor-or-ground-space-and-turning-space/','General accessibility reference. Architect must determine applicable scoping and complete design.')]
y=454
for title,url,claim in sources:
    y=para(f'<link href="{url}" color="#173e35"><b>{title}</b></link><br/>{claim}',42,y,447,9,MUTED)-14
rect(523,135,227,312,HexColor('#e7ebde'))
text('BEFORE A BUILD DECISION',538,425,8,'Helvetica-Bold',GREEN)
y=405
for s in ['Confirm the actual floorplate and pet-entry route.','Approve integrated equipment, free-use setup, controls, access and service clearances.','Engineer drainage, waterproofing, hot water, ventilation and noise control.','Set staff ownership, hours, booking policy and pet rules.','Obtain local construction and operating quotations.']:
    y=bullet(s,536,y,200,9)
para('Status: conceptual design study. Building facts are supplied by the user and remain unverified. The property has no supplied floor plan. Perspective artwork is illustrative AI imagery. Blender 360 views derive from the room model; the WebGL model supports layout exploration. All dimensions, bay counts, operating assumptions and unquoted costs require confirmation. Research checked October 29, 2026.',42,104,708,8.5,MUTED)
text('Prepared for discussion. Professional architectural and engineering design is required before construction.',42,47,8,'Helvetica',GREEN)
finish();c.save();print(OUT)
