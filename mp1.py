from ast import DictComp, Return
from distutils.command.clean import clean
from itertools import count
import sqlite3
import time,datetime
import hashlib
import getpass
import os,sys


connection = None
cursor = None
userdict={}

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
        # let the login in screen get the user input
        user_input,selection=list_input_menu(opt_format,user_input)
        # user selected to return the main menu
        if selection=='b':
            return
        # check user name, if e and c are both not in user name
        if 'e' not in user_input[0] and 'c' not in user_input[0]:
            input("1:sorry, we did not find a matching userid and password.\nenter to continue ")
            continue
        elif 'e' in user_input[0]:   # get information from the database of the username/login
            cursor.execute('SELECT e.pwd FROM editors e WHERE e.eid = :id', {"id": user_input[0]})
        else:
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
    sessionID=''
    # header line format printout
    txt1="Login in as customer {}".format(cid)
    txt2="no session ID assiged this moment"
    info=[['Start a session'],['Search for movie'],['end watching a movie'],['end the session']]
    header=[len(info),0,[],False,txt1,txt2]
    userinput=''
    userdict.clear()  # clean the dictionary
    while str(userinput).lower()!='b':
        os.system('clean')
        if sessionID == '':
            txt2="no session ID assiged this moment"
        else:
            txt2="Current session ID is:{}.".format(sessionID)
        header[-1]=txt2
        userinput=select_menu(info,header)
        if str(userinput) not in ['0','1','2','3','b']:
            print("Please follow instruction! \n ")
        elif str(userinput) == '0':
            sessionID = create_new_session(cid,sessionID)
        elif str(userinput) == '1':
            search_movie(cid,sessionID)
        elif str(userinput) == '2':
            print(2)
            input()
        elif str(userinput) == '3':
            sessionID=end_session(sessionID)
            if sessionID=='':
                userdict.clear()
            # if returning sessionID it means session still have something unable to end it yet
            print(3)
            input()
    return

def create_new_session(cid,sessionID):
    global connection, cursor,userdict
    if sessionID!='':
        input('There is a exist session ID found.\n press enter to continue'.format(sessionID))
        return sessionID
    cursor.execute('SELECT max(sid),count(*) FROM sessions ORDER by sid DESC') # find max id,and count
    dbreturn=cursor.fetchone()
    if dbreturn[1]==0:
        sessionID=1
    else:
        sessionID=dbreturn[0]+1
    userdict['session_start']=time.time()
    txt = "insert into sessions values ({}, '{}', '{}', NULL);".format(sessionID,cid,str(datetime.date.today()))
    cursor.execute(txt)
    connection.commit()
    input('new session ID {}./n enter to continue'.format(sessionID))
    return sessionID

def end_session(sessionID):
    global connection, cursor,userdict
    if sessionID=='':
        input('no current session,enter to back to the last menu')
    # check if any movie not end
    txt = '''SELECT count(*) FROM sessions,watch
             WHERE sessions.sid=watch.sid 
             and watch.duration is NULL
             and watch.sid={}'''.format(sessionID)
    cursor.execute(txt)
    dbreturn=cursor.fetchone()
    if dbreturn[0]>0:
        input('You have {} not yet end watching,please end all wating before end session.\nPress enter to continue'.format(dbreturn[0]))
        return sessionID
    # update information
    duration=int((time.time()-userdict['session_start'])/60)
    txt2='UPDATE sessions SET duration={} WHERE sid={}'.format(duration,sessionID)
    cursor.execute(txt2)
    connection.commit()
    input('Session {} ended.\n press enter to continue'.format(sessionID))
    return ''

def search_movie(cid,sessionID):
    global connection,cursor
    opt_format=[3,['title','cast member name','member role',],[],'select your movie by keyword:','not all the entry are mandortry']
    user_input=['','','']
    selected=False
    dbreturn=[]
    while not selected:
        user_input,selection = list_input_menu(opt_format,user_input)
        if selection=='b':
            return
        # data error check here
        for i in range(len(user_input)):
            if user_input[i]!='':
                break
            elif i == len(user_input)-1:
                input('at least one have to type it\n enter to continue')
                continue
        print(user_input)
        count_sel=0
        un_txt= '''union all '''
        txt1= '''select movies.mid,movies.title,movies.year,movies.runtime 
                from movies
                inner join ('''
        txt_con=['''SELECT movies.mid 
                FROM movies
                WHERE title like "%{}%" '''
                ,'''SELECT casts.mid 
                FROM moviePeople,casts
                WHERE moviePeople.pid=casts.pid
                and moviePeople.name like "%{}%" '''
                ,   '''SELECT casts.mid 
                from casts
                WHERE role like "%{}%" ''']
        txt5=''') matchmov on movies.mid=matchmov.mid
                group by movies.mid
                ORDER by count(*) DESC'''.format(user_input[0],user_input[1],user_input[2])
        for i in range(len(user_input)):
            if count_sel>=1 and user_input[i]!='':
                txt1=txt1+un_txt
            if user_input[i]!='':
                txt1=txt1+txt_con[i].format(user_input[i])
                count_sel+=1
        txt1=txt1+txt5
        print(txt1)
        cursor.execute(txt1)
        dbreturn.append(cursor.fetchone())
        if dbreturn[0] == None:
            input("no result match return to input menu\n press enter to continue")
            continue
        else:
            selected=True
    selected=False
    while dbreturn[-1]!=None:
        dbreturn.append(cursor.fetchone())
    o2=cursor.description
    col_til=[]
    for i in range(len(o2)):
        col_til.append(o2[i][0])
    print(col_til)
    dbreturn.pop()
    print(dbreturn)
    selected=False
    header=[len(dbreturn),5,col_til,True,'selected your movie','']
    userinput=''
    while not selected and str(userinput).lower()!='b':
        user_input=select_menu(dbreturn,header)
        if str(user_input).lower()=='b':
            return
        print(dbreturn[user_input])
        watch_movie_service(cid,sessionID,dbreturn[user_input][0])
    return
    
