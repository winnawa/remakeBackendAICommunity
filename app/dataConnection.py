import psycopg2
conn_str = "postgres://smokhbuk:bjPRreLazLtTKelzdNGuYUMAMRbX08cC@tiny.db.elephantsql.com/smokhbuk"
user, password, host, path = conn_str.split("//")[1].split(":")[0], conn_str.split(":")[2].split("@")[0], conn_str.split("@")[1].split("/")[0], conn_str.split("/")[3]

# Create a connection
conn = psycopg2.connect(
    dbname=path,
    user=user,
    password=password,
    host=host
)

curr = conn.cursor()


