#!/usr/bin/env python3
"""Offline semantic-cue lookup of synthesized design knowledge and original recipes."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(relative: str):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))

def sources() -> dict:
    from bootstrap_motion_libraries import LIBRARIES
    base = read('references/motion-sources.json')
    result = {name: {'id': name, 'url': url, 'review_level': 'legacy_index_only'} for name, url in LIBRARIES.items()}
    result.update({s['id']: s for s in base['sources'] + base.get('web_sources', [])})
    result.update({s['id']: s for s in read('references/research-sources.json')['sources']})
    return result

def capabilities() -> list[dict]:
    return [{k: card[k] for k in ('id', 'title', 'keywords')} for card in read('references/knowledge-cards.json')['cards']]

def cues(query: str) -> set[str]:
    # Exact Chinese cues can occur inside an unspaced sentence; English uses words.
    words = re.findall(r'[a-z0-9][a-z0-9-]*|[\u3400-\u9fff]+', query.lower())
    return {part for word in words for part in ([word] +
            ([word[i:i+2] for i in range(len(word)-1)] if re.search(r'[\u3400-\u9fff]', word) else []))}

def search(query: str, *, card_id: str | None = None, source_id: str | None = None,
           materials: bool = False, limit: int = 8) -> dict:
    cards = read('references/knowledge-cards.json')['cards']
    material_items = read('assets/material-library.json')['materials']
    registry = read('references/research-sources.json')
    inventory = sources()
    if source_id:
        source_id = registry['aliases'].get(source_id, source_id)
        unresolved = next((item for item in registry['unresolved'] if item['id'] == source_id), None)
        if source_id in registry['excluded']:
            return {'ok': True, 'source_id': source_id, 'status': 'excluded_by_user', 'results': []}
        if unresolved:
            return {'ok': True, 'source_id': source_id, 'status': 'unresolved', 'reason': unresolved['reason'], 'results': []}
        if source_id not in inventory:
            raise ValueError('Unknown source: ' + source_id)
        selected = [card for card in cards if source_id in card['sources']]
        return {'ok': True, 'source': inventory[source_id], 'results': selected,
                'scope': 'Source assessment and linked synthesis; not installation status.'}
    if card_id:
        matches = [card for card in cards if card['id'] == card_id]
        if not matches:
            raise ValueError('Unknown card: ' + card_id)
    else:
        needles = cues(query)
        if not needles:
            raise ValueError('Provide a query, --card or --source.')
        ranked = []
        for item in material_items if materials else cards:
            keywords = {s.lower() for s in item['keywords']}
            body = (item['id'] + ' ' + item['title'] + ' ' + ' '.join(keywords)).lower()
            score = sum(8 if n in keywords or n == item['id'] else 1 for n in needles if n in body)
            if score:
                ranked.append((score, item['id'], item))
        matches = [dict(item, score=score) for score, _, item in sorted(ranked, key=lambda x: (-x[0], x[1]))[:max(1, limit)]]
    source_ids = {sid for item in matches for sid in item.get('sources', [])}
    material_ids = {mid for item in matches for mid in item.get('materials', [])}
    return {'ok': True, 'query': query, 'scope': 'Offline reference suggestions, not automatic creative decisions or verified renders.',
            'results': matches, 'sources': [inventory[sid] for sid in sorted(source_ids)],
            'materials': [item for item in material_items if item['id'] in material_ids]}
