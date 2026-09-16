# Teacher guide: watching Mario learn

Open the [permanent classroom index](classroom/README.md). Reports and GIFs need only a browser; no account, installation or ROM is needed to watch. Download the repository for offline reports, preserving its directory layout. Models are separate GitHub Release assets. Running a policy requires the pinned local Python environment.

## A 45-minute classroom sequence

1. **Predict (5 min).** Watch the untrained model and hold-run-right baseline. Ask where each will fail and what would count as improvement.
2. **Explain (10 min).** An observation is a short stack of screenshots. An action is a button combination. Reward is a numeric teaching signal for new progress, with time/death costs. The policy is the neural network's action rule. PPO collects experience, then updates its weights. Evaluation freezes the weights.
3. **Compare stages (10 min).** Show the same seed's beginning and ending clips before and after training. Compare progress, success and finishing time. Inspect reward separately. Do not hide a regression or failed trial.
4. **Investigate a mistake (10 min).** Choose one trial/frame range. Describe visible movement, then use its action trace. “Mario continued right into the enemy” is an observation; “the network cannot recognize enemies” is a hypothesis requiring more tests.
5. **Question the measurement (10 min).** Show the validation's false-clear bug: the emulator reported success during a death fade-out. Explain why reward and termination logic need independent visual checks. Discuss small samples and the same-level limitation.

## Discussion questions

- Can reward improve without finishing the level?
- Why should walking back and forth not earn progress repeatedly?
- How do holding jump and releasing/repressing jump change behavior?
- Does the agent have the actions needed to recover from every mistake?
- Why do five seeds not mean five different levels?
- Can a later checkpoint regress? What could distinguish noise from a real decline?
- Why are missing evaluations not zero scores?
- Why are finish times averaged only across successful runs?
- How could a false success flag mislead both training and the professor?
- What further trials would support a claim of reliable completion or generalization?

For every stage, record what changed, measured improvement/regression, visible remaining failures, the location/frame range, and unresolved hypotheses. Link each statement to a clip or metric. Read `ANALYSIS.md` alongside the generated report. The original and final policies may both fail; that is useful classroom evidence rather than a reason to hide the experiment.
