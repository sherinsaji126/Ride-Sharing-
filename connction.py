import pyodbc


print(pyodbc.drivers())


conn = pyodbc.connect(

"DRIVER={ODBC Driver 17 for SQL Server};"
"SERVER=SherinDell\\SQLEXPRESS;"
"DATABASE=RideSharing;"
"Trusted_Connection=yes;"
"TrustServerCertificate=yes;"
)
print("Connected Successfully")