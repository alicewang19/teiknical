"""Streamlit dashboard that combines all four analysis parts."""

import sqlite3
from typing import List

import numpy as np
import pandas as pd
import streamlit as st

from stats import POPULATIONS, RESPONSES, fetch_pbmc_rows, mean, run_ttests, summarize
from subset_analysis import fetch_baseline_melanoma

DB_PATH = 'example.db'
TABLE = 'cell_counts'

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


@st.cache_data
def load_table():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(f'SELECT * FROM {TABLE}', conn)


def relative_frequency(df: pd.DataFrame) -> pd.DataFrame:
    sample_df = df[['sample', *POPULATIONS]].copy()
    sample_df['total_count'] = sample_df[POPULATIONS].sum(axis=1)
    long = sample_df.melt(
        id_vars=['sample', 'total_count'],
        value_vars=POPULATIONS,
        var_name='population',
        value_name='count',
    )
    long['percentage'] = np.where(
        long['total_count'] == 0,
        0,
        long['count'] / long['total_count'] * 100,
    )
    return long


def summarize_responses(percentages: dict) -> pd.DataFrame:
    rows = []
    for population in POPULATIONS:
        yes_mean = mean(percentages['yes'][population])
        no_mean = mean(percentages['no'][population])
        diff = yes_mean - no_mean
        rows.append(
            {
                'population': population,
                'responder_mean': yes_mean,
                'nonresponder_mean': no_mean,
                'difference': diff,
            }
        )
    return pd.DataFrame(rows)


def plot_boxplot(percentages):
    if plt is None:
        st.warning('Matplotlib is not installed—boxplot skipped.')
        return

    fig, axs = plt.subplots(
        1,
        len(POPULATIONS),
        figsize=(len(POPULATIONS) * 2.5, 5),
        sharey=True,
    )
    for ax, population in zip(axs, POPULATIONS):
        data = [percentages[response][population] for response in RESPONSES]
        ax.boxplot(data, labels=['Responder', 'Non-responder'])
        ax.set_title(population)
        ax.set_xlabel('')
    axs[0].set_ylabel('Relative Frequency (%)')
    fig.suptitle('Responder vs Non-responder PBMC population percentages')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    st.pyplot(fig)


def format_baseline(rows: List[sqlite3.Row]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(row) for row in rows])


def main():
    st.set_page_config(page_title='Miraclib Trial Dashboard', layout='wide')
    st.title('Miraclib Trial Dashboard')

    df = load_table()
    st.header('Part 1 · Data Management')
    st.metric('Total samples', len(df))
    st.metric('PBMC entries', int((df['sample_type'] == 'PBMC').sum()))
    st.markdown('First five rows of the raw dataset:')
    st.dataframe(df.head(5), use_container_width=True)

    st.header('Part 2 · Population Frequencies')
    freq_df = relative_frequency(df)
    sample_options = sorted(freq_df['sample'].unique())[:500]
    sample = st.selectbox('Sample to inspect', sample_options)
    st.write(freq_df.loc[freq_df['sample'] == sample])
    st.markdown('Relative frequencies across all samples (first 200 rows):')
    st.dataframe(freq_df.head(200), use_container_width=True)

    st.header('Part 3 · Responder vs Non-responder Analysis')
    rows = fetch_pbmc_rows()
    percentages, sample_counts = summarize(rows)
    ttests = run_ttests(percentages)
    summary_df = summarize_responses(percentages)
    if ttests:
        summary_df['p_value'] = summary_df['population'].map(
            lambda p: ttests[p][1] if ttests[p][1] is not None else np.nan
        )
        summary_df['significant'] = summary_df['p_value'] < 0.05
    st.dataframe(
        summary_df.assign(
            responder_samples=sample_counts['yes'],
            nonresponder_samples=sample_counts['no'],
        ),
        use_container_width=True,
    )
    plot_boxplot(percentages)

    st.header('Part 4 · Baseline Melanoma Subset')
    baseline_rows = fetch_baseline_melanoma()
    baseline_df = format_baseline(baseline_rows)
    if not baseline_df.empty:
        st.markdown(
            f"Baseline samples: {len(baseline_df)}, "
            f"unique subjects: {baseline_df['subject'].nunique()}"
        )
        st.markdown('Samples per project:')
        st.dataframe(
            baseline_df[['project', 'sample']].groupby('project').count(),
            use_container_width=True,
        )
        st.markdown('Responder/non-responder subject counts:')
        st.dataframe(
            baseline_df.groupby('response')['subject'].nunique(),
            use_container_width=True,
        )
        st.markdown('Sex breakdown of baseline subjects:')
        st.dataframe(
            baseline_df.groupby('sex')['subject'].nunique(),
            use_container_width=True,
        )
        st.markdown('Baseline sample details (first 250 rows):')
        st.dataframe(baseline_df.head(250), use_container_width=True)
    else:
        st.warning('No baseline melanoma samples were found in the dataset.')


if __name__ == '__main__':
    main()
