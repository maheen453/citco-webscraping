import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

# Store citation_pubs.csv into dataframes sorted in ascending order of publication counts
df = pd.read_csv('citation_pubs.csv', quotechar='"', on_bad_lines='skip', engine='python')

def remove_outliers(df, column):
    """Removes outliers from dataset --> values below Q1-1.5*IQR or above Q3+1.5*IQR"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    df_filtered = df[(df[column] >= (Q1 - 1.5*IQR)) & (df[column] <= (Q3 + 1.5*IQR))]
    return df_filtered

# Filtered dataframes to eliminate outliers
df_filt_pub = remove_outliers(df, 'Publications_6Yrs')
df_filt_cit = remove_outliers(df, 'Citations_6Yrs')

# Create subplots for graphs
fig, axs = plt.subplots(2, 1, figsize=(12,7))

# Plotting pub_count vs dg_amount
axs[0].scatter(df_filt_pub['Publications_6Yrs'], df_filt_pub['DG_Amount'], marker='o', color='blue')
axs[0].set_title('Publication Count vs DG Value (Outliers Removed)')
axs[0].set_xlabel('Publication Count (Last 6 Years)')
axs[0].set_ylabel('DG Value ($)')
axs[0].grid(True)

# Calculate linear regression for LOBF - publication count
slope, intercept, r_val, p_val, std_err = linregress(df_filt_pub['Publications_6Yrs'], df_filt_pub['DG_Amount'])
r_sqrd = r_val ** 2
equation = f'y = {slope:.2f}x + {intercept:.2f}'
axs[0].plot(df_filt_pub['Publications_6Yrs'], slope * df_filt_pub['Publications_6Yrs'] + intercept, color='black', linestyle='--')
axs[0].text(0.98, 0.98, f'R² = {r_sqrd:.2f}', transform=axs[0].transAxes, fontsize=12, verticalalignment='top')
axs[0].text(0.98, 0.90, equation, transform=axs[0].transAxes, fontsize=12, verticalalignment='top')

# Plotting cit_count vs dg_amount
axs[1].scatter(df_filt_cit['Citations_6Yrs'], df_filt_cit['DG_Amount'], marker='o', color='red')
axs[1].set_title('Citation Count vs DG Value (Outliers Removed)')
axs[1].set_xlabel('Citation Count (Last 6 Years)')
axs[1].set_ylabel('DG Value ($)')
axs[1].grid(True)

# Calculate linear regression for LOBF - citation count
slope, intercept, r_val, p_val, std_err = linregress(df_filt_cit['Citations_6Yrs'], df_filt_cit['DG_Amount'])
r_sqrd = r_val ** 2
equation = f'y = {slope:.2f}x + {intercept:.2f}'
axs[1].plot(df_filt_cit['Citations_6Yrs'], slope * df_filt_cit['Citations_6Yrs'] + intercept, color='black', linestyle='--')
axs[1].text(0.98, 0.98, f'R² = {r_sqrd:.2f}', transform=axs[1].transAxes, fontsize=12, verticalalignment='top')
axs[1].text(0.98, 0.90, equation, transform=axs[1].transAxes, fontsize=12, verticalalignment='top')

plt.tight_layout()
plt.show()

