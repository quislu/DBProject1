import psycopg2

# Generate course list
# inputs = semester, year

def prompts():
    semester = input("Enter semester: ")
    year = input("Enter year: ")
    return semester, year

def generate_list(cur, semester, year):
    print('Generating course list')
    cur.execute("""select * from section
                   where semester = %s and year = %s""",(semester, year))
    for line in cur:
        print(line[0], line[1], line[2], line[3], line[4], line[5], line[6])

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