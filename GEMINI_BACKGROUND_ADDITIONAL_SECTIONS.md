# Additional Background Sections for PowerPoint Presentation

This document contains the missing background sections that must be included in the Background section of the presentation: Feasibility Considerations, Preference-Based Trade-Offs, Evaluation Metrics (including Confusion Matrix), and State of the Art.

---

## SLIDE 5: FEASIBILITY CONSIDERATIONS AND PREFERENCE-BASED TRADE-OFFS

### Purpose
Explain how feasibility is established and how user preferences influence selection beyond pure mechanical capacity.

### Content Structure

**Part A: Feasibility Considerations**
- **Basic requirement:** Connection must transmit required torque with appropriate safety margin
- **Mechanical feasibility:**
  - Torque capacity ≥ design torque (M_req × S_R)
  - Within admissible material limits (yield strength, ultimate strength)
  - Within geometric limits (diameter ratios, wall thickness)
- **Practical feasibility:**
  - Avoid non-physical designs (invalid diameter relationships)
  - Avoid unrealistically difficult assembly (e.g., excessive interference)
  - Press fits: Interference limits (typically U_w ≤ 0.020mm for manufacturability)
- **Key point:** "Feasibility serves as prerequisite to preference-based evaluation. Only feasible connections are considered for selection."

**Part B: Preference-Based Engineering Trade-Offs**
- **Problem:** Engineering decisions involve trade-offs beyond torque capacity alone
- **Eight preference dimensions:**
  1. Assembly and disassembly ease
  2. Suitability for axial movement
  3. Cost sensitivity
  4. Bidirectional torque capability
  5. Vibration resistance
  6. High-speed suitability
  7. Maintenance effort and accessibility
  8. Durability and fatigue-related considerations

**Part C: Why Preferences Matter**
- Different connection types exhibit characteristic strengths and weaknesses across these dimensions
- Example trade-offs:
  - Press fits: Excellent concentricity, but difficult disassembly
  - Keys: Low cost, easy assembly, but stress concentrations
  - Splines: High capacity, but high manufacturing cost
- **User-defined preference weighting:** Enables selection decisions that reflect application-specific priorities
- **Key point:** "Selection should not rely solely on mechanical capacity. User preferences enable context-aware decisions."

**Visual Elements:**
- **Comparison table (optional):** Show how each connection type performs across the 8 preference dimensions
- **Simple diagram:** Feasibility filter → Preference scoring → Selection

**Key Message:**
"Feasibility ensures mechanical safety, but preferences enable application-specific optimization. Both are essential for intelligent selection."

**Transition to next slide:**
"Now let's understand how machine learning fits into this framework and how we evaluate model performance..."

---

## SLIDE 6: MACHINE LEARNING CONCEPTS AND EVALUATION METRICS

### Purpose
Explain machine learning fundamentals, tree-based models, and evaluation metrics used in this thesis.

### Content Structure

**Part A: What is Machine Learning?**
- Definition: Enables computers to learn patterns from data without explicit programming
- **Role in this thesis:** Complements analytical models by learning subtle patterns and trade-offs difficult to encode explicitly
- **Analytical models:** Provide physically grounded calculations
- **ML models:** Capture complex interactions between multiple factors (geometry, materials, preferences)

**Part B: Supervised Classification**
- **Training process:**
  - Input features: Geometric parameters, materials, preferences
  - Target label: Connection type (determined by analytical scoring system)
  - Dataset split: Training (70-80%), Validation (10-15%), Test (10-20%)
  - Validation: Hyperparameter tuning
  - Test: Unbiased performance estimate
- **Overfitting prevention:** Regularization, early stopping, cross-validation

**Part C: Tree-Based Models**
- **Why tree-based?**
  - Represent nonlinear decision boundaries (mechanical feasibility constraints)
  - Handle mixed data types (numerical + categorical)
  - Well-suited for engineering problems

**Key Models:**
- **Decision Trees:** Hierarchical yes/no questions, but prone to overfitting
- **Random Forest:** Bagging (bootstrap aggregating), many independent trees vote
- **Gradient Boosting:** Sequential training, each tree corrects previous errors
  - **XGBoost:** Regularization, second-order optimization
  - **LightGBM:** Histogram-based, leaf-wise growth
  - **CatBoost:** Robust categorical handling, ordered boosting