def watch_movie_service(cid,sessionID,mid):
    global cursor,connection,userdict
    cursor.execute('''SELECT * FROM movies WHERE mid={}'''.format(mid))
    movied=cursor.fetchone()
    print('op1')
    txt1='Title:    {}\nmid:      {}\nPublish at {}\nLength:   {}\n'.format(movied[1],movied[0],movied[2],movied[3])
    extxt=txt1
    txt1=txt1+'-'*30+'\n'
    txt1=txt1+"{:<25} {:<25} {:<8}".format('real name','role','birthYear')+'\n'
    cursor.execute('''SELECT moviePeople.name,casts.role,moviePeople.birthYear 
                        FROM casts inner join moviePeople 
                        on moviePeople.pid=casts.pid WHERE mid={}'''.format(mid))
    print('op2')
    peodt=''
    while peodt != None:
        peodt=cursor.fetchone()
        if peodt != None:
            txt2="{:<25} {:<25} {:<8}\n".format(peodt[0],peodt[1],peodt[2])
            txt1=txt1+txt2
    txt1=txt1+'-'*30+'\n'
    print('op3')
    cursor.execute('''SELECT count(DISTINCT cid) 
                      FROM watch,movies WHERE movies.mid=watch.mid 
                      AND watch.mid={} AND (movies.runtime/2)<=watch.duration'''.format(mid))
    cusdt=cursor.fetchone()
    print('op4')
    if cusdt==None:
        txt1=txt1+'0 Customer watched this movie\n'
    else:
        txt1=txt1+'{} Customer watched this movie\n'.format(cusdt[0])
    txt1=txt1+'-'*30+'\n'
    print('op5')
    info=[['follow a cast'],['start watching']]
    header=[len(info),0,[],False,txt1,'']
    inputsel=''
    while str(inputsel).lower()!='b':
        inputsel=select_menu(info,header)
        if inputsel==0:
            follow_moviepeople_service(extxt,cid,mid)
        elif sessionID=='' and inputsel==1:
            input('sorry we did not find your session, you will be send back to main menu.\n press enter to continue.')
        else:
            start_watch(cid,sessionID,mid)
    return

def follow_moviepeople_service(extxt,cid,mid):
    global connection, cursor
    done=False
    extxt='Select the movie People you want to follow:\n'+extxt
    cursor.execute('''SELECT moviePeople.pid,moviePeople.name,casts.role,moviePeople.birthYear 
                      FROM casts inner join moviePeople 
                      on moviePeople.pid=casts.pid WHERE mid={}'''.format(mid))
    print('op2')
    peodt=[cursor.fetchone()]
    while peodt[-1] != None:
        peodt.append(cursor.fetchone())
    o2=cursor.description
    col_til=[]
    for i in range(len(o2)):
        col_til.append(o2[i][0])
    peodt.pop()# last one always empty
    header=[len(peodt),5,col_til,True,extxt,'']
    userinput=''
    while str(userinput).lower()!='b':
        user_input=select_menu(peodt,header)
        if str(user_input).lower()=='b':
            return
        else:
            cursor.execute('''SELECT * FROM follows WHERE cid='{}' and pid='{}' '''.format(cid,peodt[user_input][0]))
            res=cursor.fetchone()
            if res!=None:
                input("Sorry, you alreadr follow{}.\npress enter to exit.".format(peodt[user_input][1]))
            else:
                txt = "insert into follows values ('{}', '{}');".format(cid,peodt[user_input][0])
                cursor.execute(txt)
                connection.commit()
                input("you are now  following {}.\npress enter to exit.".format(peodt[user_input][1]))

def start_watch(cid,sessionID,mid):
    global connection, cursor,userdict
    cursor.execute('''SELECT * FROM watch where cid='{}' and mid={} and sid={}'''().format(cid,mid,sessionID))
    dbreturn=cursor.fetchone()
    # it means the movie already started or finshed watching in this session
    if dbreturn is not None:
        input('you are already watching or finshed this movie in this session\n press enter to gp back')
        return
    cursor.execute(txt = "insert into watch values ({}, '{}',{},{});".format(sessionID,cid,mid,'NULL'))
    userdict[mid]=time.time()
    connection.commit()
    input('your movie start watching now!')
    return

