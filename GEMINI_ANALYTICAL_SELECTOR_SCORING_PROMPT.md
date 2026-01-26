# Analytical Selector and Scoring Formula Prompt

Create a detailed PowerPoint slide (or slides) presenting the analytical selector development and preference-weighted scoring function. This section explains how the system evaluates and ranks feasible connection candidates.

## ANALYTICAL SELECTOR AND SCORING SECTION OVERVIEW

This section should consist of **2-3 slides** covering:
1. Analytical selector overview and feasibility filtering
2. Connection performance profiles
3. Scoring function components and formulas

**Total time allocation:** 2-3 minutes

---

## SLIDE 1: ANALYTICAL SELECTOR OVERVIEW AND FEASIBILITY FILTERING

### Purpose
Explain how the analytical selector computes torque capacities and filters infeasible candidates.

### Content Structure

**Part A: Analytical Selector Process**
The analytical selector evaluates three connection types by computing their torque capacities using DIN-based equations:
- **Press fits:** M_t,press = (π/2) μ p L d²
- **Keys:** M_t,key = min(T_τ, T_p) where T_τ = shear capacity, T_p = bearing capacity
- **Splines:** M_t,spline = K × L × z × h_eff × r_m × p_allow (K = 0.75)

**Part B: Design Torque Calculation**
- **Design torque:** M_design = M_req × S_R
  - M_req = required torque (user input)
  - S_R = safety factor (user input)
- **Purpose:** Design torque is the minimum torque capacity required for mechanical feasibility

**Part C: Feasibility Filtering (Two-Stage Process)**
- **Stage 1: Mechanical Feasibility**
  - **Criterion:** M_t ≥ M_design
  - Connection must have sufficient torque capacity to meet design torque
  - Applied to all three connection types
- **Stage 2: Practical Feasibility (Press Fits Only)**
  - **Interference plausibility check:** U_w ≤ 0.020mm (typical limit for manufacturability)
  - Prevents selection of press fits with unrealistically high interference
  - Even if mechanically feasible, press fit is rejected if interference exceeds practical limit
- **Result:** Only feasible candidates proceed to scoring stage
- **If no candidate is feasible:** System returns "none" with explicit reason (e.g., "press-fit torque OK but rejected by interference check")

**Part D: Key Insight**
- Feasibility serves as prerequisite to preference-based evaluation
- Only feasible connections are considered for ranking
- System enforces both mechanical safety (torque capacity) and practical constraints (manufacturability)

**Visual Elements:**
- **Flowchart:**
  - Input parameters → Capacity calculations → Feasibility filtering → Scoring (if feasible)
  - Show two-stage filtering: Mechanical → Practical (press fits only)
- **Optional:** Simple diagram showing M_t vs M_design comparison

**Key Message:**
"Analytical selector computes torque capacities using DIN standards, then filters infeasible candidates based on mechanical feasibility (M_t ≥ M_design) and practical constraints (interference limits for press fits)."

**Transition to next slide:**
"Once feasible candidates are identified, they are ranked using a preference-weighted scoring function..."

---

## SLIDE 2: CONNECTION PERFORMANCE PROFILES

### Purpose
Explain how each connection type is characterized across eight application dimensions.

### Content Structure

**Part A: Eight Application Dimensions**
Each connection type is evaluated across eight preference dimensions:
1. Assembly/disassembly ease
2. Axial movement suitability
3. Manufacturing cost
4. Bidirectional torque capability
5. Vibration resistance
6. High-speed suitability
7. Maintenance ease
8. Durability/fatigue life

**Part B: Performance Profile Values**
Each connection type has a fixed performance profile (0.0 = very poor, 1.0 = excellent) across these dimensions:

**Press Fit Profile:**
- Assembly: 0.20 (poor - difficult disassembly)
- Axial movement: 0.10 (very poor - not possible)
- Cost: 0.70 (good - no additional components)
- Bidirectional: 0.80 (good - friction works both ways)
- Vibration: 0.85 (very good - excellent concentricity)
- High-speed: 0.90 (excellent - no backlash)
- Maintenance: 0.25 (poor - difficult to disassemble)
- Durability: 0.75 (good - low stress concentration)

