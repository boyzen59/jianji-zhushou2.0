import fs from 'node:fs';
import path from 'node:path';
import {geoMercator, geoPath} from 'd3-geo';

const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('Usage: node draw-map.mjs scene.json map.svg');
const cfg = JSON.parse(fs.readFileSync(input, 'utf8'));
const width = cfg.width ?? 1920, height = cfg.height ?? 1080;
if (!Array.isArray(cfg.layers) || !cfg.layers.length) throw new Error('Provide dated, sourced GeoJSON layers.');
const esc = v => String(v ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const theme = {background:'#e8e3d7', land:'#c8c4b6', stroke:'#777b72', ink:'#253d42', accent:'#a64630', ...cfg.theme};
const layers = cfg.layers.map((l,i) => {
  if (!l.source || !l.date) throw new Error(`Layer ${i}: source and historical date are required.`);
  const data = typeof l.geojson === 'string' ? JSON.parse(fs.readFileSync(path.resolve(path.dirname(input), l.geojson),'utf8')) : structuredClone(l.geojson);
  const polygons = geom => {
    if (!geom) return;
    if (geom.type === 'Polygon') fix(geom.coordinates);
    else if (geom.type === 'MultiPolygon') geom.coordinates.forEach(fix);
    else if (geom.type === 'GeometryCollection') geom.geometries.forEach(polygons);
  };
  const fix = rings => rings.forEach((ring,j) => {
    let area=0; for(let k=0;k<ring.length-1;k++) area+=ring[k][0]*ring[k+1][1]-ring[k+1][0]*ring[k][1];
    if ((j===0 && area>0)||(j>0 && area<0)) ring.reverse();
  });
  if (data.type === 'FeatureCollection') data.features.forEach(f=>polygons(f.geometry));
  else if(data.type === 'Feature') polygons(data.geometry); else polygons(data);
  return {...l, data, id:l.id ?? `layer-${i}`};
});
const combined={type:'FeatureCollection',features:layers.flatMap(l=>l.data.type==='FeatureCollection'?l.data.features:l.data.type==='Feature'?[l.data]:[{type:'Feature',geometry:l.data,properties:{}}])};
const projection=geoMercator().fitExtent([[120,155],[width-120,height-150]],combined);
const geo=geoPath(projection);
const pieces=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">`,
 `<rect width="100%" height="100%" fill="${esc(theme.background)}"/>`,
 `<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>`,
 `<g font-family="Microsoft YaHei, sans-serif" fill="${esc(theme.ink)}"><text x="100" y="85" font-size="44" font-weight="600">${esc(cfg.title)}</text><text x="102" y="124" font-size="21" opacity=".7">${esc(cfg.period)}</text></g>`];
for(const layer of layers){
 const data=layer.data, features=data.type==='FeatureCollection'?data.features:[data];
 pieces.push(`<g id="${esc(layer.id)}" data-date="${esc(layer.date)}" fill="${esc(layer.fill??theme.land)}" fill-opacity="${layer.opacity??1}" stroke="${esc(layer.stroke??theme.stroke)}" stroke-width="${layer.strokeWidth??2}" stroke-linejoin="round">`);
 features.forEach((f,i)=>pieces.push(`<path id="${esc(layer.id)}-${i}" d="${esc(geo(f))}"${layer.disputed?' stroke-dasharray="10 7"':''}/>`));pieces.push('</g>');
}
for(const [i,r] of (cfg.routes??[]).entries()){
 if(!r.source || !r.date) throw new Error(`Route ${i}: source and date required.`);
 const d=geo({type:'LineString',coordinates:r.coordinates});
 pieces.push(`<path id="${esc(r.id??`route-${i}`)}" data-date="${esc(r.date)}" d="${esc(d)}" fill="none" stroke="${esc(r.color??theme.accent)}" stroke-width="${r.width??5}" stroke-linecap="round" pathLength="1" marker-end="url(#arrow)"${r.approximate?' stroke-dasharray=".02 .01"':''}/>`);
}
for(const [i,p] of (cfg.places??[]).entries()){
 const [x,y]=projection(p.coordinates);
 pieces.push(`<g id="${esc(p.id??`place-${i}`)}" transform="translate(${x},${y})"><circle r="6" fill="${esc(theme.ink)}" stroke="${esc(theme.background)}" stroke-width="3"/><text x="${p.dx??14}" y="${p.dy??-12}" font-family="Microsoft YaHei, sans-serif" font-size="${p.fontSize??24}" fill="${esc(theme.ink)}" paint-order="stroke" stroke="${esc(theme.background)}" stroke-width="5" stroke-linejoin="round">${esc(p.name)}</text></g>`);
}
const attribution=[...new Set(layers.map(l=>`${l.date} · ${l.source}`).concat((cfg.routes??[]).map(r=>`${r.date} · ${r.source}`)))].join(' / ');
pieces.push(`<text x="100" y="${height-62}" font-family="Microsoft YaHei, sans-serif" font-size="16" fill="${esc(theme.ink)}" opacity=".75">${esc(cfg.footer??attribution)}</text></svg>`);
fs.mkdirSync(path.dirname(path.resolve(output)),{recursive:true});fs.writeFileSync(output,pieces.join('\n'));
fs.writeFileSync(output.replace(/\.svg$/i,'')+'.map.json',JSON.stringify({projection:'geoMercator',scale:projection.scale(),translate:projection.translate(),width,height,period:cfg.period,layers:layers.map(({data,...l})=>l),routes:cfg.routes??[],places:cfg.places??[]},null,2));
console.log(`Wrote SVG and projection metadata: ${output}`);
