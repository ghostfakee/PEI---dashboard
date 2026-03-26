import duckdb

con = duckdb.connect("teste.duckdb")

result = con.execute("SELECT 1 + 1").fetchall()

print(result)

con.close()