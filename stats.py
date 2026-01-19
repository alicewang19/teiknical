import sqlite3
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

DB_PATH = 'example.db'
TABLE = 'cell_counts'
POPULATIONS = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
RESPONSES = ['yes', 'no']
OUTPUT_IMAGE = 'response_boxplot.png'


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
    stats = {
        response: defaultdict(list) for response in RESPONSES
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
            stats[response][population].append(count / total * 100)

    return stats, {response: len(sample_counts[response]) for response in RESPONSES}


def print_summary(stats, sample_counts):
    print('population,responder_mean,nonresponder_mean,difference,responder_samples,nonresponder_samples')
    for population in POPULATIONS:
        yes_mean = mean(stats['yes'][population])
        no_mean = mean(stats['no'][population])
        diff = yes_mean - no_mean
        print(
            f'{population},{yes_mean:.2f},{no_mean:.2f},{diff:.2f},'
            f'{sample_counts["yes"]},{sample_counts["no"]}'
        )


def main():
    rows = fetch_pbmc_rows()
    stats, sample_counts = summarize(rows)
    print_summary(stats, sample_counts)

    if plt is None:
        print('Matplotlib not available, skipping the responder boxplot.')
        return

    percentages = collect_percentages(rows)
    plot_percentages(percentages)


def collect_percentages(rows):
    percentages = {
        response: {population: [] for population in POPULATIONS}
        for response in RESPONSES
    }
    for row in rows:
        response = (row['response'] or '').lower()
        if response not in RESPONSES:
            continue

        total = sum((row[pop] or 0) for pop in POPULATIONS)
        if total == 0:
            continue

        for population in POPULATIONS:
            count = row[population] or 0
            percentages[response][population].append(count / total * 100)

    return percentages


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


if __name__ == '__main__':
    main()
