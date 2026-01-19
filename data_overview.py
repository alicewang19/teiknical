import csv
import sqlite3
import sys

DB_PATH = 'example.db'
TABLE = 'cell_counts'

POPULATIONS = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']


def fetch_rows():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            f'SELECT sample, {", ".join(POPULATIONS)} FROM {TABLE} ORDER BY sample'
        )
        return cur.fetchall()


def percentage(count, total):
    return (count / total * 100) if total else 0.0


def main():
    rows = fetch_rows()
    writer = csv.writer(sys.stdout)
    writer.writerow(['sample', 'total_count', 'population', 'count', 'percentage'])
    for row in rows:
        total = sum(row[col] or 0 for col in POPULATIONS)
        for population in POPULATIONS:
            count = row[population] or 0
            writer.writerow(
                [
                    row['sample'],
                    total,
                    population,
                    count,
                    f'{percentage(count, total):.2f}',
                ]
            )


if __name__ == '__main__':
    main()

