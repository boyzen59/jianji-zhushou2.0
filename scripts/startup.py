#!/usr/bin/env python3
"""Check latest upstream revisions at every skill start and archive complete selected packages."""
from __future__ import annotations
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,shutil,subprocess,sys
from urllib.request import getproxies

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'modules/.package-cache'
STATE=ROOT/'.jianji'
VIDEO={'.mp4','.m4v','.mov','.mkv','.webm','.avi','.mpeg','.mpg','.wmv','.flv'}
OMIT_DIRS={'node_modules','.git','.venv','__pycache__','.package-cache','.source-cache'}
OMIT_NAMES={'.env','.env.local','.env.production'}
OWN_URL='https://github.com/boyzen59/jianji-zhushou2.0.git'

def read(path,default=None):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.is_file() else default
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def command(args,**kwargs):
    env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GIT_LFS_SKIP_SMUDGE='1')
    if args and args[0]=='git':
        proxy=getproxies().get('https')
        proxy_args=['-c','http.proxy='+proxy] if proxy else []
        args=['git',*proxy_args,'-c','http.version=HTTP/1.1','-c','http.lowSpeedLimit=1000','-c','http.lowSpeedTime=30',*args[1:]]
    result=subprocess.run(args,env=env,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=900,**kwargs)
    if result.returncode:raise RuntimeError(result.stderr.strip()[-1500:] or 'Git operation failed')
    return result.stdout
def remote_head(url):
    response=command(['git','ls-remote',url,'HEAD'])
    if not response.strip():raise RuntimeError('No remote HEAD')
    return response.split()[0]
def keep(name,sid,own=False):
    p=Path(name)
    if p.suffix.lower() in VIDEO or p.name in OMIT_NAMES or set(p.parts)&OMIT_DIRS:return False
    lower=name.lower().replace('-','').replace('_','')
    if ('hyper'+'frames') in lower or ('herk'+'editkit') in lower:return False
    if own and (name.startswith('modules/') or name.startswith('.jianji/')):return False
    if own and name=='references/local-installation.md':return False
    if sid=='wtt-code-animation-studio':
        return name.startswith('wattter_skills/wtt-code-animation-studio/') or '/' not in name
    return True
def preserve(path,destination):
    # All moves are file-only and bounded by the explicitly selected skill root.
    if not path.resolve().is_relative_to(ROOT.resolve()) or not destination.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Archive path outside the skill')
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():destination=destination.with_name(destination.name+'.'+sha(path)[:10])
    shutil.move(str(path),str(destination))
