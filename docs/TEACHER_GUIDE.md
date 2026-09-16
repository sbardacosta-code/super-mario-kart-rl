# Teacher guide

Open the [permanent classroom index](classroom/README.md). Reports, charts, and GIFs are public and require a browser, not a GitHub account, installation, or ROM. For offline teaching, download the repository and keep linked session folders beside the documents. To run the game or a model, follow the local setup and supply a compatible ROM/save state. Model downloads will appear in GitHub Releases only after real checkpoints exist.

**Today's lesson can cover experiment design and the verified software setup. There is no Mario Kart gameplay evidence yet.** Do not describe the Airstriker compatibility check as Mario learning to drive.

## A 45-minute lesson once stages exist

1. **Predict (5 minutes).** Show the initial untrained policy and the hold-accelerate baseline. Ask students to predict which outcome will improve first: reward, checkpoint progress, a valid lap, or a completed race.
2. **Explain the loop (10 minutes).** A screenshot is an observation. The policy chooses a button combination. The emulator advances four frames. A reward tells the learner about newly achieved progress and elapsed time. PPO gathers experience, then updates the policy's neural-network weights. Evaluation uses fixed weights and makes no updates.
3. **Compare evidence (10 minutes).** Watch the same seed's beginning and ending clips at the initial, intermediate, and final stages. Inspect the trace when clips leave a gap. Compare lap and completion charts, then inspect training reward separately. Include a regression or stalled stage if one exists.
4. **Investigate a mistake (10 minutes).** Pick a precise trial and frame range. Describe visible movement and the measured progress/lap values. Ask which explanations the data support and what controlled experiment would distinguish alternatives. “The kart turns right while progress stays constant” is an observation. “It cannot see the bend” is a hypothesis unless tested.
5. **Challenge the conclusion (10 minutes).** Show incomplete evaluations and held-out action-seed results. Discuss the same-track limitation, duplicate deterministic baselines, small samples, and why selected good clips do not prove reliable driving.

## Plain-language vocabulary

| Term | Meaning in this project |
|---|---|
| Observation | Four small grayscale screenshots, giving a short visual history. |
| Action | One of four permitted button combinations. |
| Reward | A numeric teaching signal for new ordered progress, with a small time cost. |
| Policy | The model's rule for choosing an action from screenshots. |
| PPO update | A change to model weights after collecting a batch of experience. |
| Checkpoint | A saved model at one learning stage; not the same as an on-track checkpoint. |
| Episode | One attempt from the same verified start until finish or a defined stopping condition. |
| Evaluation | Trials of a frozen model under a documented protocol. |
| Regression | A later stage performs worse on measured outcomes; the cause may be unknown. |

## Discussion questions

- Why might reward rise while race completion remains zero?
- How could an agent exploit a reward for crossing a line? Which tests defend against it here?
- Does touching the finish line after reversing count as a lap? What independent evidence is needed?
- What can the ending clip reveal that the beginning clip cannot? What is lost between them?
- Why do five seeds not mean five different race tracks?
- Could hold-accelerate produce identical trials? What does that imply about uncertainty?
- Why do we report finishing time only for successful races?
- When a later policy regresses, which measurements changed and which explanations remain untested?
- Would adding drift help? What would changing the action set do to comparability?
- What evidence would justify saying the policy finishes reliably or generalizes?

## Stage analysis worksheet

For **every** saved stage, record: model ID; active training minutes; evaluation completeness; mean/range of valid laps; completion numerator/denominator; successful finish times; progress distribution; links to clips and action traces. Then add:

- **What changed:** parameters, additional experience, or nothing except stochastic action sampling.
- **Observed improvement/regression:** exact comparison backed by a metric or clip timestamp/frame range.
- **Where Mario struggles:** identify track location visually or by validated checkpoint IDs; do not invent corner names from RAM alone.
- **What remains uncertain:** hypotheses and proposed checks.
- **Lesson learned:** what the class can conclude within this protocol.

Keep failures and unfinished stages in the gallery. A demonstration clip may be selected for clarity, but label that selection and show all-trial results nearby. Do not replace the latest stage with the “best-looking” one without disclosure.
