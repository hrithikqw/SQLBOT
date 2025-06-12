import sqlite3
connection  = sqlite3.connect("Chinook.db")
cursor = connection.cursor()
print("Records are inserted!!")
data = cursor.execute('''select * from prreport where approval_status = 1''')
for row in data:
    print(row)
connection.commit()
connection.close()