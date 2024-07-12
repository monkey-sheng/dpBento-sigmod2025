import duckdb
from pathlib import Path

scale_factors = [1, 3, 10]
parquet_base_dir = Path('base_directory_path')

for sf in scale_factors:
    duckdb_file_path = f'sf{sf}'  

    with duckdb.connect(database=duckdb_file_path, read_only=False) as conn:
            conn.execute("LOAD tpch")
            
            conn.execute(f"CALL dbgen(sf={sf})")
            
            print(f"Data generated for SF={sf} in DuckDB database at {duckdb_file_path}")
    
