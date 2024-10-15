import psycopg2

def prompts():
    fac = input("Enter the name of a new faculty member: ")
    fid = input("Enter a new ID for the faculty member: ")
    dep = input("Enter the faculty member's department: ")
    sal = input("Enter the faculty member's salary: ")
    return fac,fid,dep,sal

conn = psycopg2.connect(dbname="dbinstrux")
cur = conn.cursor()

fac,fid,dep,sal = prompts()
query = "insert into instructor values (%s, %s, %s, %s);"

try:
    cur.execute(query, (fid,fac,dep,sal))
    conn.commit()
except psycopg2.errors.UniqueViolation:
    print("ID already in use.")
    conn.rollback()
except psycopg2.errors.ForeignKeyViolation:
    print("No such department.")
    conn.rollback()
except psycopg2.errors.CheckViolation:
    print("Salary is too low.")
    conn.rollback()
except psycopg2.Error as e:
    print("Other Error")
    print(e)
    conn.rollback()

query = "select * from instructor"
try:
    cur.execute(query)
    for instructor in cur:
        print(instructor[0], instructor[1], instructor[2], instructor[3])
except psycopg2.Error as e:
    print("Other Error")
    print(e)
    conn.rollback()
finally:
    conn.close()