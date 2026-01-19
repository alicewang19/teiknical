import sqlite3

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

try:
    from scipy.stats import ttest_ind
except ImportError:
    ttest_ind = None

DB_PATH = 'example.db'
TABLE = 'cell_counts'
POPULATIONS = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
RESPONSES = ['yes', 'no']
OUTPUT_IMAGE = 'response_boxplot.png'
SIGNIFICANCE_LEVEL = 0.05


def mean(values):
    return sum(values) / len(values) if values else 0.0


def fetch_pbmc_rows():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            f'SELECT sample, response, sample_type, {", ".join(POPULATIONS)} '
            f'FROM {TABLE} '
            'WHERE sample_type = ? '
            'ORDER BY sample',
            ('PBMC',),
        )
        return cur.fetchall()


def summarize(rows):
    percentages = {
        response: {population: [] for population in POPULATIONS}
        for response in RESPONSES
    }
    sample_counts = {response: set() for response in RESPONSES}

    for row in rows:
        response = (row['response'] or '').lower()
        if response not in RESPONSES:
            continue

        counts = [row[pop] or 0 for pop in POPULATIONS]
        total = sum(counts)
        if total == 0:
            continue

        sample_counts[response].add(row['sample'])
        for population, count in zip(POPULATIONS, counts):
            percentages[response][population].append(count / total * 100)

    return percentages, {response: len(sample_counts[response]) for response in RESPONSES}


def print_summary(percentages, sample_counts, ttests):
    headers = [
        'population',
        'responder_mean',
        'nonresponder_mean',
        'difference',
        'responder_samples',
        'nonresponder_samples',
        'p_value',
        'significant',
    ]
    print(','.join(headers))
    for population in POPULATIONS:
        yes_mean = mean(percentages['yes'][population])
        no_mean = mean(percentages['no'][population])
        diff = yes_mean - no_mean
        p_value = ''
        significant = 'n/a'
        if ttests and population in ttests:
            stat, value = ttests[population]
            if value is not None:
                p_value = f'{value:.4f}'
                significant = 'yes' if value < SIGNIFICANCE_LEVEL else 'no'
        print(
            f'{population},{yes_mean:.2f},{no_mean:.2f},{diff:.2f},'
            f'{sample_counts["yes"]},{sample_counts["no"]},'
            f'{p_value},{significant}'
        )


def run_ttests(percentages):
    if ttest_ind is None:
        return None

    results = {}
    for population in POPULATIONS:
        responder = percentages['yes'][population]
        non_responder = percentages['no'][population]
        if len(responder) < 2 or len(non_responder) < 2:
            results[population] = (None, None)
            continue
        stat, p_value = ttest_ind(responder, non_responder, equal_var=False)
        results[population] = (stat, p_value)
    return results


def plot_percentages(percentages):
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
    fig.savefig(OUTPUT_IMAGE)
    print(f'Saved {OUTPUT_IMAGE}')


def main():
    rows = fetch_pbmc_rows()
    percentages, sample_counts = summarize(rows)
    ttests = run_ttests(percentages)
    print_summary(percentages, sample_counts, ttests)

    if plt is None:
        print('Matplotlib not available, skipping the responder boxplot.')
        return

    plot_percentages(percentages)


if __name__ == '__main__':
    main()
