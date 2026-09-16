"""Independent memory monitor; marks partial coverage and inaccessible children."""
import argparse,json,time,sys
from pathlib import Path
import psutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from smb3_rl.common import now,write_json
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pid',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
process=psutil.Process(a.pid);start=time.perf_counter()
report={'started_at':now(),'status':'sampling','interval_seconds':0.1,'coverage':'Started after the built-in monitor failed; not a full-run peak.', 'parent_peak_rss_bytes':0,'parent_and_children_peak_rss_bytes':0,'samples':0,'children_samples':0,'errors':[]}
next_save=0
while True:
 try:
  if not process.is_running() or process.status()==psutil.STATUS_ZOMBIE:break
  parent=process.memory_info().rss;report['parent_peak_rss_bytes']=max(report['parent_peak_rss_bytes'],parent)
  try:
   total=parent+sum(c.memory_info().rss for c in process.children(recursive=True));report['children_samples']+=1
   report['parent_and_children_peak_rss_bytes']=max(report['parent_and_children_peak_rss_bytes'],total)
  except (psutil.Error,PermissionError) as exc:
   msg=type(exc).__name__+': '+str(exc)
   if msg not in report['errors']:report['errors'].append(msg)
  report['samples']+=1
 except psutil.NoSuchProcess:break
 except (psutil.Error,PermissionError) as exc:
  report['errors'].append(str(exc));break
 if time.perf_counter()>next_save:
  report['observed_seconds']=time.perf_counter()-start;write_json(a.output,report);next_save=time.perf_counter()+10
 time.sleep(.1)
report.update(status='finished',ended_at=now(),observed_seconds=time.perf_counter()-start)
write_json(a.output,report)
print(json.dumps(report,indent=2))
