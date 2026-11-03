#!/usr/bin/env python3
"""Optional OFFLINE PC utility. Requires locally installed pyarrow, never uploads data."""
from __future__ import annotations
import argparse
from pathlib import Path
import csv

FIELDS = {'elapsed_ms', 'latitude', 'longitude', 'altitude_m', 'speed_mps', 'heading_deg', 'satellites', 'battery_pct', 'x', 'y', 'z', 'intensity'}

def main():
    parser = argparse.ArgumentParser(description='Local CSV → valid Apache Parquet (requires pyarrow)')
    parser.add_argument('source', type=Path, help='CSV exported by Drone Data Studio')
    parser.add_argument('--out', type=Path, help='Parquet output file (default: same basename)')
    args = parser.parse_args()
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        parser.error('Cần cài đặt pyarrow cục bộ: python -m pip install pyarrow. Không upload dữ liệu.')
    target = args.out or args.source.with_suffix('.parquet')
    with args.source.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            parser.error('CSV không có header')
        records = list(reader)
    if not records:
        parser.error('CSV không có bản ghi')
    data = {}
    for key in reader.fieldnames:
        raw = [r.get(key, '') for r in records]
        if key in FIELDS:
            try:
                data[key] = pa.array([float(v) if v not in ('',None) else None for v in raw], type=pa.float64())
            except ValueError:
                parser.error(f'Cột số không hợp lệ: {key}')
        else:
            data[key] = pa.array([v if v != '' else None for v in raw], type=pa.string())
    table = pa.table(data)
    pq.write_table(table, target, compression='zstd')
    with target.open('rb') as f:
        if f.read(4) != b'PAR1':
            parser.error('Output Parquet magic không hợp lệ')
    print(f'Đã tạo {target}: {table.num_rows} hàng; {table.num_columns} cột; không upload.')

if __name__ == '__main__': main()
