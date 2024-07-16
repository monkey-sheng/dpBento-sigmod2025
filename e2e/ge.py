import duckdb
from pathlib import Path

# 定义scale factor的列表和对应的目录路径
scale_factors = [0.1, 1, 3, 10]
parquet_base_dir = Path('base_directory_path')

# 循环处理每个scale factor
for sf in scale_factors:
    # 拼接DuckDB文件路径
    duckdb_file_path = f'sf{sf}.db'  # 确保文件扩展名是.db

    # 连接到DuckDB数据库
    try:
        with duckdb.connect(database=duckdb_file_path, read_only=False) as conn:
            # 尝试加载tpch扩展
            conn.execute("LOAD tpch")
            
            # 调用dbgen生成数据
            conn.execute(f"CALL dbgen(sf={sf})")
            
            # 打印完成生成数据的信息
            print(f"Data generated for SF={sf} in DuckDB database at {duckdb_file_path}")
    except duckdb.DuckDBError as e:
        # 如果tpch扩展未安装，进行安装
        if "Extension not found" in str(e):
            with duckdb.connect(database=duckdb_file_path, read_only=False) as conn:
                conn.execute("INSTALL tpch")
                conn.execute("LOAD tpch")
                conn.execute(f"CALL dbgen(sf={sf})")
                print(f"TPC-H extension installed and data generated for SF={sf} in DuckDB database at {duckdb_file_path}")
        else:
            # 打印其他可能的错误信息
            print(f"An error occurred: {e}")