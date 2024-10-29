# Team1 best project
# More comments for git testing

import psycopg2

def advisor_list():
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


def insert_instructor_prompts():
    fac = input("Enter the name of a new faculty member: ")
    fid = input("Enter a new ID for the faculty member: ")
    dep = input("Enter the faculty member's department: ")
    sal = input("Enter the faculty member's salary: ")
    return fac,fid,dep,sal

def insert_instructor():
        fac,fid,dep,sal = insert_instructor_prompts()
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

def generate_transcript():

def course_list():

def register_prompts():
    student_id = input("Enter student ID: ")
    course_id = input("Enter course ID: ")
    sec_id = input("Enter section ID: ")
    semester = input("Enter semester: ")
    year = input("Enter year: ")
    return student_id, course_id, sec_id, semester, year

def register_prerequisites(cur, student_id, course_id):
    cur.execute("""select prereq_id from prereq 
                    where course_id = %s;""", (course_id,))
    prerequisites = cur.fetchall()

    for prereq in prerequisites:
        cur.execute("""select count(*) from takes 
                        where id = %s and 
                        course_id = %s and 
                        grade is not null;""", (student_id, prereq[0]))
        if cur.fetchone()[0] == 0:
            print("Student has not completed all prerequisites")
            return False
    return True

def register_schedule(cur, student_id, course_id, sec_id, semester, year):
    cur.execute("""select time_slot_id from section 
                    where course_id = %s and 
                    sec_id = %s and 
                    semester = %s and 
                    year = %s;""", (course_id, sec_id, semester, year))
    wanted_time = cur.fetchone()

    if wanted_time:
        cur.execute("""select s.time_slot_id from takes t 
                        join section s on t.course_id = s.course_id and 
                        t.sec_id = s.sec_id and 
                        t.semester = s.semester and 
                        t.year = s.year 
                        where t.id = %s and 
                        t.semester = %s and 
                        t.year = %s;""", (student_id, semester, year))
        for taken_time in cur.fetchall():
            if taken_time[0] == wanted_time[0]:
                print("Student already has a course registered for that time")
                return False
    return True

def register_avalability(cur, course_id, sec_id, semester, year):
    cur.execute("""select building, room_number from section 
                    where course_id = %s and 
                    sec_id = %s and 
                    semester = %s and 
                    year = %s;""", (course_id, sec_id, semester, year))
    sec = cur.fetchone()

    if sec:
        cur.execute("""select capacity from classroom 
                        where building = %s and 
                        room_number = %s;""", (sec[0], sec[1]))
        capacity = cur.fetchone()[0]

        cur.execute("""select count(*) from takes 
                        where course_id = %s and 
                        sec_id = %s and 
                        semester = %s and 
                        year = %s;""", (course_id, sec_id, semester, year))
        num_students = cur.fetchone()[0]
        if num_students >= capacity:
            print("This section is already full.")
            return False

    else:
        print("That course or section is not offered in the specified term")
        return False
    return True

def register(cur, student_id, course_id, sec_id, semester, year):
    if not register_prerequisites(cur, student_id, course_id):
        return
    if not register_schedule(cur, student_id, course_id, sec_id, semester, year):
        return
    if not register_avalability(cur, course_id, sec_id, semester, year):
        return
    
    try:
        cur.execute ("""insert into takes(ID, course_id, sec_id, semester, year) 
                     values (%s, %s, %s, %s, %s);""", (student_id, course_id, sec_id, semester, year))
        print("Registration complete!")
    except psycopg2.Error:
        print("Registration error")

def register_handler():
    student_id,course_id,sec_id,semester,year = register_prompts()

    try:
        register(cur, student_id, course_id, sec_id, semester, year)
        conn.commit()

    except psycopg2.Error as e:
        print("Error")
        print(e)
        conn.rollback()

def main():

    conn = psycopg2.connect(dbname="team1")
    cur = conn.cursor()
        
    while(1):
        print("Welcome to the Team1 University Database System(c)!\n\n")
        print("A: Generate list of advisees and advisors\n")
        print("I: Add an instructor to the database\n")
        print("T: Generate a student's transcript\n")
        print("C: Generate a course list for a term\n")
        print("R: Register a student for a course\n")
        print("Q: Close the connection and exit the program\n\n")
        
        input = input("Enter your selection: \n")

        match input:
                case "A":
                        advisor_list()
                case "I":
                        insert_instructor()
                case "T":
                        generate_transcript()
                case "C":
                        course_list()
                case "R":
                        register_handler()
                case "Q":
                        break
                case _:
                        print("Invalid input, please try again\n")
                        
    finally:
        conn.close()
