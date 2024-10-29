import pyscopg2
# Register student for a course

def prompts():
    student_id = input("Enter student ID: ")
    course_id = input("Enter course ID: ")
    sec_id = input("Enter section ID: ")
    semester = input("Enter semester: ")
    year = int(input("Enter year: "))
    return semester, year, student_id, course_id, sec_id

def prerequisites(cur, student_id, course_id):
    cur.execute("""select prereq_id from prereq
                    where course_id = %s""", (course_id))
    prerequisites = cur.fetchall()

    for prereq in prerequisites:
        cur.execute("""select count(*) from takes
                        where id = %s and
                        course_id =%s and
                        grade is not null""", (student_id, prereq[0]))
        if cur.fetchone()[0] == 0:
            print("Student has not completed all prerequisites")
            return False
    return True

def schedule(cur, student_id, course_id, sec_id, semester, year):
    cur.execute("""select time_slot_id from section
                    where course_id = %s and
                    sec_id = %s and
                    semester = %s and
                    year = %s""", (course_id, sec_id, semester, year))
    wanted_time = cur.fetchone()

    if wanted_time:
        cur.execute("""select s.time_slot_id from takes t
                        join section s on t.course_id = s.course_id and 
                        t.sec_id = s.sec_id and 
                        t.semester = s.semester and
                        t.year = s.year
                        where t.id = %s and
                        t.semester = %s and
                        t.year = %s""", (student_id, semester, year))
        for taken_time in cur.fetchall():
            if taken_time[0] == wanted_time[0]:
                print("Student already has a course registered for that time")
                return False
    return True

def avalability(cur, course_id, sec_id, semester, year):
    cur.execute("""select building, room_number from section 
                    where course_id = %s and 
                    sec_id = %s and 
                    semester = %s and 
                    year = %s""", (course_id, sec_id, semester, year))
    sec = cur.fetchone()

    if sec:
        cur.execute("""select capacity from classroom
                        where building = %s and
                        room_number = %s""", (sec[0], sec[1]))
        capacity = cur.fetchone()[0]

        cur.execute("""select count(*) from takes 
                        where course_id = %s and 
                        sec_id = %s and 
                        semester = %s and 
                        year = %s""", (course_id, sec_id, semester, year))
        num_students = cur.fetchone()[0]
        if enrollment >= capacity:
            print("This section is already full.")
            return False

    else:
        print("That course or section is not offered in the specified term")
        return False
    return True

def register(cur, student_id, course_id, sec_id, semester, year):
    if not prerequisites(cur, student_id, course_id):
        return
    if not schedule(cur, student_id, course_id, sec_id, semester, year):
        return
    if not avalability(cur, course_id, sec_id, semester, year):
        return
    
    try:
        cur.execute ("""insert into takes(ID, course_id, sec_id, semester, year) 
                     values (%s, %s, %s, %s, %s)""", (student_id, course_id, sec_id, semester, year))
        print("Register complete!")
    except psycopg2.Error:
        print("Registration error")

def main():
    conn = psycopg2.connect(dbname="dbinstrux")
    cur = conn.cursor()

    student_id,course_id,sec_id,semester,year = prompts()

try:
    register(cur, student_id, course_id, sec_id, semester, year)
    conn.commit()

except pycopg2.Error as e:
    print("Error")
    print(e)
    conn.rollback()

finally:
    conn.close()