**Key Profile:**
- Assembly: 0.75 (good - simple insertion)
- Axial movement: 0.30 (poor - limited)
- Cost: 0.50 (moderate - standardized components)
- Bidirectional: 0.70 (good - form closure)
- Vibration: 0.45 (moderate - potential backlash)
- High-speed: 0.55 (moderate - stress concentrations)
- Maintenance: 0.80 (good - easy disassembly)
- Durability: 0.40 (moderate - stress concentrations at keyways)

**Spline Profile:**
- Assembly: 0.40 (moderate - requires precision)
- Axial movement: 0.95 (excellent - designed for sliding)
- Cost: 0.20 (poor - expensive manufacturing)
- Bidirectional: 0.90 (excellent - form closure)
- Vibration: 0.70 (good - load sharing)
- High-speed: 0.75 (good - good concentricity)
- Maintenance: 0.30 (moderate - more complex)
- Durability: 0.85 (excellent - load sharing across teeth)

**Part C: Profile Assignment Rationale**
- **Press fits:** High vibration resistance and high-speed suitability (excellent concentricity, no backlash), but poor assembly/disassembly and maintenance (permanent connections)
- **Keys:** Balanced, low-cost solution with good assembly/disassembly and maintenance, but lower vibration resistance and durability (keyways introduce backlash and stress concentrations)
- **Splines:** Excellent axial movement, bidirectional torque, and durability (load sharing), but expensive to manufacture and more demanding to maintain
- **Note:** These profiles are author-defined heuristic estimates based on engineering design guidelines and expert judgment

**Visual Elements:**
- **Performance profile table:**
  - Rows: Connection types (Press fit, Key, Spline)
  - Columns: Eight application dimensions
  - Values: 0.0 to 1.0 (normalized)
  - Source: Table from methodology (tab:connection_profiles)
- **Optional:** Radar charts for each connection type showing performance across dimensions

**Key Message:**
"Each connection type has a fixed performance profile across eight dimensions. These profiles encode domain knowledge about relative strengths and weaknesses, enabling preference-weighted ranking."

**Transition to next slide:**
"Now let's see how these profiles are combined with user preferences and mechanical capacity to compute the final score..."

---

## SLIDE 3: SCORING FUNCTION COMPONENTS AND FORMULAS

### Purpose
Present the complete scoring function that combines mechanical capacity margin, user preferences, and connection-specific penalties.

### Content Structure

**Part A: Scoring Function Overview**
The scoring function transforms mechanical capacity and user preferences into a single numerical score that enables ranking of feasible connection candidates. It balances multiple competing objectives:
- Mechanical safety margins
- Economic efficiency
- Alignment with user priorities

**User Preference Weights:**
- Users specify preference weights for each dimension (0.0 to 1.0 in 0.1 increments)
- 0.0 = dimension is unimportant
- 1.0 = dimension is critical

**Part B: Scoring Function Components**

The scoring function combines five terms:

**1. Margin Reward Term:**
```
s_margin = w_margin × min(1, (M_t - M_design) / (0.35 × M_design))
```
where:
- w_margin = 0.10 (weight)
- M_t = torque capacity
- M_design = design torque
- **Behavior:**
  - Rewards connections with positive margin up to a cap of 35% above design torque
  - When margin ≤ 35%: reward scales linearly from 0 (at zero margin) to 0.10 (at 35% margin)
  - When margin > 35%: reward saturates at 0.10 (does not increase further)
- **Rationale:** 35% margin reflects engineering practice for static shaft design (utilization levels of 60-80% of material strength are safe and economical). Provides reserve against uncertainties while avoiding overdesign.

