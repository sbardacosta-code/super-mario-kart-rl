from kart_rl.progress import Progress

def test_forward_lap_requires_both_evidence_sources():
    p = Progress(4,0,128)
    for cp in [1,2,3,0]:
        p.update(cp,128)
    assert p.maximum==4 and p.valid_laps==0
    p.update(0,129)
    assert p.valid_laps==1

def test_oscillation_cannot_farm_reward_or_laps():
    p = Progress(4,0,128)
    reward = sum(p.update(cp,128) for cp in [1,0]*100)
    assert reward==.25 and p.valid_laps==0 and p.position==0

def test_backward_finish_crossing_and_lap_counter_spoof():
    p = Progress(4,0,128)
    assert sum(p.update(cp,133,True) for cp in [3,2,1,0]*5)==0
    assert p.valid_laps==0 and not p.complete

def test_backward_then_revisit_does_not_reset_highwater():
    p = Progress(4,0,128)
    assert sum(p.update(cp,128) for cp in [1,2,1,0,1,2])==.5

def test_jump_invalidates_episode():
    p = Progress(8,0,128)
    assert p.update(3,129)==0 and p.invalid
    assert p.update(4,130)==0 and not p.complete

def test_five_full_laps_complete():
    p = Progress(4,0,128)
    for lap in range(5):
        for cp in [1,2,3,0]:
            p.update(cp,128+lap+(cp==0))
    assert p.complete and p.valid_laps==5

def test_backward_flag_conflict_fails_closed():
    p = Progress(4,0,128)
    assert p.update(1,128,True)==0 and p.invalid
