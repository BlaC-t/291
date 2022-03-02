
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

    cursor.execute('''drop table if exists editors''')
    cursor.execute('''drop table if exists follows''')
    cursor.execute('''drop table if exists watch''')
    cursor.execute('''drop table if exists sessions''')
    cursor.execute('''drop table if exists customers''')
    cursor.execute('''drop table if exists recommendations''')
    cursor.execute('''drop table if exists casts''')
    cursor.execute('''drop table if exists movies''')
    cursor.execute('''drop table if exists moviePeople''')

    editors_query = '''
                        CREATE TABLE editors (
                            eid char(4),
                            pwd text,
                            primary key (eid)
                        );
                    '''

    follows_query = '''
                            CREATE TABLE follows (
                                eid char(4),
                                pid char(4),
                                primary key (eid, pid),
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
                                    watch int,
                                    recommended int,
                                    primary key (watch, recommended),
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
                                CREATE TABLE follows (
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

def data():

def main():

if __name__ == "__main__":
    main()