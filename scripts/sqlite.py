import csv
import sqlite3
from pathlib import Path

DB_PATH = Path('example.db')
CSV_PATH = Path('cell-count.csv')
TABLE = 'cell_counts'

HEADERS = [
    'project',
    'subject',
    'condition',
    'age',
    'sex',
    'treatment',
    'response',
    'sample',
    'sample_type',
    'time_from_treatment_start',
    'b_cell',
    'cd8_t_cell',
    'cd4_t_cell',
    'nk_cell',
    'monocyte',
]

INT_COLUMNS = {
    'age',
    'time_from_treatment_start',
    'b_cell',
    'cd8_t_cell',
    'cd4_t_cell',
    'nk_cell',
    'monocyte',
}

CREATE_SQL = f'''
CREATE TABLE IF NOT EXISTS {TABLE} (
    project TEXT,
    subject TEXT,
    condition TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT,
    sample TEXT,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    b_cell INTEGER,
    cd8_t_cell INTEGER,
    cd4_t_cell INTEGER,
    nk_cell INTEGER,
    monocyte INTEGER
);
'''


def load_csv():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f'missing {CSV_PATH}')

    with CSV_PATH.open(newline='') as fh:
        reader = csv.DictReader(fh)
        records = []
        for row in reader:
            vals = []
            for header in HEADERS:
                value = row[header]
                if header in INT_COLUMNS:
                    value = int(value) if value else None
                vals.append(value)
            records.append(tuple(vals))
        return records


def main():
    records = load_csv()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(CREATE_SQL)
        cur.execute(f'DELETE FROM {TABLE}')
        cur.executemany(
            f'INSERT INTO {TABLE} ({", ".join(HEADERS)}) VALUES ({", ".join("?" for _ in HEADERS)})',
            records,
        )
        conn.commit()


if __name__ == '__main__':
    main()
