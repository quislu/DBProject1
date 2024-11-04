# Team1 best project
# More comments for git testing

import psycopg2

# Generates advisor list
def advisor_list(cur):
    '''Submits query and prints for table of advisor and advisee names'''
    query = """
        select advisee.id, advisee.name, instructor.name 
        from (
            select * 
            from advisor, student 
            where id = s_id) as advisee, instructor 
        where instructor.id = i_id;"""

    try:
        cur.execute(query)
        print("\nAdvisee id | Advisee name | Advisor name")
        print("===========|==============|=============")
        for advisee in cur:
            print(advisee[0], '     |', advisee[1], ' '*(11-len(advisee[1])), '|', advisee[2])
        # conn.commit()
    except psycopg2.Error as e:
        print("Other Error")
        print(e)
        # conn.rollback()

def insert_instructor_prompts():
    '''Accepts user input and assigns to variables that will be passed to insert_instructor()'''
    fac = input("Enter the name of a new faculty member: ")
    fid = input("Enter a new ID for the faculty member: ")
    dep = input("Enter the faculty member's department: ")
    sal = input("Enter the faculty member's salary: ")
    return fac,fid,dep,sal

# tries to insert a new instructor into the table
def insert_instructor(cur):
    '''Takes user inputs and attempts to insert a new instructor with those values'''
    fac,fid,dep,sal = insert_instructor_prompts()
    query = "insert into instructor values (%s, %s, %s, %s);"
        
    try:
        cur.execute(query, (fid,fac,dep,sal))
    except psycopg2.errors.UniqueViolation:
        print("ID already in use.")
        raise
    except psycopg2.errors.ForeignKeyViolation:
        print("No such department.")
        raise
    except psycopg2.errors.CheckViolation:
        print("Salary is too low.")
        raise
    except psycopg2.Error as e:
        print("Other Error", e)
        raise
    
    query = "select * from instructor"
    # try:
    #     cur.execute(query)
    #     for instructor in cur:
    #         print(instructor[0], instructor[1], instructor[2], instructor[3])
    # except psycopg2.Error as e:
    #     print("Other Error")
    #     print(e)
    #     conn.rollback()

# gets input for generating course list
def course_list_prompts():
    semester = input("Enter semester: ")
    year = input("Enter year: ")
    return semester, year

# gets all matching sections in the given semester and year
def get_sections(cur, semester, year):
    cur.execute("""select * from section
                   where semester = %s and year = %s
                   order by course_id""",(semester, year))
    sections = []
    for line in cur:
        sections += [[line[i] for i in range(0, len(line))]]
    return sections

# gets the course title from the course id given
def get_course_name(cur, c_id):
    cur.execute("""select title, credits from section natural join course
                   where course_id = %s""", (c_id,))
    course_info = cur.fetchone()
    return course_info[0], str(course_info[1])

# gets the time slot from given time slot and formats it
def get_time_slots(cur, ts_id):
    cur.execute("""select day, start_hr, start_min, end_hr, end_min
                   from time_slot
                   where time_slot_id = %s""",(ts_id,))
    result = cur.fetchall()
    time_slot = []
    i = 0
    for line in result:
        time_slot += [[str(line[i]) for i in range(0, len(line))]]
        if time_slot[i][2] == "0":
            time_slot[i][2] = "00"
        i += 1
    for i in range(0, len(time_slot)):
        time_slot[i] = [time_slot[i][0], f"{time_slot[i][1]}:{time_slot[i][2]}",f"{time_slot[i][3]}:{time_slot[i][4]}"]
    return time_slot

# gets capacity of classroom given building and room number
def get_capacity(cur, building, room):
    cur.execute("""select capacity from classroom
                   where building = %s and room_number = %s""", (building, room))
    return str(cur.fetchone()[0])

# gets the number of students enrolled in a given class
def get_enrollment(cur, course_id, sec_id, semester, year):
    cur.execute(""" select count(id)
                    from takes 
                    where course_id = %s and sec_id = %s and semester = %s and year = %s""", (course_id, sec_id, semester, year))
    return str(cur.fetchone()[0])


