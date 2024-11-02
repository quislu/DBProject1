import psycopg2

def prompts():
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

def generate_list(cur, semester, year):
    course_list = []
    print('Generating course list')
    cur.execute("""select * from section
                   where semester = %s and year = %s
                   order by course_id""",(semester, year))
    sections = get_sections(cur, semester, year)
    for i in range(0,len(sections)):
        sections[i][2], sections[i][3] = get_course_name(cur, sections[i][0])
        sections[i][6] = get_time_slots(cur, sections[i][6])
        sections[i].append(get_capacity(cur, sections[i][4], sections[i][5]))
        sections[i].append(get_enrollment(cur, sections[i][0], sections[i][1], semester, year))
        print(sections[i])

def main():
    conn = psycopg2.connect(dbname="team1")
    cur = conn.cursor()

    semester,year = prompts()

    try:
        generate_list(cur, semester, year)
        conn.commit()

    except psycopg2.Error as e:
        print("Error")
        print(e)
        conn.rollback()

    finally:
        conn.close()
main()