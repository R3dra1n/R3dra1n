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
    colors=['#e2ece9','#c3ddd8','#93c4bf','#619c9f','#3d718b']
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
            parts.append(f'<rect x="{56+col*18.4:.1f}" y="{133+row*19}" width="13" height="13" rx="3" fill="{colors[level]}"><title>{label}: {count} contributions</title></rect>')
    parts.extend(['<text x="56" y="298" font-family="Arial,sans-serif" font-size="12" fill="#779096">One idea at a time.</text>',
      '<text x="885" y="298" font-family="Arial,sans-serif" font-size="12" fill="#779096">Less</text>'])
    for i,c in enumerate(colors): parts.append(f'<rect x="{920+i*19}" y="287" width="13" height="13" rx="3" fill="{c}"/>')
    parts.append('<text x="1020" y="298" font-family="Arial,sans-serif" font-size="12" fill="#779096">More</text></svg>')
    out=Path(__file__).resolve().parent.parent/'assets'/'contributions.svg';out.write_text('\n'.join(parts),encoding='utf-8');print(f'Generated {len(weeks)} weeks.')
if __name__=='__main__':main()