**2. Overdesign Penalty Term:**
```
s_overkill = -w_overkill × min(0.5, ((M_t - M_design) / M_design - 0.35)^+)
```
where:
- w_overkill = 0.10 (weight)
- (·)^+ = positive part (max(0, ·))
- **Behavior:**
  - When margin ≤ 35%: penalty = 0 (expression is negative or zero)
  - When margin > 35%: penalty activates and scales with excess margin above 35%
  - Bounded at 0.5 to prevent extreme penalties
- **Rationale:** Penalizes excessive overdesign to avoid unnecessarily large or complex connections when simpler alternatives are adequate. Works in conjunction with margin reward: margins up to 35% are desirable (rewarded), margins beyond 35% are penalized as over-dimensioned.

**3. Preference Utility Term:**
```
s_prefs = w_prefs × (Σ(u_i × p_i)) / (Σ u_i)
```
where:
- w_prefs = 0.70 (largest weight - primary differentiator)
- u_i = user preference weights (8 dimensions)
- p_i = connection profile scores (8 dimensions)
- Denominator normalizes by sum of user weights (ensures utility bounded 0.0-1.0)
- If all weights are zero: denominator defaults to 1.0, system falls back to mechanical criteria alone
- **Rationale:** Quantifies how well a connection type aligns with user priorities. Largest component reflects that user preferences are the primary differentiator when multiple connections are mechanically feasible.

**4. Hub Stiffness Penalty (Press Fits Only):**
```
s_hub_stiffness = w_hub_stiffness × (f_hub - 1.0)
```
where:
- w_hub_stiffness = 0.10 (weight)
- f_hub decreases from 1.0 to 0.1 as Q_A = d/D increases from 0.5 to 0.8
- **Rationale:** When Q_A > 0.5, thin-walled hubs are susceptible to deformation during assembly (bell-mouthing). Penalty discourages press fits in thin hub scenarios.

