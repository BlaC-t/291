import sqlite3
import time
import hashlib

connection = None
cursor = None


def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_key=ON; ')
    connection.commit()

    return


def define_tables():
    global connection, cursor

    # drop table
    cursor.execute('''drop table if exists editors''')
    cursor.execute('''drop table if exists follows''')
    cursor.execute('''drop table if exists watch''')
    cursor.execute('''drop table if exists sessions''')
    cursor.execute('''drop table if exists customers''')
    cursor.execute('''drop table if exists recommendations''')
    cursor.execute('''drop table if exists casts''')
    cursor.execute('''drop table if exists movies''')
    cursor.execute('''drop table if exists moviePeople''')

    # creating table
    editors_query = '''
                        CREATE TABLE editors (
                            eid char(4),
                            pwd text,
                            primary key (eid)
                        );
                    '''

    follows_query = '''
                        CREATE TABLE follows (
                            cid char(4),
                            pid char(4),
                            primary key (cid, pid),
                            foreign key (cid) references customers,
                            foreign key (pid) references moviePeople
                    );
                    '''

    watch_query = '''
                        CREATE TABLE watch (
                            sid int,
                            cid char(4),
                            mid int,
                            primary key (sid, cid, mid),
                            foreign key (sid, cid) references sessions,
                            foreign key (mid) references movies
                        );
                    '''

    sessions_query = '''
                        CREATE TABLE sessions (
                            sid int,
                            cid char(4),
                            sdate date,
                            duration int,
                            primary key (sid, cid),
                            foreign key (cid) references customers on delete cascade
                        );
                    '''

    customers_query = '''
                        CREATE TABLE customers (
                            cid char(4),
                            name text,
                            pwd text,
                            primary key (cid)

                        );
                        '''

    recommendations_query = '''
                                CREATE TABLE recommendations (
                                    watched int,
                                    recommended int,
                                    primary key (watched, recommended),
                                    foreign key (watched) references movies,
                                    foreign key (recommended) references movies
                                );
                            '''

    casts_query = '''
                    CREATE TABLE casts (
                        mid int,
                        pid char(4),
                        role text,
                        primary key (mid, pid),
                        foreign key (mid) references movies,
                        foreign key (pid) references moviePeople
                    );
                    '''

    movies_query = '''
                    CREATE TABLE movies (
                        mid int,
                        title text,
                        year int,
                        runtime int,
                        primary key (mid)
                    );
                    '''

    moviePeople_query = '''
                            CREATE TABLE moviePeople (
                                pid char(4),
                                name text,
                                birthYear int,
                                primary key (pid)
                            );
                        '''
    cursor.execute(editors_query)
    cursor.execute(follows_query)
    cursor.execute(watch_query)
    cursor.execute(sessions_query)
    cursor.execute(customers_query)
    cursor.execute(recommendations_query)
    cursor.execute(casts_query)
    cursor.execute(movies_query)
    cursor.execute(moviePeople_query)
    connection.commit()

    return


def insert_data():
    global connection, cursor

    editors_data = '''
                    INSERT INTO editors(eid, pwd) VALUES
                        ('e100', 1001),
                        ('e200', 1945);
                        '''
    customers_data = '''
                        INSERT INTO customers(cid, name, pwd) VALUES
                            ('c100', 'Richard He', 1234),
                            ('c200', 'Eric Kim', 2345);
                            '''
    cursor.execute(editors_data)
    cursor.execute(customers_data)
    connection.commit()

    return


def login_screen():
    global connection, cursor

    good_name = False
    user_name = input("Enter in your user name:  ")
    cursor.execute('SELECT e.eid FROM editors e WHERE e.eid = :id', {"id": user_name})
    editors_eid = cursor.fetchone()
    print(editors_eid[0])

    while not good_name:

        user_name = input("Enter in your user name:  ")

        if "e" or "c" not in user_name:
            print("Please enter in the correct user name!  ")
        else:
            good_name = True
            pwd = input("Enter in your password:  ")
            if "e" in user_name:
                cursor.execute('SELECT e.pwd FROM editors e WHERE e.eid = :id', {"id": user_name})
                editors_id = cursor.fetchone()
                print(editors_id)
            if "c" in user_name:
                ...


def editors_menu():
    ...


def customers_menu():
    ...


def main():
    global connection, cursor
    path = "./mp1.db"
    connect(path)
    define_tables()
    insert_data()

    end = False

    while not end:
        welcome = input("Welcome, do you want to log in (Y) or exit (N):  ")
        if end:
            exit()
        elif welcome.lower() == "n":
            end = True
        elif welcome.lower() == 'y':
            login_screen()
        else:
            print("Please follow instruction! \n ")


if __name__ == "__main__":
    main()
