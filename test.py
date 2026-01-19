import sqlite3


def main():
    conn = sqlite3.connect('example.db')
    try:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM cell_counts')
        (count,) = cur.fetchone()
        print(f'cell_counts rows: {count}')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
