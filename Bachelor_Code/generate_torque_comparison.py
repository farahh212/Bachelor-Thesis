"""
Generate torque comparison chart for analytical model verification.
Shows predicted torque capacities relative to design torque (required torque × safety factor).
"""

import matplotlib.pyplot as plt
import numpy as np

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-whitegrid')

# Test case parameters
required_torque = 870  # N·m
safety_factor = 2.0
design_torque = required_torque * safety_factor  # 1740 N·m (this is the baseline = 100%)

# Data: Connection type, Torque capacity (N·m)
data = [
    ('Key', 945),
    ('Spline', 6470),
]

# Extract values
connection_types = [d[0] for d in data]
torque_capacities = [d[1] for d in data]

# Calculate percentages (design torque = 100%)
percentages = [(capacity / design_torque) * 100 for capacity in torque_capacities]

# Create figure
fig, ax = plt.subplots(figsize=(8, 5))

# Create bar chart
x_pos = np.arange(len(connection_types))
width = 0.35

# Bars for design torque (100% baseline - required torque × safety factor)
bars1 = ax.bar(x_pos - width/2, [100] * len(connection_types), width, 
               label=f'Design Torque ({design_torque:.0f} N·m)', color='#2E86AB', alpha=0.8, edgecolor='black')

# Bars for torque capacities
bars2 = ax.bar(x_pos + width/2, percentages, width, 
               label='Torque Capacity (Analytical Model)', color='#A23B72', alpha=0.8, edgecolor='black')

# Add value labels on capacity bars
for i, (bar, pct, capacity) in enumerate(zip(bars2, percentages, torque_capacities)):
    # For bars below 100%, show percentage inside bar
    # For bars above 100%, show percentage above bar
    if pct < 100:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            f'{capacity} N·m\n({pct:.1f}%)',
            ha='center',
            va='center',
            fontsize=9,
            fontweight='bold',
            color='white',
        )
    else:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f'{capacity} N·m\n({pct:.1f}%)',
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='bold',
            color='black',
        )

# Customize axes
ax.set_ylabel('Torque [%] (Normalized to Design Torque)', fontsize=11, fontweight='bold')
ax.set_xlabel('Connection Type', fontsize=11, fontweight='bold')
ax.set_title('Torque Capacity vs. Design Torque (Required Torque × Safety Factor)', 
             fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x_pos)
ax.set_xticklabels(connection_types, fontsize=11)
ax.set_ylim([0, max(max(percentages) * 1.15, 120)])
ax.axhline(y=100, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Feasibility Threshold (100%)')
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3, linestyle='--', axis='y')

# Add feasibility annotation
for i, (pct, conn_type) in enumerate(zip(percentages, connection_types)):
    if pct < 100:
        ax.text(i, pct + 5, 'Not Feasible', ha='center', va='bottom', 
                fontsize=9, fontweight='bold', color='red', style='italic')
    else:
        ax.text(i, 100 + 5, 'Feasible', ha='center', va='bottom', 
                fontsize=9, fontweight='bold', color='green', style='italic')

plt.tight_layout()
plt.savefig('../thesis/figures/torque_comparison_chart.png', dpi=300, bbox_inches='tight')
print("Torque comparison chart saved to thesis/figures/torque_comparison_chart.png")
plt.close()

