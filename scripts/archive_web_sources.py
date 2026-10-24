#!/usr/bin/env python3
"""Archive the complete selected upstream package, including non-video runtime assets."""
import argparse,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',action='append',required=True)
p.add_argument('--force',action='store_true',help='Compatibility flag; upstream is always checked.')
a=p.parse_args()
command=[sys.executable,str(Path(__file__).with_name('startup.py'))]
for source in a.source:command+=['--source',source]
raise SystemExit(subprocess.call(command))
