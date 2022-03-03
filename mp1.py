from distutils.command.clean import clean
import sqlite3
import time
import hashlib
import getpass
import os


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
    cursor.execute(''' INSERT INTO editors(eid, pwd) VALUES ('e100', 1001);''')
    cursor.execute(''' INSERT INTO editors(eid, pwd) VALUES ('e200', 1945);''')
    cursor.execute(''' INSERT INTO customers(cid, name, pwd) VALUES ('c100', 'Richard He', 1234);''')
    cursor.execute(''' INSERT INTO customers(cid, name, pwd) VALUES ('c200', 'Eric Kim', 2345);''')
    connection.commit()

    return


def login_screen():
    global connection, cursor
    user_name=input('User name:')
    password= getpass.getpass('Pass word')
    print('you wrote(print as test purpose):',user_name,password)
    # check user name
    if 'e' not in user_name and 'c' not in user_name:
        print("1:sorry, we did not find a matching userid and password.")
        return
    elif 'e' in user_name:
        cursor.execute('SELECT e.pwd FROM editors e WHERE e.eid = :id', {"id": user_name})
    else:
        cursor.execute('SELECT c.pwd FROM customers c WHERE c.cid = :id', {"id": user_name})
    useridrec = cursor.fetchone()
    
    # find if the customer exist
    if (useridrec == None) or (type(useridrec)!= tuple):
        print("2:sorry, we did not find a matching userid and password.")
        return
    # password matching
    if  (password!=useridrec[0]) :
        print("3:sorry, we did not find a matching userid and password.")
        return
    # real person validaed 
    if 'c' in user_name:
        customers_menu(user_name)
    elif 'e' in user_name:
        editors_menu(user_name)
    os.system('clear')
    return

def editors_menu(eid):
    print("Login in as editor :id",{"id":eid})
    input("press enter to exit")
    return


def customers_menu(cid):
    print("Login in as custimer :id",{"id":cid})
    input("press enter to exit")
    return
    


def main():
    global connection, cursor
    # clean the screen
    os.system('clear')
    path = "./mp1.db"
    connect(path)
    define_tables()
    insert_data()

    welcome=''

    while welcome.lower()!='n':
        welcome = input("Welcome, do you want to log in (Y) or exit (N):  ")
        if welcome.lower() == 'y':
            login_screen()
        elif welcome.lower() != 'n':
            print("Please follow instruction! \n ")
    os.system('clear')

if __name__ == "__main__":
    main()
