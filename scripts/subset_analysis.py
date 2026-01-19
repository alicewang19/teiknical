import sqlite3
from collections import defaultdict
from pprint import pprint

DB_PATH = 'example.db'
TABLE = 'cell_counts'


def fetch_baseline_melanoma():
    query = f'''
SELECT
    project,
    sample,
    subject,
    condition,
    treatment,
    response,
    sex,
    age,
    sample_type,
    time_from_treatment_start,
    b_cell,
    cd8_t_cell,
    cd4_t_cell,
    nk_cell,
    monocyte
FROM {TABLE}
WHERE
    condition = 'melanoma'
    AND sample_type = 'PBMC'
    AND treatment = 'miraclib'
    AND time_from_treatment_start = 0
ORDER BY sample
'''
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        return cur.fetchall()


def main():
    rows = fetch_baseline_melanoma()

    summary = {
        'projects': defaultdict(int),
        'response_subjects': defaultdict(set),
        'sex_subjects': defaultdict(set),
    }
    writer = []

    for row in rows:
        summary['projects'][row['project']] += 1

        subject = row['subject']
        if row['response']:
            summary['response_subjects'][row['response'].lower()].add(subject)
        sex = (row['sex'] or '').upper()
        if sex:
            summary['sex_subjects'][sex].add(subject)

        writer.append({
            'sample': row['sample'],
            'project': row['project'],
            'subject': subject,
            'response': row['response'],
            'sex': row['sex'],
            'age': row['age'],
            'b_cell': row['b_cell'],
            'cd8_t_cell': row['cd8_t_cell'],
            'cd4_t_cell': row['cd4_t_cell'],
            'nk_cell': row['nk_cell'],
            'monocyte': row['monocyte'],
        })

    #pprint(writer)
    print('\nSummary:')
    print('Samples per project:')
    pprint(dict(summary['projects']))
    print('Responder/non-responder subject counts:')
    pprint({k: len(v) for k, v in summary['response_subjects'].items()})
    print('Male/female subject counts:')
    pprint({k: len(v) for k, v in summary['sex_subjects'].items()})


if __name__ == '__main__':
    main()
