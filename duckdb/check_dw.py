import duckdb

con = duckdb.connect("agro_clima.duckdb")

print("SHOW TABLES:")
print(con.execute("show tables").fetchall())

print("\nINFORMATION_SCHEMA:")
print(
    con.execute("""
        select table_schema, table_name, table_type
        from information_schema.tables
        order by table_schema, table_name
    """).fetchall()
)

con.close()