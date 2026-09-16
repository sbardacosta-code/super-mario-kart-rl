"""Plot exploratory training episodes separately from fixed-policy evaluation."""
import argparse,gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from smb3_rl.common import write_json

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('session',type=Path);a=p.parse_args()
 rows=[];reward=0.;decisions=0
 for path in sorted((a.session/'logs').glob('*-training-trace.jsonl.gz')):
  with gzip.open(path,'rt') as stream:
   for line in stream:
    r=json.loads(line);reward+=r['reward'];decisions+=1
    if r['terminated'] or r['truncated']:
     rows.append({'model_decision':r['model_decision'],'progress_pixels':r['progress_pixels'],
                  'level_complete':r['level_complete'],'death':r['death'],'training_reward':reward,
                  'episode_decisions':decisions,'frames':r['frames']})
     reward=0.;decisions=0
 write_json(a.session/'training-history.json',{'episodes':rows,'trailing_partial_episode_decisions':decisions,
            'interpretation':'Exploratory training episodes, not independent fixed-policy evaluations.'})
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True,layout='constrained')
 fields=[('progress_pixels','Furthest progress (pixels)'),('training_reward','Shaped episode reward'),('level_complete','Level completion (0 or 1)')]
 x=[r['model_decision'] for r in rows]
 for ax,(field,label) in zip(axes,fields):
  y=[float(r[field]) for r in rows]
  smoothed=[sum(y[max(0,i-49):i+1])/len(y[max(0,i-49):i+1]) for i in range(len(y))]
  ax.scatter(x,y,s=5,alpha=.2,color='#687787',label='Each completed training episode')
  ax.plot(x,smoothed,color='#1c678f',label='Trailing mean, up to 50 episodes')
  ax.set_ylabel(label);ax.grid(alpha=.2)
  if field=='level_complete':ax.set_ylim(0,1)
 axes[0].legend(fontsize=8);axes[-1].set_xlabel('Cumulative agent decisions in this model')
 fig.suptitle('Exploratory training history — not the fixed-seed evaluation')
 fig.savefig(a.session/'training-history.png',dpi=150);plt.close(fig)
 print('Recorded training episodes:',len(rows),'clears:',sum(r['level_complete'] for r in rows))
if __name__=='__main__':main()
