# Team1 best project
# More comments for git testing

import psycopg2

conn = psycopg2.connect(dbname="team1")
cur = conn.cursor()

query = '''
        select advisee.id, advisee.name, instructor.name 
        from (
            select * 
            from advisor, student 
            where id = s_id) as advisee, instructor 
        where instructor.id = i_id;'''

try:
    cur.execute(query)
    print("\nAdvisee id | Advisee name | Advisor name")
    print("===========|==============|=============")
    for advisee in cur:
        print(advisee[0], '     |', advisee[1], ' '*(11-len(advisee[1])), '|', advisee[2])
    conn.commit()
except psycopg2.Error as e:
    print("Other Error")
    print(e)
    conn.rollback()


def prompts():
    fac = input("Enter the name of a new faculty member: ")
    fid = input("Enter a new ID for the faculty member: ")
    dep = input("Enter the faculty member's department: ")
    sal = input("Enter the faculty member's salary: ")
    return fac,fid,dep,sal

conn = psycopg2.connect(dbname="team1")
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