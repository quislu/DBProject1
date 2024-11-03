import psycopg2

# generate transcript for given student id
# Generate transcript. Prompt for a student ID and present a summary of that
# student's information followed by a list of every class taken by that student. Classes
# should be grouped by and in order of semester. For each class, the transcript should
# display the course ID, section number, course name, credits, and grade. In each
# semester group, display the GPA for that semester. At the end, display the current
# cumulative GPA. For example, the transcript for Zhang might appear as follows.
# Formatting details are at your discretion. Impress us.

def prompt():
    s_id = input("Enter the student id: ")
    return s_id

#query = "insert into instructor values (%s, %s, %s, %s);"

def transcript(cur, id):
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
        
    except psycopg2.error:
        print("Transcript generation error")
    


def main():
    conn = psycopg2.connect(dbname="team1")
    cur = conn.cursor()

    s_id = prompt()
    try:
        transcript(cur, s_id)
        conn.commit()
    except psycopg2.Error as e:
        print("Error")
        print(e)
        conn.rollback()
    finally:
        conn.close()

main()
