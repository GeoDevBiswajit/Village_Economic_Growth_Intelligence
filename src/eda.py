import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from config import *

def generate_eda_plots(df_merged):
    print("Generating EDA charts for presentation slides...")
    
    # 1. Define Features
    features = ['built', 'crops', 'trees', 'nightlight_density', 'total_population']
    change_cols = []
    
    # 2. Calculate changes on the fly specifically for EDA
    for f in features:
        change_col = f'{f}_change'
        change_cols.append(change_col)
        if change_col not in df_merged.columns:
            df_merged[change_col] = df_merged[f'{f}_2025'] - df_merged[f'{f}_2020']
            
    # 3. Correlation Matrix
    plt.figure(figsize=(10, 8))
    corr_matrix = df_merged[change_cols].corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt=".2f", linewidths=.5)
    plt.title('Correlation Matrix of Feature Changes (2020-2025)', fontsize=14)
    
    corr_path = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Correlation_Matrix.png')
    plt.tight_layout()
    plt.savefig(corr_path, dpi=300)
    plt.close()
    
    # 4. Distribution Plot
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'Distribution of Changes (2020 to 2025) across {DISTRICT_NAME} Villages', fontsize=16)
    axes = axes.flatten()

    for i, col in enumerate(change_cols):
        sns.histplot(df_merged[col], kde=True, ax=axes[i], bins=50, color='royalblue')
        axes[i].set_title(f'Distribution of {col}')
        axes[i].axvline(x=0, color='red', linestyle='--') 

    fig.delaxes(axes[5])
    
    dist_path = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Distributions.png')
    plt.tight_layout()
    plt.savefig(dist_path, dpi=300)
    plt.close()

    # 5. Pairwise Scatter Plots for Top Economic Indicators
    economic_indicators = ['built_change', 'nightlight_density_change', 'total_population_change']
    pair_plot = sns.pairplot(df_merged[economic_indicators], kind='reg', corner=True, 
                             plot_kws={'line_kws':{'color':'red'}, 'scatter_kws': {'alpha': 0.5}})
    pair_plot.fig.suptitle('Pairwise Relationships of Key Economic Drivers', y=1.02)
    
    pair_path = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Pair_Plot.png')
    pair_plot.savefig(pair_path, dpi=300)
    plt.close()
    
    print(f"EDA charts (Distributions, Correlations, Pairplot) saved to {RESULTS_DIR} for your presentation deck.")