# formats and prints the course list
def print_course_list(sections, semester, year):
    space = " "
    print(f"\nCourses offered in {semester} of {year}: \n")
    print("Course-Section   Course Title                  Credits   Building   Room Number   Capacity   Enrollment")
    for line in sections:
        course_section = f"{line[0]}-{line[1]}"
        course_section += (space * (17-len(course_section)))

        title = line[2]
        title += (space * (30-len(title)))

        credits = f"({line[3]})"
        credits += (space * (10-len(credits)))

        building = line[4]
        building += (space * (11-len(building)))

        room = line[5]
        room += (space * (14-len(room)))

        capacity = line[7]
        capacity += (space * (11-len(capacity)))

        enroll = line[8]

        course_line = f"{course_section}{title}{credits}{building}{room}{capacity}{enroll}"
        print("-"*103)
        print(course_line)
        print("\nMeeting times:")
        for time in line[6]:
            timeslot = f" {time[0]} {time[1]}-{time[2]}"
            print(timeslot)
        print("")

# generates course list
def generate_course_list(cur):
    semester, year = course_list_prompts()
    sections = get_sections(cur, semester, year)
    if len(sections) == 0:
        print(f"\nNo sections being offered for {semester} of {year}. \n")
    else:
        for i in range(0,len(sections)):
            sections[i][2], sections[i][3] = get_course_name(cur, sections[i][0])
            sections[i][6] = get_time_slots(cur, sections[i][6])
            sections[i].append(get_capacity(cur, sections[i][4], sections[i][5]))
            sections[i].append(get_enrollment(cur, sections[i][0], sections[i][1], semester, year))
        print_course_list(sections, semester, year)