**Part D: Evaluation Metrics**
- **Classification outcomes:**
  - True Positives (TP): Correctly predicted class
  - False Positives (FP): Incorrectly predicted as class
  - True Negatives (TN): Correctly predicted different class
  - False Negatives (FN): Missed instances of class

**Key Metrics:**
1. **Accuracy:** Overall percentage correct
   - Accuracy = (TP + TN) / (TP + FP + TN + FN)
   - Limitation: Misleading with imbalanced classes

2. **Precision:** Reliability of predictions
   - Precision = TP / (TP + FP)
   - "Of all predicted as class, how many were actually that class?"

3. **Recall (Sensitivity):** How well model finds all instances
   - Recall = TP / (TP + FN)
   - "Of all actual instances, how many were correctly identified?"

4. **F1-Score:** Harmonic mean of precision and recall
   - F1 = 2 × (Precision × Recall) / (Precision + Recall)
   - Balances precision and recall

5. **Macro F1-Score:** Average F1 across all classes
   - Macro F1 = (1/C) × Σ F1_i
   - Ensures all classes weighted equally
   - **Used for model selection in this thesis** (avoids favoring dominant classes)

**Part E: Confusion Matrix**
- **Purpose:** Detailed breakdown of classification performance
- **Structure:** 3×3 table (for 3-class problem: press fit, key, spline)
  - Rows: True classes
  - Columns: Predicted classes
  - Diagonal: Correct predictions (TP for each class)
  - Off-diagonal: Misclassifications (which classes are confused)
- **Use:** Qualitative error analysis, identify systematic misclassification patterns
- **Example:** "Do keys get confused with splines? Do press fits get confused with keys?"

**Visual Elements:**
- **Confusion matrix diagram (figures/conf-matrix3x3.png):**
  - Shows 3×3 structure for three-class problem
  - Illustrates how predictions are distributed
  - Source: researchgate_confusion_matrix_2021
- **Optional:** Simple diagram showing precision vs recall trade-off

**Key Message:**
"Macro F1-score ensures balanced performance across all classes. Confusion matrix reveals which connection types are most easily confused, enabling targeted improvements."

**Transition to next slide:**
"Let's examine the state of the art in engineering design automation to understand where this work fits..."

---

## SLIDE 7: STATE OF THE ART IN ENGINEERING DESIGN AUTOMATION

### Purpose
Contextualize the thesis contribution within the broader landscape of engineering design automation.

### Content Structure

**Part A: Evolution of Design Automation**
- **Traditional approach:**
  - Analytical calculations from first principles
  - Standardized design codes (DIN standards)
  - Transparent, physically grounded
  - **Limitation:** Requires expert knowledge, manual iteration, time-consuming
- **For shaft-hub connections:** Engineers consult handbook charts, perform iterative calculations, rely on experience
- **Problem:** Doesn't scale to rapid design exploration or automated optimization

