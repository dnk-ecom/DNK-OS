# Neuro-Retention Heatmap & Attention Simulation Model

## Mathematical Foundations

### 1. Baseline Retention Decay (Survival Analysis)
In mobile short-form video (TikTok, Reels, Shorts), viewer loss follows an accelerated hazard rate $h_0(t)$ modeled as:
$$R_{base}(t) = \frac{100}{1 + (t / t_0)^\alpha}$$
Typical unoptimized parameter estimates:
- Characteristic drop-off time $t_0 \approx 3.2\text{s}$
- Dispersion index $\alpha \approx 0.85$
- Typical 3s survival: ~50%
- Typical 15s completion: ~18-20%

### 2. Retention Boosters & Hazard Reduction Multipliers
Each active stimulus attenuates the instantaneous hazard rate $h(t)$:
$$h(t) = h_0(t) \cdot \prod_{k} (1 - \delta_k)$$

- **Validated Hook ($\delta_{hook} = 0.55$)**: Active during 0.0s–3.0s. Cuts the early swipe risk by more than half, raising 3-second retention from ~50% to 82–88%.
- **Kinetic Subtitles ($\delta_{captions} = 0.35$)**: Prevents silent-scrolling drop-offs and reduces cognitive parsing strain.
- **Pattern Interrupts ($\delta_{interrupt} = 0.60$)**: Applied at the exact timestamp of punch zoom or B-roll cutaway. Resets boredom/habituation.
- **Sound Design & Ducking ($\delta_{sound} = 0.30$)**: Enforces speech intelligibility >90% and keeps the soundscape engaging without masking dialogue.

Cumulative retention calculation:
$$R(t) = R(t-1) \cdot (1 - h(t))$$

### 3. Cognitive Attention Score ($A(t) \in [0, 100]$)
Attention decays dynamically over continuous uninterrupted speech:
$$A(t) = A_{base} - \text{fatigue}(t) + \sum \text{StimulusBoost}_i$$

Attention zones classification:
- **Green (>75%)**: Peak Focus ⚡ / Safe Retention. Viewer is actively hooked.
- **Yellow (55–75%)**: Fading Attention ⚠️. Pacing is becoming monotonous.
- **Red (<55% or hazard > 0.12)**: Drop-off Danger Zone 🚨. High risk of immediate swipe-away.

### 4. Viral Index & Neuro Engagement Score
- **Neuro Engagement Score**: Time-weighted average attention normalized across video duration.
- **Viral Index**: Weighted composite of 3s Hook Retention (40%), Completion Rate (35%), and Minimum Attention Valley (25%). Scores >80 indicate high organic distribution likelihood.
