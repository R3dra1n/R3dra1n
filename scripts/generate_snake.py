#!/usr/bin/env python3
"""Render a coastal contribution calendar from GitHub's actual daily data."""
from datetime import date
import html
import json
import math
import os
from pathlib import Path
from urllib.request import Request, urlopen

QUERY='''query($login: String!) { user(login:$login) { contributionsCollection {
 contributionCalendar { weeks { contributionDays { date contributionCount } } }
} } }'''

def main():
    req=Request('https://api.github.com/graphql',data=json.dumps({'query':QUERY,'variables':{'login':os.environ.get('GITHUB_USERNAME','R3dra1n')}}).encode(),headers={'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Content-Type':'application/json','User-Agent':'coastal-contribution-calendar'})
    with urlopen(req,timeout=30) as response:
        result=json.load(response)
    if result.get('errors') or not result.get('data',{}).get('user'):
        raise RuntimeError('Could not retrieve GitHub contribution data')
    weeks=result['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    if not weeks: raise RuntimeError('Empty contribution calendar')
    snake = True
    food_times = []
    colors=['#e2ece9','#f2ced7','#e8a7b9','#d97f9b','#bf5678']
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 330" role="img" aria-labelledby="title desc">',
        '<title id="title">A year of GitHub contributions</title>',
        '<desc id="desc">Each square represents one day. Darker squares indicate more contributions.</desc>',
        '<rect width="1100" height="330" fill="#f8f7f1"/>',
        '<text x="55" y="53" font-family="Georgia, serif" font-size="27" fill="#294d60">A year of small steps</text>',
        '<text x="56" y="79" font-family="Arial, sans-serif" font-size="13" letter-spacing="2" fill="#72949b">CONTRIBUTION TIDES</text>',
        '<path d="M55 95 C200 88 320 105 465 95 S725 87 850 96 S1000 98 1045 91" fill="none" stroke="#c2dad5" stroke-width="2"/>']
    last_month=''
    for col,week in enumerate(weeks):
        days=week['contributionDays']
        if not days: continue
        month=days[0]['date'][:7]
        if month!=last_month:
            if col <= 50:
                month_name=date.fromisoformat(days[0]['date']).strftime('%b')
                parts.append(f'<text x="{56+col*18.4:.1f}" y="121" font-family="Arial,sans-serif" font-size="11" fill="#6d8a90">{month_name}</text>')
            last_month=month
        for day in days:
            row=(date.fromisoformat(day['date']).weekday()+1)%7
            count=int(day['contributionCount'])
            level=0 if count==0 else min(4,1+int(math.log2(count)))
            label=html.escape(day['date'])
            cell=f'<rect x="{56+col*18.4:.1f}" y="{133+row*19}" width="13" height="13" rx="{7 if count else 3}" fill="{colors[level]}"><title>{label}: {count} contributions</title>'
            if snake and count:
                horizontal=(len(weeks)-1)*18.4
                distance=row*(horizontal+19)+(col if row%2==0 else len(weeks)-1-col)*18.4
                total=8*horizontal+6*19+218
                t=distance/total
                food_times.append(t)
                before=max(.001,min(.994,t-.001))
                after=min(.996,max(before+.001,t+.001))
                restore_start=min(.998,max(after+.0004,t+.055))
                restored=min(.9995,max(restore_start+.0004,t+.075))
                cell+=f'<animate attributeName="opacity" values="1;1;0.18;0.18;1;1" keyTimes="0;{before:.4f};{after:.4f};{restore_start:.4f};{restored:.4f};1" dur="50s" repeatCount="indefinite"/>'
            parts.append(cell+'</rect>')
    parts.extend(['<text x="56" y="298" font-family="Arial,sans-serif" font-size="12" fill="#779096">One idea at a time.</text>',
      '<text x="885" y="298" font-family="Arial,sans-serif" font-size="12" fill="#779096">Less</text>'])
    for i,c in enumerate(colors): parts.append(f'<rect x="{920+i*19}" y="287" width="13" height="13" rx="{7 if i else 3}" fill="{c}"/>')
    parts.append('<text x="1020" y="298" font-family="Arial,sans-serif" font-size="12" fill="#779096">More</text>')
    if snake:
        x0=62.5
        x1=62.5+(len(weeks)-1)*18.4
        path=f'M {x0} 139.5'
        for row in range(7):
            path+=f' L {x1 if row%2==0 else x0:.1f} {139.5+row*19:.1f}'
            if row<6:
                path+=f' L {x1 if row%2==0 else x0:.1f} {139.5+(row+1)*19:.1f}'
        # Return around the outside of the calendar to form a closed path.
        path+=f' L {x1+16:.1f} 253.5 L {x1+16:.1f} 275.5 L {x0-14:.1f} 275.5 L {x0-14:.1f} 139.5 L {x0:.1f} 139.5 Z'
        food_times.sort()
        segment_delay=0.095
        # Each contribution day adds one body segment; the loop starts fresh.
        segment_count=2+len(food_times)
        for i in reversed(range(1, segment_count+1)):
            growth=0.0 if i<=2 else food_times[i-3]
            visible=min(.999, max(.001, max(growth, i*segment_delay/50)))
            before=max(0,visible-.0005)
            delay=(50-i*segment_delay)%50
            fade_start=max(visible+.002, .89+.08*(segment_count-i)/max(1,segment_count-1))
            fade_end=min(.9995, fade_start+.015)
            parts.append(f'<g opacity="0"><circle r="6" fill="#729e8b" stroke="#f8f7f1" stroke-width="1"/><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{before:.5f};{visible:.5f};{fade_start:.5f};{fade_end:.5f};1" dur="50s" repeatCount="indefinite"/><animateMotion path="{path}" dur="50s" begin="-{delay:.4f}s" repeatCount="indefinite"/></g>')
        parts.append(f'<g><circle r="7" fill="#477b6d" stroke="#f8f7f1" stroke-width="1"/><circle cx="-2" cy="-2" r="1" fill="white"/><circle cx="2" cy="-2" r="1" fill="white"/><animateMotion path="{path}" dur="50s" repeatCount="indefinite"/></g>')
    parts.append('</svg>')
    out=Path(__file__).resolve().parent.parent/'assets'/'contributions-snake.svg';out.write_text('\n'.join(parts),encoding='utf-8');print(f'Generated {len(weeks)} weeks.')
if __name__=='__main__':main()
