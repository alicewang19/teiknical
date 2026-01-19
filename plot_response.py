try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit(
        'matplotlib is required to generate the response plot; install it with '
        '"pip install matplotlib"'
    ) from exc

from stats import POPULATIONS, RESPONSES, fetch_pbmc_rows

OUTPUT = 'response_boxplot.png'


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


def main():
    rows = fetch_pbmc_rows()
    percentages = collect_percentages(rows)

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
    fig.savefig(OUTPUT)
    print(f'Saved {OUTPUT}')


if __name__ == '__main__':
    main()
