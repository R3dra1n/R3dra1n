#!/usr/bin/env python3
"""Update desktop and mobile, light and dark contribution animations."""
from pathlib import Path
import math
import re
import generate_snake

p = Path(__file__).resolve().parent.parent / 'assets'
generate_snake.main()
desktop = p / 'contributions-snake.svg'
s = desktop.read_text(encoding='utf-8')
s = s.replace('#f8f7f1', '#f8f4e9').replace('#729e8b', '#d5a0a5').replace('#477b6d', '#b96e82')
s = s.replace('</svg>', '<g fill="#dba2af"><rect x="1006" y="42" width="4" height="4"/><rect x="1020" y="49" width="4" height="4"/><rect x="1030" y="38" width="4" height="4"/></g></svg>')
desktop.write_text(s, encoding='utf-8')
raw=(p/'contributions-snake.svg').read_text(); matches=list(re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="13" height="13" rx="3" fill="([^\"]+)"><title>(\d{4}-\d\d-\d\d): (\d+) contributions</title>',raw));assert len(matches)>=360
cells=[]
for m in matches:
 x,y,col,date_,count=m.groups();colno=round((float(x)-56)/18.4);row=round((float(y)-133)/19);cells.append((colno,row,int(count),date_,col))
W=800;stride=23;padx=69; rowys=[110+i*18+(75 if i>=7 else 0) for i in range(14)];duration=50;horizontal=26*stride;total=14*horizontal+sum(rowys[i+1]-rowys[i] for i in range(13));parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 520" role="img" aria-labelledby="title desc">','<title id="title">A year of GitHub contributions in two rows</title>','<desc id="desc">A snake grows as it visits contribution days; squares reappear after it passes.</desc>','<rect width="800" height="520" fill="#f8f4e9"/>','<text x="50" y="42" font-family="Georgia,serif" font-size="27" fill="#294d60">A year of small steps</text>','<text x="50" y="67" font-family="Arial,sans-serif" font-size="15" fill="#72949b">CONTRIBUTION TIDES</text>','<text x="69" y="93" font-family="Arial,sans-serif" font-size="14" fill="#6d8a90">FIRST HALF</text>','<text x="69" y="315" font-family="Arial,sans-serif" font-size="14" fill="#6d8a90">SECOND HALF</text>']
# first panel row y=110..218, second panel row y=311..419 (spacing leaves room for label)
rowys=[110+i*18+(75 if i>=7 else 0) for i in range(14)]
parts=[x.replace('y="315"','y="295"') for x in parts]
total=14*horizontal+sum(rowys[i+1]-rowys[i] for i in range(13));food=[]
for week,row,count,date_,color in cells:
 panel=week//27;col=week%27;r=panel*7+row;y=rowys[r];x=padx+col*stride
 anim=''
 if count:
  distance=r*horizontal+sum(rowys[i+1]-rowys[i] for i in range(r))+(col if r%2==0 else 26-col)*stride;t=distance/total;food.append(t);before=max(.001,min(.994,t-.001));after=min(.996,max(before+.001,t+.001));rs=min(.998,max(after+.0004,t+.055));rf=min(.9995,max(rs+.0004,t+.075));anim=f'<animate attributeName="opacity" values="1;1;0.18;0.18;1;1" keyTimes="0;{before:.4f};{after:.4f};{rs:.4f};{rf:.4f};1" dur="50s" repeatCount="indefinite"/>'
 parts.append(f'<rect x="{x}" y="{y}" width="16" height="16" rx="3" fill="{color}"><title>{date_}: {count} contributions</title>{anim}</rect>')
x0=padx+8;x1=padx+26*stride+8;path=f'M {x0} {rowys[0]+8}'
for r in range(14):
 x=x1 if r%2==0 else x0;path+=f' L {x} {rowys[r]+8}'
 if r<13:path+=f' L {x} {rowys[r+1]+8}'
food.sort()
for i in reversed(range(1,3+len(food))):
 growth=0 if i<=2 else food[i-3];visible=min(.999,max(.001,max(growth,i*.095/50)));before=max(0,visible-.0005);delay=(50-i*.095)%50;parts.append(f'<g opacity="0"><circle r="7" fill="#d5a0a5" stroke="#f8f4e9" stroke-width="1"/><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{before:.5f};{visible:.5f};1" dur="50s" repeatCount="indefinite"/><animateMotion path="{path}" dur="50s" begin="-{delay:.4f}s" repeatCount="indefinite"/></g>')
parts.append(f'<g><circle r="8" fill="#b96e82" stroke="#f8f4e9" stroke-width="1"/><circle cx="-2" cy="-2" r="1" fill="white"/><circle cx="2" cy="-2" r="1" fill="white"/><animateMotion path="{path}" dur="50s" repeatCount="indefinite"/></g>');parts.append('<text x="69" y="490" font-family="Arial,sans-serif" font-size="14" fill="#779096">Each square represents one day · The snake grows and starts again</text></svg>')
(p/'contributions-mobile.svg').write_text('\n'.join(parts));print(f'Mobile calendar: {len(cells)} real days, {len(food)} contribution days')

# Light and dark charts are generated from the same snapshot.
svgcolors={'#f8f4e9':'#17272e','#294d60':'#dbe9df','#72949b':'#a1beb3','#c2dad5':'#426a65','#6d8a90':'#9abbb1','#779096':'#92ada5','#e2ece9':'#304949','#c3ddd8':'#4e7770','#93c4bf':'#72a99c','#619c9f':'#92caba','#3d718b':'#b2d9cf','#d5a0a5':'#e6aabb','#b96e82':'#df8fa5'}
for name in ['contributions-snake.svg','contributions-mobile.svg']:
    text=(p/name).read_text(encoding='utf-8')
    for light,dark in svgcolors.items():
        text=text.replace(light,dark)
    (p/name.replace('.svg','-dark.svg')).write_text(text,encoding='utf-8')

def inner(name):
    text=(p/name).read_text(encoding='utf-8')
    text=text[text.index('>')+1:text.rindex('</svg>')]
    return text.replace('<title id="title">A year of GitHub contributions in two rows</title>','').replace('<desc id="desc">A snake grows as it visits contribution days; squares reappear after it passes.</desc>','')
style='<style>.night{display:none}@media (prefers-color-scheme:dark){.night{display:inline}.day{display:none}}</style>'
wrapper='<svg xmlns="http://www.w3.org/2000/svg" width="800" height="520" viewBox="0 0 800 520" role="img"><title>Animated contribution calendar</title>'+style+'<g class="day">'+inner('contributions-mobile.svg')+'</g><g class="night">'+inner('contributions-mobile-dark.svg')+'</g></svg>'
(p/'contributions-mobile-adaptive.svg').write_text(wrapper,encoding='utf-8')