def generate_transcript(cur):
    id = input("Enter the student id: ")
    setup_query = '''
    DROP VIEW IF EXISTS student_gpa_semester;
    DROP VIEW IF EXISTS student_gpa;
    DROP VIEW IF EXISTS credits_taken;
    DROP TABLE IF EXISTS GPA CASCADE;
    CREATE TABLE GPA (
        letter VARCHAR(2) PRIMARY KEY,
        points NUMERIC(2)
    );

    INSERT INTO GPA VALUES ('A+', 4.0);
    INSERT INTO GPA VALUES ('A', 4.0);
    INSERT INTO GPA VALUES ('A-', 3.7);
    INSERT INTO GPA VALUES ('B+', 3.3);
    INSERT INTO GPA VALUES ('B', 3.0);
    INSERT INTO GPA VALUES ('B-', 2.7);
    INSERT INTO GPA VALUES ('C+', 2.3);
    INSERT INTO GPA VALUES ('C', 2.0);
    INSERT INTO GPA VALUES ('C-', 1.7);
    INSERT INTO GPA VALUES ('D+', 1.3);
    INSERT INTO GPA VALUES ('D', 1.0);
    INSERT INTO GPA VALUES ('D-', 0.7);
    INSERT INTO GPA VALUES ('F', 0);
    

    CREATE VIEW credits_taken AS
        SELECT student.ID as student_id, SUM(credits) AS taken_creds
        FROM student 
        NATURAL JOIN takes 
        NATURAL JOIN course
        GROUP BY student.ID;

    CREATE VIEW student_gpa AS
        SELECT takes.ID as student_id, SUM(GPA.points * 1.0 * course.credits / credits_taken.taken_creds) AS cumulative_gpa
        FROM takes
        LEFT JOIN credits_taken ON takes.ID = credits_taken.student_id
        LEFT JOIN GPA ON takes.grade = GPA.letter
        LEFT JOIN course ON takes.course_id = course.course_id
        GROUP BY takes.ID;

    CREATE VIEW student_gpa_semester AS
        SELECT takes.ID as student_id, 
            takes.semester || takes.year AS semester_year,
            SUM(GPA.points * 1.0 * course.credits / credits_taken.taken_creds) AS semester_gpa
        FROM takes
        LEFT JOIN credits_taken ON takes.ID = credits_taken.student_id
        LEFT JOIN GPA ON takes.grade = GPA.letter
        LEFT JOIN course ON takes.course_id = course.course_id
        GROUP BY takes.ID, semester_year;
    '''
    cur.execute(setup_query)

    transcript_query = '''
    WITH student_takes AS (
        SELECT student.ID AS student_id, student.name, student.dept_name, takes.*
        FROM student 
        LEFT JOIN takes ON student.ID = takes.ID
    ),
    student_takes_course AS (
        SELECT student_takes.student_id, student_takes.name, student_takes.dept_name, student_takes.semester, student_takes.year,
        student_takes.course_id, student_takes.sec_id, course.title, course.credits, student_takes.grade, credits_taken.taken_creds
        FROM student_takes 
        LEFT JOIN course ON student_takes.course_id = course.course_id
        LEFT JOIN credits_taken ON student_takes.student_id = credits_taken.student_id
    )
    SELECT 
        student_takes_course.student_id as ID, 
        student_takes_course.name, 
        student_takes_course.dept_name, 
        student_takes_course.semester || student_takes_course.year AS semester_year,
        student_takes_course.course_id, 
        student_takes_course.sec_id, 
        student_takes_course.title, 
        student_takes_course.credits, 
        student_takes_course.grade,
        student_gpa_semester.semester_gpa,
        student_gpa.cumulative_gpa
    FROM 
        student_takes_course
    LEFT JOIN student_gpa ON student_takes_course.student_id = student_gpa.student_id
    LEFT JOIN student_gpa_semester 
        ON student_takes_course.student_id = student_gpa_semester.student_id
        AND student_takes_course.semester || student_takes_course.year = student_gpa_semester.semester_year
    WHERE student_takes_course.student_id = %s
    ORDER BY student_takes_course.year;
    '''

    drop_query = '''
    DROP VIEW IF EXISTS student_gpa_semester;
    DROP VIEW IF EXISTS student_gpa;
    DROP VIEW IF EXISTS credits_taken;
    DROP TABLE IF EXISTS GPA CASCADE;'''
    try:
        cur.execute(transcript_query, (id,))
        rows = cur.fetchall()

        if rows:
            # Print transcript
            print(f"Transcript for {rows[0][1]}: {id} ")
            print(f"{rows[0][2]}")
            current_semester = None
            for row in rows:
                if row[3] != current_semester:
                    current_semester = row[3]
                    sem_gpa = row[9] if row[9] is not None else "N/A"
                    cumulative_gpa = row[10] if row[10] is not None else "N/A"
                    if sem_gpa != "N/A":
                        print(f"\n{current_semester} Semester GPA: {sem_gpa:.2f}")
                    else: 
                        print(f"\n{current_semester} Semester GPA: N/A ")
                    ("Course ID | Section | Course Name | Credits | Grade")
                    print("-" * 60)

                print(f"{row[4]}-{row[5]} {row[6]} ({row[7]}) {row[8]}")

            # Display cumulative GPA at the end
            if cumulative_gpa != "N/A":
                print(f"Cumulative GPA: {cumulative_gpa:.2f}")
            else:
                print(f"Cumulative GPA: N/A")
        else:
            print("No records found for that student ID.")
        cur.execute(drop_query)
        
    except psycopg2.error:
        print("Transcript generation error")

def course_list():
    return

def register_prompts():
    # Accepts user input and assigns to variables that will be passed to insert_instructor()
    student_id = input("Enter student ID: ")
    course_id = input("Enter course ID: ")
    sec_id = input("Enter section ID: ")
    semester = input("Enter semester: ")
    year = input("Enter year: ")
    return student_id, course_id, sec_id, semester, year

