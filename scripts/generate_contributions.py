#!/usr/bin/env python3
"""Render the account's GitHub contribution calendar as an isometric SVG."""
import html
from datetime import date
import json
import math
import os
from pathlib import Path
from urllib.request import Request, urlopen

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def main():
    token = os.environ['GITHUB_TOKEN']
    username = os.environ.get('GITHUB_USERNAME', 'R3dra1n')
    request = Request('https://api.github.com/graphql',
                      data=json.dumps({'query': QUERY, 'variables': {'login': username}}).encode(),
                      headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json',
                               'User-Agent': 'coastal-profile-contributions'})
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError('GitHub could not return the contribution calendar: ' + str(result['errors']))
    user = result['data']['user']
    if not user:
        raise RuntimeError('GitHub user not found')
    weeks = user['contributionsCollection']['contributionCalendar']['weeks']
    if not weeks or not any(w['contributionDays'] for w in weeks):
        raise RuntimeError('GitHub returned an empty contribution calendar')
    colors = [('#e4eee9', '#c8dcd6', '#b8cfc8'),
              ('#c6e3d7', '#a6d0c1', '#8abbaa'),
              ('#97cdbd', '#76b3a3', '#5d9c8e'),
              ('#6aaea6', '#4b9291', '#3c7c80'),
              ('#5284a6', '#3d6c90', '#335a7d')]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1050 280" role="img" aria-labelledby="title desc">',
             '<title id="title">GitHub contributions in 3D</title>',
             '<desc id="desc">Each column represents one day. Height and color increase with the number of contributions; heights use a logarithmic scale.</desc>',
             '<path d="M24 143 L956 177 L1022 138 L92 104 Z" fill="#f6f0e7"/>']
    for row in range(7):
        for col, week in enumerate(weeks):
            days = week['contributionDays']
            day = next((d for d in days if (date.fromisoformat(d['date']).weekday() + 1) % 7 == row), None)
            if day is None:
                continue
            count = int(day['contributionCount'])
            level = 0 if count == 0 else min(4, 1 + int(math.log2(count)))
            height = 3 if count == 0 else 4 + min(35, round(8 * math.log2(count + 1)))
            x = 72 + col * 17 - row * 6
            y = 95 + col * 0.65 + row * 8 - height
            top, left, right = colors[level]
            day_label = html.escape(day['date'])
            parts.append(f'<g><title>{day_label}: {count} contributions</title>'
                         f'<path fill="{left}" d="M{x} {y} l0 {height} l8 4 l0 -{height} Z"/>'
                         f'<path fill="{right}" d="M{x+8} {y+4} l0 {height} l12 -4 l0 -{height} Z"/>'
                         f'<path fill="{top}" d="M{x} {y} l12 -4 l8 4 l-12 4 Z"/></g>')
    parts.append('</svg>')
    output = Path(__file__).resolve().parent.parent / 'assets' / 'contributions.svg'
    output.write_text('\n'.join(parts), encoding='utf-8')
    print(f'Generated {output} from {len(weeks)} weeks of GitHub contribution data.')


if __name__ == '__main__':
    main()
