from pymilvus import connections, db
connections.connect(
  alias="default",
  user='username',
  password='password',
  host='localhost',
  port='19530'
)
db_list = db.list_database()
print(db_list)