def register_prerequisites(cur, student_id, course_id):
    # Fetches prereq table from database as array
    cur.execute("""select prereq_id from prereq 
                    where course_id = %s;""", (course_id,))
    prerequisites = cur.fetchall()

    # Iterates over the array, testing if the student has taken each prerequisite.  If not, returns false to
    # fail the conditional in register() and prints an error message.
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
    # Fetches the time slot of the desired class
    cur.execute("""select time_slot_id from section 
                    where course_id = %s and 
                    sec_id = %s and 
                    semester = %s and 
                    year = %s;""", (course_id, sec_id, semester, year))
    wanted_time = cur.fetchone()

    # Fetches and iterates over the student's schedule, comparing each class's time slot to the desired class's time slot.
    # If not, returns false to fail the conditional in register() and prints an error message.
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
    # Fetches the classroom of the desired course, and if the desired course is not found, returns false to fail the conditional
    # in register() and prints an error message.
    cur.execute("""select building, room_number from section 
                    where course_id = %s and 
                    sec_id = %s and 
                    semester = %s and 
                    year = %s;""", (course_id, sec_id, semester, year))
    sec = cur.fetchone()

    # Fetches the number of students already registered for the desired course and compares it to the room capacity.  If the section is full,
    # returns false to fail the conditional in register and prints and error message.
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
    # Calls each of the test funtions to check if registration is possible
    if not register_prerequisites(cur, student_id, course_id):
        return
    if not register_schedule(cur, student_id, course_id, sec_id, semester, year):
        return
    if not register_avalability(cur, course_id, sec_id, semester, year):
        return

    # Attempts to execute the registration query, and prints error(s) if it fails
    try:
        cur.execute ("""insert into takes(ID, course_id, sec_id, semester, year) 
                     values (%s, %s, %s, %s, %s);""", (student_id, course_id, sec_id, semester, year))
        print("Registration complete!")
    except psycopg2.errors.ForeignKeyViolation:
        print("No such ID, course, or section.")
    except psycopg2.Error as e:
        print("Error")
        print(e)
    
def register_handler(cur):
    # Calls register_prompts(), saves user input, and attempts to call register() with it.  If it fails, passes on the error.
    student_id,course_id,sec_id,semester,year = register_prompts()

    try:
        register(cur, student_id, course_id, sec_id, semester, year)
        # conn.commit()

    except psycopg2.Error as e:
        print("Error")
        print(e)
        # conn.rollback()

def main():
    print("wokring")
    # Prints the snazzy header and establishes the menu loop, accepting user input and calling query functions as needed.
    try: 
        print("working2")
        conn = psycopg2.connect(dbname="team1")
        cur = conn.cursor()

        print()
        print("#######                        #      #     #                                                       ######                                                  ")
        print("   #    ######   ##   #    #  ##      #     # #    # # #    # ###### #####   ####  # ##### #   #    #     #   ##   #####   ##   #####    ##    ####  ###### ")
        print("   #    #       #  #  ##  ## # #      #     # ##   # # #    # #      #    # #      #   #    # #     #     #  #  #    #    #  #  #    #  #  #  #      #      ")
        print("   #    #####  #    # # ## #   #      #     # # #  # # #    # #####  #    #  ####  #   #     #      #     # #    #   #   #    # #####  #    #  ####  #####  ")
        print("   #    #      ###### #    #   #      #     # #  # # # #    # #      #####       # #   #     #      #     # ######   #   ###### #    # ######      # #      ")
        print("   #    #      #    # #    #   #      #     # #   ## #  #  #  #      #   #  #    # #   #     #      #     # #    #   #   #    # #    # #    # #    # #      ")
        print("   #    ###### #    # #    # #####     #####  #    # #   ##   ###### #    #  ####  #   #     #      ######  #    #   #   #    # #####  #    #  ####  ###### \n")
        
        print("Welcome to the Team1 University Database System! (c) 2024, all rights reserved.\n")
        
        while True:
            print("A: Generate list of advisees and advisors")
            print("I: Add an instructor to the database")
            print("T: Generate a student's transcript")
            print("C: Generate a course list for a term")
            print("R: Register a student for a course")
            print("Q: Close the connection and exit the program\n")

            user_in = ""
            user_in = input("Enter your selection: ")
            user_in = user_in.upper()
        
            if user_in == "A":
                advisor_list(cur)
            elif user_in == "I":
                try:
                    insert_instructor(cur)
                    conn.commit() 
                except Exception:
                    conn.rollback()
            elif user_in == "T":
                try:
                    generate_transcript(cur)
                    conn.commit()
                except Exception:
                    conn.rollback()

            elif user_in == "C":
                generate_course_list(cur)
            elif user_in == "R":
                register_handler(cur)
            elif user_in == "Q":
                break
            else:
                print("Invalid input, please try again\n")
    except psycopg2.Error as e:
        print(e)
    finally:
        conn.close()

if __name__=="__main__":
    main()
