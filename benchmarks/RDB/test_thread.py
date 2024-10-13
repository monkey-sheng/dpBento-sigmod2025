import duckdb

# Connect to DuckDB (or create an in-memory database)
conn = duckdb.connect()

# Show a list of all available settings
settings_df = conn.execute("SELECT * FROM duckdb_settings()").fetchdf()
print(settings_df)

# Return the current value of a specific setting (e.g., 'threads')
threads_setting = conn.execute("SELECT current_setting('threads')").fetchone()
print(threads_setting[0])
