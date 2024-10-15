# Team1 best project
# More comments for git testing

import psycopg2

conn = psycopg2.connect(dbname="team1")
cur = conn.cursor()

query = "select advisee.id, advisee.name, instructor.name from (select * from advisor, student where id = s_id) as advisee, instructor where instructor.id = i_id;"

try:
    cur.execute(query)
    print("\nAdvisee id | Advisee name | Advisor name")
    print("========================================")
    for advisee in cur:
        print(advisee[0], '     |', advisee[1], ' '*(11-len(advisee[1])), '|', advisee[2])
    conn.commit()
except psycopg2.Error as e:
    print("Other Error")
    print(e)
    conn.rollback()