def package(sid,url,target,previous,revision=None,own=False):
    revision=revision or remote_head(url)
    old=read(previous,{}) or {}
    if old.get('revision')==revision and old.get('package_complete') is True:
        tracked=old.get('files',{})
        missing=[name for name in tracked if not (target/name).is_file()]
        if not missing:return {'id':sid,'status':'latest','revision':revision,'files':len(tracked)},None
    repo=CACHE/sid
    repo.parent.mkdir(parents=True,exist_ok=True)
    if not (repo/'.git').is_dir():
        command(['git','-c','core.longpaths=true','clone','--filter=blob:none','--no-checkout','--depth','1',url,str(repo)])
    command(['git','-C',str(repo),'config','core.longpaths','true'])
    command(['git','-C',str(repo),'fetch','--depth','1','origin',revision])
    listing=command(['git','-C',str(repo),'ls-tree','-r','-z',revision])
    blobs={};submodules=[];omitted=[]
    for record in listing.split('\0'):
        if not record:continue
        header,name=record.split('\t',1);mode,kind,oid=header.split()
        if kind=='commit':submodules.append(name);continue
        if kind!='blob':continue
        if keep(name,sid,own):blobs[name]=oid
        else:omitted.append(name)
    patterns='\n'.join('/'+re.sub(r'([\\*?\[\]])',r'\\\1',name) for name in blobs)+'\n'
    command(['git','-C',str(repo),'sparse-checkout','init','--no-cone'])
    command(['git','-C',str(repo),'sparse-checkout','set','--no-cone','--stdin'],input=patterns)
    command(['git','-C',str(repo),'checkout','--detach',revision])
    oldfiles=old.get('upstream_files',old.get('files',{}));files={};upstream_files={};local=[];missing=[];lfs=[]
    for name in blobs:
        src=(repo/name).resolve();dest=(target/name).resolve()
        if not src.is_relative_to(repo.resolve()) or not dest.is_relative_to(target.resolve()):raise ValueError('Invalid package path')
        if not src.is_file():missing.append(name);continue
        digest=sha(src)
        upstream_files[name]=digest
        if dest.is_file():
            actual=sha(dest)
            if name in oldfiles and actual!=oldfiles[name] and actual!=digest:
                incoming=ROOT/'modules/incoming'/sid/revision/name
                incoming.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,incoming)
                files[name]=actual;local.append(name);continue
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.is_file() or sha(dest)!=digest:shutil.copy2(src,dest)
        files[name]=digest
        if src.stat().st_size<1024:
            try:
                if src.read_text(encoding='utf-8').startswith('version https://git-lfs.github.com/spec/v1'):lfs.append(name)
            except UnicodeError:pass
    retired=[]
    for name,digest in oldfiles.items():
        path=target/name
        if name not in blobs and path.is_file() and sha(path)==digest and name not in ['ADAPTER.md','source.json']:
            preserve(path,ROOT/'modules/history'/sid/old.get('revision','previous')[:12]/name);retired.append(name)
    complete=not missing and not submodules and not lfs
    state={'id':sid,'url':url,'revision':revision,'checked_at':datetime.now(timezone.utc).isoformat(),
           'package_complete':complete,'scope':'Complete selected Git package except video files, generated dependencies, private env files and excluded runtime directories.',
           'files':files,'upstream_files':upstream_files,'omitted_paths':omitted,'missing_paths':missing,'git_submodules':submodules,
           'git_lfs_assets':lfs,'local_edits_retained':local,'retired_paths_archived':retired}
    write(previous,state)
    return {'id':sid,'status':'updated' if complete else 'package_needs_dependency','revision':revision,
            'files':len(files),'missing':len(missing),'submodules':submodules,'lfs_assets':len(lfs),'local_edits':len(local)},state

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-self',action='store_true',help='Bootstrap before this repository is first published.')
    parser.add_argument('--source',action='append',help='Limit to selected sources for maintenance; normal start checks all.')
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if not shutil.which('git'):raise SystemExit('Git is required to check and update full packages.')
    STATE.mkdir(exist_ok=True)
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'self':{},'sources':[]}
    exclusions=set(read(ROOT/'references/research-sources.json',{}).get('excluded',[]))
    if not args.skip_self:
        try:
            report['self'],_=package('_self',OWN_URL,ROOT,STATE/'self-update.json',own=True)
        except Exception as exc:report['self']={'status':'offline_retained','reason':str(exc)}
    research_path=ROOT/'references/research-sources.json'
    research=read(research_path,{})
    research['excluded']=sorted(exclusions | set(research.get('excluded',[])))
    write(research_path,research)
    manifest_path=ROOT/'references/motion-sources.json';manifest=read(manifest_path)
    manifest['sources']=[s for s in manifest['sources'] if s['id'] not in exclusions]
    selected=[s for s in manifest['sources'] if not args.source or s['id'] in args.source]
    def sync(source):
        sid=source['id'];folder=ROOT/'modules/upstream'/sid
        try:
            return package(sid,source['url'],folder,folder/'source.json')
        except Exception as exc:return {'id':sid,'status':'offline_retained','reason':str(exc)},None
    updates={}
    with ThreadPoolExecutor(max_workers=max(1,min(args.workers,8))) as pool:
        futures=[pool.submit(sync,s) for s in selected]
        for future in as_completed(futures):
            status,state=future.result();report['sources'].append(status)
            if state:updates[status['id']]=state
            print(json.dumps(status,ensure_ascii=False),flush=True)
    for source in manifest['sources']:
        if source['id'] in updates:
            state=updates[source['id']]
            source.update(audited_commit=state['revision'],reference_files=list(state['files']),status='full package archived' if state['package_complete'] else 'package has missing dependencies')
    write(manifest_path,manifest)
    write(STATE/'startup-report.json',report)
    report['summary']={'checked':len(report['sources']),'latest_or_updated':sum(s['status'] in ['latest','updated'] for s in report['sources']),
                       'offline_or_incomplete':sum(s['status'] not in ['latest','updated'] for s in report['sources'])}
    write(STATE/'startup-report.json',report)
    print(json.dumps({'summary':report['summary']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
