import duckdb

con = duckdb.connect("agro_clima.duckdb")
con.execute("SELECT 1;")
print("Banco criado com sucesso.")
con.close()