**5. Spline Practicality Penalty:**
```
s_spline_practicality = -0.2 × max(0, 1.0 - (u_movement + u_bidirectional + u_durability) / 3)
```
where:
- u_movement, u_bidirectional, u_durability = user preference weights for axial movement, bidirectional torque, durability
- **Behavior:**
  - Reaches -0.2 when none of these preferences are valued (user doesn't need spline advantages)
  - Zero when all three are at maximum (user values spline advantages)
- **Rationale:** If user doesn't value spline advantages (axial movement, bidirectional capability, durability), a simpler connection (key) is more appropriate.

**Part C: Composite Score Calculation**
```
s_total = s_margin + s_overkill + s_prefs + s_hub_stiffness + s_spline_practicality
```
- The feasible candidate with the highest composite score becomes the analytical recommendation
- **Score clamping:** Final score is clamped to minimum of -0.15
  - Prevents extreme negative scores from connection-specific penalties from completely eliminating otherwise reasonable candidates
  - Ensures penalized connections remain in consideration if they are the only feasible option or if user preferences strongly favor them

**Part D: Key Design Principles**
- **Transparency:** All intermediate values (capacities, individual score terms, interference diagnostics) are retained in response
- **Interpretability:** Users can understand why a particular connection was recommended and how close alternative options were
- **Balance:** Function balances safety (margin reward), efficiency (overdesign penalty), and user priorities (preference utility)
- **Engineering judgment:** 35% threshold based on engineering practice (Budynas & Nisbett 2020, Kittsteiner 1990)

**Visual Elements:**
- **Scoring function formula:** Show complete equation with all terms
- **Component breakdown table:**
  - Term | Formula | Weight | Purpose
  - Margin reward | s_margin = ... | 0.10 | Reward safety margin up to 35%
  - Overdesign penalty | s_overkill = ... | 0.10 | Penalize excessive overdesign
  - Preference utility | s_prefs = ... | 0.70 | Align with user priorities
  - Hub stiffness | s_hub_stiffness = ... | 0.10 | Penalize thin hubs (press fits)
  - Spline practicality | s_spline_practicality = ... | -0.2 max | Penalize unnecessary splines
- **Optional:** Graph showing margin reward and overdesign penalty behavior vs. margin percentage

**Key Message:**
"Scoring function combines mechanical capacity margin (rewarded up to 35%, penalized beyond), user preferences (70% weight - primary differentiator), and connection-specific penalties. The 35% threshold reflects engineering practice for safe and economical design."

**Transition to next slide:**
"This analytical selector serves as a labeling oracle for synthetic dataset generation..."

---

## PRESENTATION GUIDELINES FOR ANALYTICAL SELECTOR AND SCORING SECTION

### 1. Technical Accuracy - CRITICAL
All formulas and values must match thesis exactly:
- **Design torque:** M_design = M_req × S_R
- **Margin reward:** s_margin = 0.10 × min(1, (M_t - M_design) / (0.35 × M_design))
- **Overdesign penalty:** s_overkill = -0.10 × min(0.5, ((M_t - M_design) / M_design - 0.35)^+)
- **Preference utility:** s_prefs = 0.70 × (Σ(u_i × p_i)) / (Σ u_i)
- **Weights:** w_margin = 0.10, w_overkill = 0.10, w_prefs = 0.70, w_hub_stiffness = 0.10
- **35% threshold:** Based on engineering practice (60-80% utilization of material strength)
- **Score clamping:** Minimum -0.15

### 2. Key Concepts to Emphasize
- **Two-stage process:** Feasibility filtering → Preference-weighted scoring
- **35% margin threshold:** Engineering practice for safe and economical design
- **Preference utility is largest component (0.70):** User priorities are primary differentiator
- **Margin reward and overdesign penalty work together:** Reward up to 35%, penalize beyond
- **Connection-specific penalties:** Address practical considerations (thin hubs, unnecessary splines)

### 3. Visual Strategy
- **Flowchart:** Show two-stage process (feasibility → scoring)
- **Performance profile table:** Show all three connection types across eight dimensions
- **Scoring formula:** Present complete equation with all terms
- **Component breakdown:** Table showing each term, formula, weight, purpose
- **Optional:** Graph showing margin reward/penalty behavior

### 4. Common Mistakes to Avoid
- ❌ Not explaining why 35% threshold is used (engineering practice)
- ❌ Not showing how margin reward and overdesign penalty work together
- ❌ Missing the preference utility weight (0.70 - largest component)
- ❌ Not explaining connection-specific penalties
- ❌ Incorrect formula notation (especially the positive part (·)^+)
- ❌ Not explaining score clamping (-0.15 minimum)

### 5. Speaker Notes Suggestions
- Emphasize that feasibility is prerequisite to scoring
- Explain the 35% threshold rationale (engineering practice, 60-80% utilization)
- Clarify how margin reward and overdesign penalty interact (reward ≤35%, penalize >35%)
- Highlight that preference utility (0.70) is the largest component
- Explain why connection-specific penalties are needed (practical considerations)
- Show how the scoring function balances multiple objectives

---

## YOUR TASK

Create 2-3 PowerPoint slides for the Analytical Selector and Scoring section that:

1. **Present analytical selector process** clearly (feasibility filtering)
2. **Show connection performance profiles** (8 dimensions, 3 connection types)
3. **Present complete scoring function** with all formulas and weights
4. **Explain the 35% threshold** rationale (engineering practice)
5. **Show how components work together** (margin reward + overdesign penalty)
6. **Maintain exact technical accuracy** (all formulas and weights match thesis)
7. **Use clear visualizations** (flowcharts, tables, formulas)
8. **Emphasize key insights** (preference utility is primary differentiator, 35% threshold rationale)

The Analytical Selector and Scoring section should clearly demonstrate:
- How feasible candidates are identified (two-stage filtering)
- How candidates are ranked (preference-weighted scoring)
- Why the scoring function is designed this way (engineering practice, user priorities)
- How all components work together to produce recommendations

Make it suitable for a 20-minute Bachelor thesis defense at Technische Hochschule Ulm, Department of Computer Science.

