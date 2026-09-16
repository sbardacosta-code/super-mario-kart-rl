"""Real-game validation, regression replay, and traceable control probes."""
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from stable_baselines3.common.env_checker import check_env
from .common import ROOT,read_json,write_json,identity,now,digest
from .env import MarioEnv,HighWater

def run():
    c=read_json(ROOT/'configs/smb3-1-1.json');out=ROOT/'sessions/2026-09-16-smb3-validation'
    out.mkdir(exist_ok=True)
    e=MarioEnv(c,validate=False);checks={};report={'at':now(),'status':'running','identity':identity(c),'checks':checks}
    try:
        check_env(e,warn=True);checks['gymnasium_api']='passed'
        hashes=[]
        for seed in range(10):
            obs,info=e.reset(seed=seed);h=hashlib.sha256(obs.tobytes()+e.raw.unwrapped.ram.tobytes())
            for _ in range(30):
                obs,r,t,tr,info=e.step(3);h.update(obs.tobytes());h.update(str((info['x_pos'],info['y_pos'],r,t,tr)).encode())
            hashes.append(h.hexdigest())
        checks['ten_resets_and_120_frame_replays_identical']=len(set(hashes))==1
        report['reset_replay_hashes']=hashes
        controls={}
        for action in range(len(c['actions'])):
            obs,info=e.reset();images=[];rows=[]
            # First decision releases buttons; then compare each configured action.
            e.step(0)
            for n in range(20):
                obs,r,t,tr,info=e.step(action);rows.append({'decision':n+1,'action':action,**info})
                images.append(Image.fromarray(e.render()))
                if t or tr:break
            write_json(out/f'control-{action}.json',rows)
            images[0].save(out/f'control-{action}.gif',save_all=True,append_images=images[1:],duration=67,loop=0)
            controls[c['action_names'][action]]={'max_x':info['max_x'],'y_range':[min(r['y_pos'] for r in rows),max(r['y_pos'] for r in rows)]}
        report['controls']=controls
        checks['right_moves']=controls['walk right']['max_x']>controls['coast']['max_x']
        checks['run_faster_than_walk']=controls['run right']['max_x']>controls['walk right']['max_x']
        checks['jump_changes_vertical_position']=controls['jump right']['y_range']!=controls['walk right']['y_range']
        obs,info=e.reset();frames=[];rows=[]
        for n in range(300):
            a=4 if n%6<2 else 3
            obs,r,t,tr,info=e.step(a);rows.append({'action':a,'reward':r,**info})
            frames.append(Image.fromarray(e.render()))
            if t or tr:break
        checks['false_clear_replay_is_death_not_success']=info['death'] and not info['level_complete'] and t
        write_json(out/'corrected-death-trace.json',rows)
        frames[0].save(out/'corrected-death.gif',save_all=True,append_images=frames[1:],duration=67,loop=0)
        timeout_config={**c,'episode_frames':7};limited=MarioEnv(timeout_config,validate=False)
        limited.reset();limited.step(0);o,r,t,tr,i=limited.step(0)
        checks['timeout_exact_frames']=tr and not t and i['frames']==7 and i['frames_advanced']==3
        limited.close()
        h=HighWater(24)
        gains=[h.update(x) for x in [30,24,30,24,30,40,24,40]]
        checks['repeated_progress_not_rewarded_twice']=sum(gains)==16
        checks['map_does_not_reward_progress']=h.update(10000,False)==0
        path=ROOT/'.cache/clear-controller-actions.json'
        if path.exists():
            actions=read_json(path);obs,info=e.reset();frames=[];rows=[]
            for a in actions:
                obs,r,t,tr,info=e.step(a);rows.append({'action':a,'reward':r,**info})
                frames.append(Image.fromarray(e.render()))
                if t or tr:break
            write_json(out/'scripted-clear-actions.json',actions)
            write_json(out/'scripted-clear-trace.json',rows)
            frames[-150].save(out/'scripted-clear-ending.gif',save_all=True,append_images=frames[-149:],duration=67,loop=0)
            Image.fromarray(e.render()).save(out/'scripted-clear-end.png')
            # Contact sheet for visually reviewing the actual finish and map return.
            chosen=list(range(max(0,len(frames)-150),len(frames),15))+[len(frames)-1]
            sheet=Image.new('RGB',(256*4,260*((len(chosen)+3)//4)),'white');draw=ImageDraw.Draw(sheet)
            for k,idx in enumerate(chosen):
                x=k%4*256;y=k//4*260;sheet.paste(frames[idx],(x,y));draw.text((x,y+240),f"decision {idx+1}",fill='black')
            sheet.save(out/'scripted-clear-contact-sheet.png')
            checks['scripted_level_clear']=info['level_complete'] and not info['death'] and info['progress_pixels']>2000
            report['scripted_clear_outcome']=info
            for _ in range(60):e.raw.unwrapped._frame_advance(0)
            Image.fromarray(e.raw.unwrapped.screen.copy()).save(out/'scripted-clear-map-plus60.png')
            report['post_terminal_map_image_delay_frames']=60
        else:checks['scripted_level_clear']=False
        checks['pixel_stack']=obs.shape==(4,84,84) and obs.dtype==np.uint8
        report['status']='passed' if all(v is True or v=='passed' for v in checks.values()) else 'failed'
        report['notes']=['Nominal 60 emulated frames/s; no claim that wall time equals game time.',
                         'Scripted successful controller is validation evidence, not PPO training or an evaluated learned model.',
                         'Stage-specific correction requires exact World 1-1 map-panel coordinates before declaring success.']
    finally:
        e.close();write_json(out/'validation.json',report)
    print(report['status'],checks)
    if report['status']!='passed':raise SystemExit(1)
if __name__=='__main__':run()
