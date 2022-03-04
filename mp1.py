from distutils.command.clean import clean
import sqlite3
import time
import hashlib
import getpass
import os,sys


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
    # set up user input screen
    opt_format=[2,['id_name','password',],['password'],'user login:','']
    user_input=['','']
    login_sucess=False
    # info input loop
    while not login_sucess:
        user_input,selection=list_input_menu(opt_format,user_input)
        if selection=='b':
            return
        # check user name
        if 'e' not in user_input[0] and 'c' not in user_input[0]:
            input("1:sorry, we did not find a matching userid and password.\nenter to continue ")
        elif 'e' in user_input[0]:
            cursor.execute('SELECT e.pwd FROM editors e WHERE e.eid = :id', {"id": user_input[0]})
        else: # 确定不用把c写上去嘛
            cursor.execute('SELECT c.pwd FROM customers c WHERE c.cid = :id', {"id": user_input[0]})
        useridrec = cursor.fetchone()
        # find if the customer exist
        if (useridrec == None) or (type(useridrec)!= tuple):
            input("2:sorry, we did not find a matching userid and password.\n enter to continue ")
        # password matching
        if  (user_input[1]!=useridrec[0]) :
            input("3:sorry, we did not find a matching userid and password.\n enter to continue")
        else:
            login_sucess=True
    # real person validaed 
    if 'c' in user_input[0]:
        customers_menu(user_input[0])
    elif 'e' in user_input[0]:
        editors_menu(user_input[0])
    return

def editors_menu(eid):
    os.system('clear')
    print("Login in as editor {}".format(eid))
    input("press enter to exit")
    return


def customers_menu(cid):
    os .system('clear')
    print("Login in as customer {}".format(cid))
    input("press enter to exit")
    return

def list_input_menu(print_format,user_input):
    # this list will be present a list of blank space like this:
    # user name:
    # password:(hide if serveic bridge requested)
    # number of argument areallow to be set
    # argv1=[num input,[nmae of input],[hideen password],msg1(before list),msg2]
    # argv2=[previously input]
    selection =''
    # while use did not quite or submit
    while selection.lower() not in ['b','s']:
        # header printing
        os.system('clear')
        print(print_format[3])
        print('-'*20)
        # each line completed information printing
        for i in range(print_format[0]):
            if (print_format[1][i] not in print_format[2]) or user_input[i]=='':
                print('{}: {:<15}    {}'.format(i,print_format[1][i],user_input[i]))
            else:
                print('{}: {:<15}    {}'.format(i,print_format[1][i],'*****'))
        print('B: go back\nS: submit\n')
        # user promote their input and input check
        selection=input('your selection> ')
        if selection>='0' and selection<='9':
            # number validation
            if int(selection)>=print_format[0] or (int(selection)<0):
                print('invalid selection, enter to continue')
                input()
            # if password hidden
            else:
                if print_format[1][int(selection)] not in print_format[2]:
                    user_input[int(selection)]=input('{}: '.format(print_format[1][int(selection)]))
                else:
                    user_input[int(selection)]=getpass.getpass('{}: '.format(print_format[1][int(selection)]))
        elif selection.lower() not in ['b','s']:
            print('invalid selection, enter to continue')
            input()
    return user_input,selection                    

def register_service_bridge():
    global connection,cursor
    # set up register
    opt_format=[3,['id_name','user name','password',],['password'],'new user register:','']
    user_input=['','','']
    register_sucess=False
    while not register_sucess:
        # request information
        missed=False
        user_input,selection=list_input_menu(opt_format,user_input)
        if selection=='b':
            return
        for i in range(len(user_input)):
           if user_input[i]=='':
               missed=True
        if missed:
            input('some information not complete\n press enter to continue')
        else:
            # find if the user are in conflict
            if 'e' in user_input[0]:
                cursor.execute('SELECT e.eid FROM editors e WHERE e.eid = :id', {"id": user_input[0]})
            else:
                cursor.execute('SELECT c.pwd FROM customers c WHERE c.cid = :id', {"id": user_input[0]})
            useridrec = cursor.fetchone()
            # input the information into database
            if useridrec==None:
                if 'e' in user_input[0]:
                    txt=''' INSERT INTO editors VALUES ('{}', '{}');'''.format(user_input[0],user_input[2])
                    print(txt)                                                      
                    cursor.execute(txt)
                    connection.commit()
                    register_sucess=True
                    input('Sucess! use {} as your login credentials'.format(user_input[0]))
                if 'c' in user_input[0]:
                    txt=''' INSERT INTO customers VALUES ('{}', '{}', '{}');'''.format(user_input[0],user_input[1],user_input[2])
                    cursor.execute(txt)
                    connection.commit()
                    register_sucess=True
                    input('Sucess! use {} as your login credentials'.format(user_input[0]))
            else:
                input('id exist,enter to remodify your information')

def main():
    global connection, cursor
    # clean the screen
    os.system('clear')
    #print(sys.argv)
    if len(sys.argv)==1:
        path = "./mp1.db"
    else:
        path = sys.argv[1]
    connect(path)
    if len(sys.argv)==1:
        define_tables()
        insert_data()
    
    welcome=''
    while welcome.lower()!='e':
        print('Welcome screen','\n connected to database {}'.format(path))
        print('-'*20)
        print('1:exising customer and editor log in\n2:register\nE:exit\n')
        
        if welcome.lower() not in ['1', '2', 'e','']:
            print("Please follow instruction! \n ")
        welcome = input("Enter your selection: ")
        if welcome.lower() == '1':
            login_screen()
        elif welcome.lower() == '2':
            register_service_bridge()
        os.system('clear')

if __name__ == "__main__":
    main()