def end_watch(cid,sessionID):
    global connection, cursor,userdict
    if sessionID=='':
        input('session ID not found\n press enter to continue')
        return
    cursor.execute('''SELECT watch.mid,movies.title,movies.year 
                      FROM watch,movies
                      WHERE  movies.mid=watch.mid
                      and cid='{}' and sid={} and watch.mid is NULL'''.format(cid,sessionID))
    dbreturn=[cursor.fetchone()]
    if dbreturn[0] is None:
        input('no watch found\n press enter to continue')
        return
    while dbreturn[-1] is not None:
        dbreturn.append(cursor.fetchone())
    dbreturn.pop()
    o2=cursor.information
    title=[]
    for i in range(len(o2)):
        title.append(o2[i][0])
    header=[len(dbreturn),5,title,False,'select the, movie that you want to watch','']
    re=select_menu(dbreturn,header)
    if str(re).lower()=='b':
        return
    duration=int ((time.time() - userdict[dbreturn[re][0]])/60)
    cursor.execute('''UPDATE watch SET duration={} 
                      WHERE cid='{}' and mid={} and sid={} '''.format(duration,cid,dbreturn[re][0],sessionID))
    try:
        del userdict[dbreturn[re][0]]
    except KeyError:
        pass
    input('movie {} end watching.enter to exit'.format(dbreturn[re][1]))
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
                print('{}: {:<15}    {}'.format(i+1,print_format[1][i],user_input[i]))
            else:
                print('{}: {:<15}    {}'.format(i+1,print_format[1][i],'*****'))
        print(print_format[-1])
        print('B: go back\nS: submit\n')
        # user promote their input and input check
        selection=input('your selection> ')
        if selection>='0' and selection<='9':
            # number validation
            if int(selection)>print_format[0] or (int(selection)<=0):
                print('invalid selection, enter to continue')
                input()
            # if password hidden
            else:
                selection=str(int(selection)-1)
                if print_format[1][int(selection)] not in print_format[2]:
                    user_input[int(selection)]=input('{}: '.format(print_format[1][int(selection)]))
                else:
                    user_input[int(selection)]=getpass.getpass('{}: '.format(print_format[1][int(selection)]))
        elif selection.lower() not in ['b','s']:
            print('invalid selection, enter to continue')
            input()
    return user_input,selection.lower()                    

def select_menu(info,header):
    # header=[len(info),3,['name','age','pp'],False,txt1,txt2]
            # total line #title each col    #show col(T/F)
                      # showing each page         #(BF) (AF)
    selected=False
    page=0
    #  present index overflow
    if header[1]>header[0] or header[1]==0:
        header[1]=header[0]
    # calc finding the max page
    max_page=int(header[0]/header[1])
    if (header[0]%header[1])==0:
        max_page-=1
    selection=''
    # when not selected keeop brwing
    while not selected:
        #header printing
        os.system('clear')
        print(header[4])
        print('-'*20)
        # header printing requested
        if header[3]:
            txt='#   '
            for i in range(len(info[0])):
                txt+='{:<25} '.format(header[2][i])
            print(txt)
        start=page*header[1]
        end= (page+1)*header[1]
        # sometime last page not full
        if (end>header[0]):
            end = header[0]
        for y in range(start,end,1):
            txt='{:<3} '.format(y-page*header[1]+1)
            for x in range(len(info[0])):
                if len(str(info[y][x]))<=25:
                    txt+='{:<25} '.format(info[y][x])
                else:
                    txt+='{:<23}.. '.format(info[y][x][:23])
            print(txt)
        # printing number of option key allow
        if header[-1]!=None:
            
        if max_page!=0:
            print('\nshowing {} - {} of {}'.format(start,end,header[0]))
            print('''\nL last page\nN next page''')
        print('''\n<int> number of option\nB back\n''')
        # get the user input
        selection=input('indicate your choice> ').lower()
        # exit ,flip page
        if selection == 'b':
            return selection
        elif selection == 'n' and page<max_page:
            page+=1
        elif selection =='l' and page>=1:
            page-=1
        else: # number validation
            try:
                if int(selection)-1<0:
                    input("invalid input\nenter to continue")
                    continue
                elif int(selection)-1>=header[1]:
                    input("invalid input\nenter to continue")
                    continue
            except:
                input("invalid input\nenter to continue")
                continue
            selected=True
            break
    return int(selection)-1+header[1]*page


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
    info=[['log in'],['register']]
    txt1='Welcome screen\nconnected to database {}'.format(path)
    header=[len(info),0,[],False,txt1,'']
    welcome=''

    while str(welcome).lower()!='b':
        welcome=select_menu(info,header)
        if welcome not in [0, 1,'b']:
            print("Please follow instruction! \n ")
        if welcome == 0:
            login_screen()
        elif welcome == 1:
            register_service_bridge()
    connection.close()

if __name__ == "__main__":
    main()




