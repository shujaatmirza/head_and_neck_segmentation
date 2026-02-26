"""
Comprehensive Analysis & Visualization for Head and Neck Segmentation Project.

Generates:
1. Summary bar chart of best Dice scores across ALL experiments
2. Loss function comparison plot (previously missing)
3. Multi-panel figure combining all experiment categories
4. LaTeX-formatted summary table
5. Improved individual plots with consistent styling
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# ─── Configuration ───────────────────────────────────────────────────────────
CSV_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(CSV_DIR, "plots", "summary")
os.makedirs(SAVE_DIR, exist_ok=True)

# Consistent plot style
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# Color palettes
COLORS_5 = ['#2196F3', '#FF5722', '#4CAF50', '#9C27B0', '#FF9800']
COLORS_4 = ['#2196F3', '#FF5722', '#4CAF50', '#9C27B0']
COLORS_3 = ['#2196F3', '#FF5722', '#4CAF50']
COLORS_2 = ['#2196F3', '#FF5722']

PRETTY_NAMES = {
    'no_aug': 'No Augmentation',
    'rand_affine': 'Random Affine',
    'rand_elastic': 'Random Elastic',
    'rand_spatial_crop': 'Random Spatial Crop',
    'rand_zoom': 'Random Zoom',
    '1_gpu': '1 GPU',
    '2_gpu': '2 GPUs',
    '4_gpu': '4 GPUs',
    'normal_unet': 'UNet',
    'deeper_unet': 'Deeper UNet',
    'segresnet': 'SegResNet',
    'no_pretrain': 'No Pretraining',
    'pretrain': 'With Pretraining',
    'crop1': 'Crop 1 (1.4x)',
    'crop2': 'Crop 2 (1.2x)',
    'crop3': 'Crop 3 (1.0x)',
    'crop4': 'Crop 4 (0.8x)',
}

# ─── Helper Functions ────────────────────────────────────────────────────────

def load_csv(prefix, name):
    """Load a CSV file and return a DataFrame."""
    path = os.path.join(CSV_DIR, f"{prefix}{name}.csv")
    return pd.read_csv(path)


def get_best_score(prefix, name):
    """Get best (max) Dice score from a CSV file."""
    df = load_csv(prefix, name)
    return df["Value"].max()


def get_best_epoch(prefix, name):
    """Get epoch at which best Dice score was achieved."""
    df = load_csv(prefix, name)
    idx = df["Value"].idxmax()
    return int(df.loc[idx, "Step"])


def pretty(name):
    """Get display-friendly name."""
    return PRETTY_NAMES.get(name, name)


# ─── 1. Summary Bar Chart: Best Scores Across ALL Experiments ────────────────

def plot_summary_bar_chart():
    """Create a comprehensive bar chart showing peak Dice scores for every experiment."""
    experiments = {
        'Augmentation': {
            'prefix': 'aug_exp_',
            'names': ['no_aug', 'rand_affine', 'rand_elastic', 'rand_spatial_crop', 'rand_zoom'],
        },
        'Delayed Aug.': {
            'prefix': 'aug_delayed_exp_',
            'names': ['no_aug', 'rand_affine', 'rand_elastic', 'rand_spatial_crop', 'rand_zoom'],
        },
        'Model': {
            'prefix': 'model_exp_',
            'names': ['normal_unet', 'deeper_unet', 'segresnet'],
        },
        'Data Parallel': {
            'prefix': 'distributed_exp_',
            'names': ['1_gpu', '2_gpu', '4_gpu'],
        },
        'Batch Size\n(LR Scale)': {
            'prefix': 'effective_bsz_exp_',
            'names': ['2', '4', '8', '16'],
        },
        'Batch Size\n(No LR Scale)': {
            'prefix': 'effective_bsz_no_lr_scaling_v2_exp_',
            'names': ['2', '4', '8', '16'],
        },
        'Input Resize': {
            'prefix': 'resize_vs_performance_exp_',
            'names': ['crop1', 'crop2', 'crop3', 'crop4'],
        },
        'SSL Pretrain': {
            'prefix': 'ssl_exp_',
            'names': ['no_pretrain', 'pretrain'],
        },
    }

    fig, ax = plt.subplots(figsize=(16, 6))

    all_labels = []
    all_scores = []
    all_colors = []
    group_positions = []
    group_labels = []
    pos = 0

    color_cycle = plt.cm.Set2(np.linspace(0, 1, len(experiments)))

    for gi, (group_name, group) in enumerate(experiments.items()):
        start_pos = pos
        for name in group['names']:
            score = get_best_score(group['prefix'], name)
            label = pretty(name) if name in PRETTY_NAMES else f"BSZ {name}"
            all_labels.append(label)
            all_scores.append(score)
            all_colors.append(color_cycle[gi])
            pos += 1
        end_pos = pos - 1
        group_positions.append((start_pos + end_pos) / 2)
        group_labels.append(group_name)
        pos += 1  # gap between groups

    x = np.arange(len(all_scores))
    # Adjust x positions with gaps
    adjusted_x = []
    gap_count = 0
    for gi, (group_name, group) in enumerate(experiments.items()):
        for _ in group['names']:
            adjusted_x.append(len(adjusted_x) + gap_count)
        gap_count += 1
    adjusted_x = np.array(adjusted_x)

    bars = ax.bar(adjusted_x, all_scores, color=all_colors, edgecolor='white', width=0.8)

    # Add value labels on top of bars
    for bar, score in zip(bars, all_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f'{score:.3f}', ha='center', va='bottom', fontsize=7, fontweight='bold')

    ax.set_xticks(adjusted_x)
    ax.set_xticklabels(all_labels, rotation=45, ha='right', fontsize=7)
    ax.set_ylabel('Best Mean Dice Score')
    ax.set_title('Peak Performance Across All Experiments', fontweight='bold', fontsize=14)
    ax.set_ylim(0, 0.85)

    # Add group labels
    # Recalculate group_positions with gaps
    gap_count = 0
    for gi, (group_name, group) in enumerate(experiments.items()):
        start = sum(len(experiments[g]['names']) for g in list(experiments.keys())[:gi]) + gi
        end = start + len(group['names']) - 1
        mid = (start + end) / 2
        ax.annotate(group_name, xy=(mid, -0.18), xycoords=('data', 'axes fraction'),
                    ha='center', va='top', fontsize=8, fontweight='bold',
                    color=color_cycle[gi])

    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, "summary_best_scores.png"))
    plt.savefig(os.path.join(SAVE_DIR, "summary_best_scores.pdf"))
    plt.close()
    print("[1/5] Summary bar chart saved.")


# ─── 2. Loss Function Comparison (from report data) ─────────────────────────

def plot_loss_function_comparison():
    """Bar chart of loss function results (from report Table 1)."""
    # These are from the project report - loss function experiments
    loss_functions = [
        'Dice CE\nLoss', 'Dice\nLoss', 'Dice Focal\nLoss', 'Masked\nDice Loss',
        'Tversky\nLoss', 'Focal\nLoss', 'Generalized\nDice Loss'
    ]
    scores = [0.737, 0.701, 0.695, 0.680, 0.634, 0.632, 0.250]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(scores)))
    # Sort by score for color mapping
    sorted_indices = np.argsort(scores)[::-1]
    bar_colors = ['#4CAF50' if i == sorted_indices[0] else '#2196F3' for i in range(len(scores))]

    bars = ax.bar(loss_functions, scores, color=bar_colors, edgecolor='white', width=0.6)

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f'{score:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('Mean Dice Score')
    ax.set_title('Loss Function Comparison', fontweight='bold')
    ax.set_ylim(0, 0.85)
    ax.axhline(y=0.737, color='#4CAF50', linestyle='--', alpha=0.4, label='Best (Dice CE)')
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, "loss_function_comparison.png"))
    plt.savefig(os.path.join(SAVE_DIR, "loss_function_comparison.pdf"))
    plt.close()
    print("[2/5] Loss function comparison saved.")


# ─── 3. Multi-Panel Figure ──────────────────────────────────────────────────

def plot_multipanel():
    """Create a 2x4 multi-panel figure summarizing all experiment categories."""
    fig = plt.figure(figsize=(18, 10))
    gs = gridspec.GridSpec(2, 4, hspace=0.35, wspace=0.3)

    # Panel 1: Augmentation
    ax1 = fig.add_subplot(gs[0, 0])
    prefix = 'aug_exp_'
    names = ['no_aug', 'rand_affine', 'rand_elastic', 'rand_spatial_crop', 'rand_zoom']
    for i, name in enumerate(names):
        df = load_csv(prefix, name)
        ax1.plot(df['Step'], df['Value'], label=pretty(name), color=COLORS_5[i], linewidth=1.5)
    ax1.set_title('(a) Augmentation', fontweight='bold')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Mean Dice Score')
    ax1.legend(fontsize=7)

    # Panel 2: Delayed Augmentation
    ax2 = fig.add_subplot(gs[0, 1])
    prefix = 'aug_delayed_exp_'
    for i, name in enumerate(names):
        df = load_csv(prefix, name)
        ax2.plot(df['Step'], df['Value'], label=pretty(name), color=COLORS_5[i], linewidth=1.5)
    ax2.set_title('(b) Delayed Augmentation', fontweight='bold')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Mean Dice Score')
    ax2.legend(fontsize=7)

    # Panel 3: Model Architectures
    ax3 = fig.add_subplot(gs[0, 2])
    prefix = 'model_exp_'
    model_names = ['normal_unet', 'deeper_unet', 'segresnet']
    for i, name in enumerate(model_names):
        df = load_csv(prefix, name)
        ax3.plot(df['Step'], df['Value'], label=pretty(name), color=COLORS_3[i], linewidth=1.5)
    ax3.set_title('(c) Model Architectures', fontweight='bold')
    ax3.set_xlabel('Epoch')
    ax3.set_ylabel('Mean Dice Score')
    ax3.legend(fontsize=7)

    # Panel 4: Data Parallelism
    ax4 = fig.add_subplot(gs[0, 3])
    prefix = 'distributed_exp_'
    gpu_names = ['1_gpu', '2_gpu', '4_gpu']
    for i, name in enumerate(gpu_names):
        df = load_csv(prefix, name)
        ax4.plot(df['Step'], df['Value'], label=pretty(name), color=COLORS_3[i], linewidth=1.5)
    ax4.set_title('(d) Data Parallelism', fontweight='bold')
    ax4.set_xlabel('Epoch')
    ax4.set_ylabel('Mean Dice Score')
    ax4.legend(fontsize=7)

    # Panel 5: Effective Batch Size (LR Scaling)
    ax5 = fig.add_subplot(gs[1, 0])
    prefix = 'effective_bsz_exp_'
    bsz_names = ['2', '4', '8', '16']
    for i, name in enumerate(bsz_names):
        df = load_csv(prefix, name)
        ax5.plot(df['Step'], df['Value'], label=f'BSZ {name}', color=COLORS_4[i], linewidth=1.5)
    ax5.set_title('(e) Eff. Batch Size (LR Scale)', fontweight='bold')
    ax5.set_xlabel('Epoch')
    ax5.set_ylabel('Mean Dice Score')
    ax5.legend(fontsize=7)

    # Panel 6: Effective Batch Size (No LR Scaling)
    ax6 = fig.add_subplot(gs[1, 1])
    prefix = 'effective_bsz_no_lr_scaling_v2_exp_'
    for i, name in enumerate(bsz_names):
        df = load_csv(prefix, name)
        ax6.plot(df['Step'], df['Value'], label=f'BSZ {name}', color=COLORS_4[i], linewidth=1.5)
    ax6.set_title('(f) Eff. Batch Size (No LR Scale)', fontweight='bold')
    ax6.set_xlabel('Epoch')
    ax6.set_ylabel('Mean Dice Score')
    ax6.legend(fontsize=7)

    # Panel 7: Input Resize
    ax7 = fig.add_subplot(gs[1, 2])
    prefix = 'resize_vs_performance_exp_'
    crop_names = ['crop1', 'crop2', 'crop3', 'crop4']
    for i, name in enumerate(crop_names):
        df = load_csv(prefix, name)
        ax7.plot(df['Step'], df['Value'], label=pretty(name), color=COLORS_4[i], linewidth=1.5)
    ax7.set_title('(g) Input Resolution', fontweight='bold')
    ax7.set_xlabel('Epoch')
    ax7.set_ylabel('Mean Dice Score')
    ax7.legend(fontsize=7)

    # Panel 8: SSL Pretraining
    ax8 = fig.add_subplot(gs[1, 3])
    prefix = 'ssl_exp_'
    ssl_names = ['no_pretrain', 'pretrain']
    for i, name in enumerate(ssl_names):
        df = load_csv(prefix, name)
        ax8.plot(df['Step'], df['Value'], label=pretty(name), color=COLORS_2[i], linewidth=1.5)
    ax8.set_title('(h) Self-Supervised Pretraining', fontweight='bold')
    ax8.set_xlabel('Epoch')
    ax8.set_ylabel('Mean Dice Score')
    ax8.legend(fontsize=7)

    fig.suptitle('Multi-Organ Head & Neck Segmentation: Comprehensive Experiment Overview',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.savefig(os.path.join(SAVE_DIR, "multipanel_all_experiments.png"))
    plt.savefig(os.path.join(SAVE_DIR, "multipanel_all_experiments.pdf"))
    plt.close()
    print("[3/5] Multi-panel figure saved.")


# ─── 4. LaTeX Summary Table ─────────────────────────────────────────────────

def generate_latex_table():
    """Generate a LaTeX-formatted summary table of all experiments."""
    rows = []

    # Augmentation
    for name in ['no_aug', 'rand_affine', 'rand_elastic', 'rand_spatial_crop', 'rand_zoom']:
        score = get_best_score('aug_exp_', name)
        epoch = get_best_epoch('aug_exp_', name)
        rows.append(('Augmentation', pretty(name), f'{score:.4f}', str(epoch)))

    # Delayed Augmentation
    for name in ['no_aug', 'rand_affine', 'rand_elastic', 'rand_spatial_crop', 'rand_zoom']:
        score = get_best_score('aug_delayed_exp_', name)
        epoch = get_best_epoch('aug_delayed_exp_', name)
        rows.append(('Delayed Augmentation', pretty(name), f'{score:.4f}', str(epoch)))

    # Models
    for name in ['normal_unet', 'deeper_unet', 'segresnet']:
        score = get_best_score('model_exp_', name)
        epoch = get_best_epoch('model_exp_', name)
        rows.append(('Model Architecture', pretty(name), f'{score:.4f}', str(epoch)))

    # Data Parallelism
    for name in ['1_gpu', '2_gpu', '4_gpu']:
        score = get_best_score('distributed_exp_', name)
        epoch = get_best_epoch('distributed_exp_', name)
        rows.append(('Data Parallelism', pretty(name), f'{score:.4f}', str(epoch)))

    # Effective Batch Size (LR Scaling)
    for name in ['2', '4', '8', '16']:
        score = get_best_score('effective_bsz_exp_', name)
        epoch = get_best_epoch('effective_bsz_exp_', name)
        rows.append(('Eff. BSZ (LR Scale)', f'Batch Size {name}', f'{score:.4f}', str(epoch)))

    # Effective Batch Size (No LR Scaling)
    for name in ['2', '4', '8', '16']:
        score = get_best_score('effective_bsz_no_lr_scaling_v2_exp_', name)
        epoch = get_best_epoch('effective_bsz_no_lr_scaling_v2_exp_', name)
        rows.append(('Eff. BSZ (No LR Scale)', f'Batch Size {name}', f'{score:.4f}', str(epoch)))

    # Input Resize
    for name in ['crop1', 'crop2', 'crop3', 'crop4']:
        score = get_best_score('resize_vs_performance_exp_', name)
        epoch = get_best_epoch('resize_vs_performance_exp_', name)
        rows.append(('Input Resolution', pretty(name), f'{score:.4f}', str(epoch)))

    # SSL
    for name in ['no_pretrain', 'pretrain']:
        score = get_best_score('ssl_exp_', name)
        epoch = get_best_epoch('ssl_exp_', name)
        rows.append(('SSL Pretraining', pretty(name), f'{score:.4f}', str(epoch)))

    # Write LaTeX table
    latex_lines = []
    latex_lines.append(r"\begin{table}[htbp]")
    latex_lines.append(r"\centering")
    latex_lines.append(r"\caption{Summary of all experimental results. Best Dice score per category shown in \textbf{bold}.}")
    latex_lines.append(r"\label{tab:summary}")
    latex_lines.append(r"\small")
    latex_lines.append(r"\begin{tabular}{llcc}")
    latex_lines.append(r"\toprule")
    latex_lines.append(r"\textbf{Category} & \textbf{Configuration} & \textbf{Best Dice} & \textbf{Best Epoch} \\")
    latex_lines.append(r"\midrule")

    # Group rows by category and bold the best in each
    current_category = None
    category_rows = []
    all_categories = []

    for row in rows:
        if row[0] != current_category:
            if category_rows:
                all_categories.append((current_category, category_rows))
            current_category = row[0]
            category_rows = [row]
        else:
            category_rows.append(row)
    if category_rows:
        all_categories.append((current_category, category_rows))

    for cat_name, cat_rows in all_categories:
        best_score = max(float(r[2]) for r in cat_rows)
        for i, row in enumerate(cat_rows):
            cat_display = cat_name if i == 0 else ''
            score_str = r'\textbf{' + row[2] + '}' if float(row[2]) == best_score else row[2]
            latex_lines.append(f"{cat_display} & {row[1]} & {score_str} & {row[3]} \\\\")
        latex_lines.append(r"\midrule")

    # Remove last midrule and add bottomrule
    latex_lines[-1] = r"\bottomrule"
    latex_lines.append(r"\end{tabular}")
    latex_lines.append(r"\end{table}")

    latex_output = '\n'.join(latex_lines)

    # Save to file
    table_path = os.path.join(SAVE_DIR, "summary_table.tex")
    with open(table_path, 'w') as f:
        f.write(latex_output)

    # Also print plaintext table
    print("\n" + "=" * 80)
    print("SUMMARY TABLE: Best Mean Dice Scores Across All Experiments")
    print("=" * 80)
    print(f"{'Category':<25} {'Configuration':<25} {'Best Dice':<12} {'Best Epoch':<10}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:<25} {row[1]:<25} {row[2]:<12} {row[3]:<10}")
    print("=" * 80)

    print(f"\n[4/5] LaTeX summary table saved to {table_path}")
    return latex_output


# ─── 5. Best Configuration Comparison ───────────────────────────────────────

def plot_best_per_category():
    """Bar chart showing only the best experiment from each category."""
    categories = {
        'Augmentation': ('aug_exp_', ['no_aug', 'rand_affine', 'rand_elastic', 'rand_spatial_crop', 'rand_zoom']),
        'Delayed\nAug.': ('aug_delayed_exp_', ['no_aug', 'rand_affine', 'rand_elastic', 'rand_spatial_crop', 'rand_zoom']),
        'Model\nArch.': ('model_exp_', ['normal_unet', 'deeper_unet', 'segresnet']),
        'Data\nParallel': ('distributed_exp_', ['1_gpu', '2_gpu', '4_gpu']),
        'BSZ\n(LR)': ('effective_bsz_exp_', ['2', '4', '8', '16']),
        'BSZ\n(No LR)': ('effective_bsz_no_lr_scaling_v2_exp_', ['2', '4', '8', '16']),
        'Input\nResize': ('resize_vs_performance_exp_', ['crop1', 'crop2', 'crop3', 'crop4']),
        'SSL': ('ssl_exp_', ['no_pretrain', 'pretrain']),
    }

    cat_labels = []
    best_scores = []
    best_configs = []

    for cat_name, (prefix, names) in categories.items():
        scores = [(name, get_best_score(prefix, name)) for name in names]
        best_name, best_score = max(scores, key=lambda x: x[1])
        cat_labels.append(cat_name)
        best_scores.append(best_score)
        config_label = pretty(best_name) if best_name in PRETTY_NAMES else f'BSZ {best_name}'
        best_configs.append(config_label)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.Set2(np.linspace(0, 1, len(cat_labels)))
    bars = ax.bar(cat_labels, best_scores, color=colors, edgecolor='white', width=0.6)

    for bar, score, config in zip(bars, best_scores, best_configs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f'{score:.3f}\n({config})', ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_ylabel('Best Mean Dice Score')
    ax.set_title('Best Configuration Per Experiment Category', fontweight='bold')
    ax.set_ylim(0, 0.88)

    # Add loss function result as reference line
    ax.axhline(y=0.737, color='red', linestyle='--', alpha=0.5, label='Best Overall (Dice CE Loss): 0.737')
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, "best_per_category.png"))
    plt.savefig(os.path.join(SAVE_DIR, "best_per_category.pdf"))
    plt.close()
    print("[5/5] Best-per-category chart saved.")


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating comprehensive analysis...")
    print(f"Output directory: {SAVE_DIR}\n")

    plot_summary_bar_chart()
    plot_loss_function_comparison()
    plot_multipanel()
    latex_table = generate_latex_table()
    plot_best_per_category()

    print(f"\nAll outputs saved to: {SAVE_DIR}")
    print("Files generated:")
    print("  - summary_best_scores.png/pdf")
    print("  - loss_function_comparison.png/pdf")
    print("  - multipanel_all_experiments.png/pdf")
    print("  - summary_table.tex")
    print("  - best_per_category.png/pdf")
