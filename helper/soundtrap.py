def make_soundtrap_accounts():
    """
    Reads csv from google forms, reconciles bad form data, outputs a csv for
    soundtrap and updates the csv of all student accounts.
    """

    with open('/Users/JohnDeVries/Downloads/permission.csv', 'r') as csvfile:
        rd = csv.reader(csvfile)

        with open('soundtrap_input.csv', 'w') as csvout:
            wr = csv.writer(csvout)

            matches = []
            for rd_row in rd:
                if rd_row[4][0] == 'D':
                    continue

                for st in helper.students:
                    if st.last_name == rd_row[3] and st.first_name == rd_row[2]:
                        matches.append(st)
                    else:
                        print(f'no match for {rd_row[2] + ' ' + rd_row[3]}')

                if rd_row[3] not in [s.last_name for s in helper.students]:
                    print(f'***no match {rd_row}')

            wr.writerow(['First name', 'Last name', 'Email', 'Password'])

            with open('with_message.csv', 'w') as rich_csvout:
                wr2 = csv.writer(rich_csvout, delimiter=';')
                wr2.writerow(['First name', 'Last name', 'Student ID', 'Homeroom', 'Email', 'Password', 'Message'])
                for st in matches:

                    st.email = st.email.lower()
                    password = st.last_name + st.first_name + str(randint(10, 99))
                    password = password.lower()

                    wr.writerow([
                        st.first_name,
                        st.last_name,
                        st.email,
                        password,
                    ])

                    wr2.writerow([
                        st.first_name,
                        st.last_name,
                        st.student_id,
                        st.homeroom,
                        st.email,
                        password,
                        template,
                    ])