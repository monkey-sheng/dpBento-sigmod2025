import duckdb
from pathlib import Path

# 定义scale factor的列表和对应的目录路径
scale_factors = [0.1, 1, 3, 10]  # 只包含0.1
parquet_base_dir = Path('base_directory_path')

# 循环处理每个scale factor
for sf in scale_factors:
        # 拼接DuckDB文件路径
        duckdb_file_path = f'sf{sf}'
        # 这里不需要创建目录，因为我们不导出数据到Parquet文件

        # 连接到DuckDB数据库
        with duckdb.connect(database=duckdb_file_path, read_only=False) as conn:
            # 安装并加载TPC-H扩展
            conn.execute("INSTALL tpch")
            conn.execute("LOAD tpch")
            
            # 调用dbgen生成数据
            conn.execute(f"CALL dbgen(sf={sf})")
            
            # 打印完成生成数据的信息
            print(f"Data generated for SF={sf} in DuckDB database at {duckdb_file_path}")
