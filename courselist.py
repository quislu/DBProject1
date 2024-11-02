import psycopg2

# Generate course list
# inputs = semester, year

def prompts():
    semester = input("Enter semester: ")
    year = input("Enter year: ")
    return semester, year

def get_course_name(cur, c_id):
    cur.execute("""select title, credits from section natural join course
                   where course_id = %s""", (c_id,))
    course_info = cur.fetchone()
    return course_info[0], str(course_info[1])


def get_sections(cur, semester, year):
    cur.execute("""select * from section
                   where semester = %s and year = %s
                   order by course_id""",(semester, year))
    sections = []
    for line in cur:
        sections += [[line[i] for i in range(0, len(line))]]
    return sections

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
        # start = f"{time_slot[i][1]}:{time_slot[i][2]}"
        # end = f"{time_slot[i][3]}:{time_slot[i][4]}"
        time_slot[i] = [time_slot[i][0], f"{time_slot[i][1]}:{time_slot[i][2]}",f"{time_slot[i][3]}:{time_slot[i][4]}"]
    return time_slot
    


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