**Part B: Early Automation Attempts**
- **Rule-based expert systems:**
  - Encode expert knowledge as explicit if-then rules
  - Consistent application of design logic
  - **Limitations:**
    - Brittleness (can't handle cases outside predefined rules)
    - Extensive maintenance as knowledge evolves
    - Struggle with multi-criteria trade-offs

**Part C: Machine Learning Promise and Challenge**
- **Promise:** Learn patterns directly from data, capture complex nonlinear relationships
- **Challenge:** Requires large, labeled datasets
- **Data sources:**
  - Experiments: Expensive and time-consuming
  - Historical design databases: Proprietary, not publicly accessible
  - Simulations: Require computational resources
- **Reality:** "At the moment, this work does not have access to these proprietary datasets."

**Part D: Hybrid Approaches**
- **Physics-informed machine learning:**
  - Incorporates domain knowledge into model architectures
  - Ensures predictions respect physical constraints
  - Examples: Raissi et al. 2019, Karniadakis et al. 2021
- **Surrogate modeling:**
  - ML approximates expensive simulations
  - Enables rapid design exploration
- **Limitation:** Most hybrid approaches still require some form of training data (simulations or experiments)

**Part E: Synthetic Data Generation**
- **Concept:** Use analytical models or simulations as "labeling oracles"
- **Advantage:** Generate large datasets reflecting engineering knowledge encoded in standards
- **Benefit:** Bridges gap between rule-based systems and data-driven methods
- **Result:** Enables machine learning while maintaining physical consistency

**Part F: This Thesis Contribution**
- **Problem context:** Shaft-hub connection selection sits at intersection of:
  - Multiple competing criteria
  - Mechanical constraints
  - Interpretable recommendations
  - Data-scarce environment
- **Solution approach:**
  1. Generate synthetic data from analytical models
  2. Train machine-learning classifiers on this data
  3. Integrate both components into unified decision-support system
- **Related work:**
  - Saeed et al. 2023: AI techniques for shrink-fit couplings
  - Massoud 2025: Previous bachelor thesis using XGBoost and Random Forest
  - **This work:** Builds upon and extends previous work with preference-weighted scoring and enhanced model selection

**Visual Elements:**
- **System architecture diagram (figures/system_architecture.png):**
  - Shows: React frontend → FastAPI backend → Analytical engine + ML pipeline
  - Offline dataset generation module
  - Material database
  - Source: own illustration
- **Optional:** Timeline or evolution diagram showing progression from rule-based → ML → hybrid approaches

**Key Message:**
"Synthetic data generation from analytical models enables machine learning in data-scarce domains. This thesis demonstrates a complete framework combining analytical rigor with ML efficiency for shaft-hub connection selection."

**Transition to next slide:**
"With this background established, we can now present our methodology for building the hybrid system..."

---

## KEY POINTS TO REMEMBER

### Feasibility Considerations
- Mechanical feasibility: Torque capacity ≥ design torque, within material/geometric limits
- Practical feasibility: Avoid non-physical designs, assembly constraints (e.g., interference limits)
- Serves as prerequisite to preference-based evaluation

### Preference-Based Trade-Offs
- 8 dimensions: Assembly/disassembly, axial movement, cost, bidirectional torque, vibration, high-speed, maintenance, durability
- Enables application-specific optimization beyond pure mechanical capacity
- Different connection types have characteristic strengths/weaknesses across dimensions

### Evaluation Metrics
- Accuracy: Overall percentage correct (but misleading with imbalanced classes)
- Precision: Reliability of predictions (TP / (TP + FP))
- Recall: How well model finds all instances (TP / (TP + FN))
- F1-Score: Harmonic mean of precision and recall
- **Macro F1-Score:** Average F1 across all classes - **USED FOR MODEL SELECTION** (ensures balanced performance)
- Confusion Matrix: 3×3 table showing true vs predicted classes, enables error analysis

### State of the Art
- Evolution: Traditional → Rule-based → ML → Hybrid approaches
- Data scarcity challenge: No publicly available labeled datasets
- Synthetic data generation solution: Use analytical models as labeling oracles
- This thesis: Complete framework combining analytical rigor with ML efficiency

---

## VISUAL REQUIREMENTS

### Slide 5 (Feasibility & Preferences)
- Optional comparison table showing connection types across 8 preference dimensions
- Simple flowchart: Feasibility filter → Preference scoring → Selection

### Slide 6 (ML & Evaluation Metrics)
- **Essential:** Confusion matrix diagram (figures/conf-matrix3x3.png)
- Optional: Precision vs recall trade-off diagram
- Optional: Tree-based model comparison table

### Slide 7 (State of the Art)
- **Essential:** System architecture diagram (figures/system_architecture.png)
- Optional: Evolution timeline diagram

---

## INTEGRATION NOTES

These slides should be inserted into the Background section as follows:
- **After Slide 4** (DIN Standards and Material Considerations): Insert Slide 5 (Feasibility & Preferences)
- **After Slide 5** (Feasibility & Preferences): Insert Slide 6 (ML Concepts & Evaluation Metrics)
- **After Slide 6** (ML Concepts & Evaluation Metrics): Insert Slide 7 (State of the Art)
- **Before Methodology section:** These background slides prepare the audience to understand the methodology

The total Background section should now be **7-8 slides** (7-8 minutes) instead of 4-5 slides.

