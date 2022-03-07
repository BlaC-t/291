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
    userinput=''# see line 206, detact if end while loop needed
    userdict.clear()  # clean the dictionary
    while str(userinput).lower()!='b':
        os.system('clean')
        if sessionID == '':
            txt2="no session ID assiged this moment"
        else:
            txt2="Current session ID is:{}.".format(sessionID)
        header[-1]=txt2
        # print to get get the user response
        userinput=select_menu(info,header)
        if str(userinput) not in ['0','1','2','3','b']:
            print("Please follow instruction! \n ")
        elif str(userinput) == '0':    #create new session
            sessionID = create_new_session(cid,sessionID)
        elif str(userinput) == '1':    #search movie
            search_movie(cid,sessionID)
        elif str(userinput) == '2':    # end watching movie
            # still uder test
            end_watch(cid,sessionID)
        elif str(userinput) == '3':    # end session
            sessionID=end_session(sessionID)
            if sessionID=='':          # clean everything in the dictionary
                userdict.clear()
            # if returning sessionID it means session still have something unable to end it yet
    return

def create_new_session(cid,sessionID):
    global connection, cursor,userdict
    # if a new session exist,let user end watching all the movie
    if sessionID!='':
        input('There is a exist session ID found.\n press enter to continue'.format(sessionID))
        return sessionID
    # find the max session id and plus one, so there will be no repeat session
    cursor.execute('SELECT max(sid),count(*) FROM sessions ORDER by sid DESC') # find max id,and count
    dbreturn=cursor.fetchone()
    # when there are session in the history
    if dbreturn[1]==0:
        sessionID=1
    else: # just add one to avoid repat
        sessionID=dbreturn[0]+1
    # put the start time in the dictionary
    userdict['session_start']=time.time()
    # create new session record
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
    dbreturn,tille=fetch_info(txt)
    if dbreturn[0][0]>0: # count always return a number so no none deact here
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
    # here is the pg1, let the user decide what keyword they should keyin(at least one)
    opt_format=[3,['title','cast member name','member role',],[],'select your movie by keyword:','not all the entry are mandortry']
    user_input=['','','']
    selected=False
    while not selected:
        # get input here
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
        # here is ateset code remember to delete the code
        print(user_input)
        count_sel=0
        # according to the user inputed,change the sql querry to what it needed to
        # line setup
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
                ORDER by count(*) DESC'''
        # detection and bind them in to one sql query
        for i in range(len(user_input)):
            if count_sel>=1 and user_input[i]!='':
                txt1=txt1+un_txt
            if user_input[i]!='':
                txt1=txt1+txt_con[i].format(user_input[i])
                count_sel+=1
        # add the sort into the line as well
        txt1=txt1+txt5
        # fetch informaion and return a list of multi entries
        dbreturn,col_til=fetch_info(txt1)
        # if no matching,return to last menu
        if len(dbreturn) == 0:
            input("no result match return to input menu\n press enter to continue")
            continue
        else:
            selected=True
    # print(dbreturn)  # test purpose
    selected=False
    header=[len(dbreturn),5,col_til,True,'selected your movie','']
    userinput=''
    # let user select the movie
    while not selected and str(userinput).lower()!='b':
        user_input=select_menu(dbreturn,header)
        if str(user_input).lower()=='b':
            return
        print(dbreturn[user_input])
        # send the user input to movie watching information
        watch_movie_service(cid,sessionID,dbreturn[user_input][0])
    return
    
def watch_movie_service(cid,sessionID,mid):
    global cursor,connection,userdict
    # print the movie information to the screen
    movied,title=fetch_info('''SELECT * FROM movies WHERE mid={}'''.format(mid))
    txt1='Title:    {}\nmid:      {}\nPublish at {}\nLength:   {}\n'.format(movied[0][1],movied[0][0],movied[0][2],movied[0][3])
    # use it again when select cast
    extxt=txt1
    txt1=txt1+'-'*30+'\n'
    # print out all the cast
    
    dbreturn,tille=fetch_info('''SELECT moviePeople.name,casts.role,moviePeople.birthYear 
                                FROM casts inner join moviePeople 
                                on moviePeople.pid=casts.pid WHERE mid={}'''.format(mid))
    txt1=txt1+"{:<25} {:<25} {:<8}".format(title[0],title[1],tille[2])+'\n'
    # each movie have at least one cast,so it just start fetching infomation
    for i in range(len(dbreturn)):
            txt2="{:<25} {:<25} {:<8}\n".format(dbreturn[i][0],dbreturn[i][1],dbreturn[i][2])
            txt1=txt1+txt2
    txt1=txt1+'-'*30+'\n'
    # print number of customer watched this movie
    dbreturn,title=fetch_info('''SELECT count(DISTINCT cid) 
                                FROM watch,movies WHERE movies.mid=watch.mid 
                                AND watch.mid={} AND (movies.runtime/2)<=watch.duration'''.format(mid))
    txt1=txt1+'{} Customer watched this movie\n'.format(dbreturn[0][0])+'-'*30+'\n'
    # setup select option
    info=[['follow a cast'],['start watching']]
    header=[len(info),0,[],False,txt1,'']
    inputsel=''
    # in loop selection
    while str(inputsel).lower()!='b':
        inputsel=select_menu(info,header)
        if inputsel==0:
            follow_moviepeople_service(extxt,cid,mid)
        elif sessionID=='' and inputsel==1: # want to start watch but no session ID
            input('sorry we did not find your session\n press enter to continue.')
        elif inputsel==1:
            start_watch(cid,sessionID,mid)
    return

def follow_moviepeople_service(extxt,cid,mid):
    global connection, cursor
    # print out the
    extxt='Select the movie People you want to follow:\n'+extxt
    dbreturn,title=fetch_info('''SELECT moviePeople.pid,moviePeople.name,casts.role,moviePeople.birthYear 
                      FROM casts inner join moviePeople 
                      on moviePeople.pid=casts.pid WHERE mid={}'''.format(mid))
    header=[len(dbreturn),5,title,True,extxt,'']
    userinput=''
    while str(userinput).lower()!='b':
        user_input=select_menu(dbreturn,header)
        if str(user_input).lower()=='b':
            return
        else:
            cursor.execute('''SELECT * FROM follows WHERE cid='{}' and pid='{}' '''.format(cid,dbreturn[user_input][0]))
            res=cursor.fetchone()
            if res!=None:
                input("Sorry, you alreadr follow{}.\npress enter to exit.".format(dbreturn[user_input][1]))
            else:
                txt = "insert into follows values ('{}', '{}');".format(cid,dbreturn[user_input][0])
                cursor.execute(txt)
                connection.commit()
                input("you are now  following {}.\npress enter to exit.".format(dbreturn[user_input][1]))

def start_watch(cid,sessionID,mid):
    global connection, cursor,userdict
    cursor.execute('''SELECT * FROM watch where cid='{}' and mid={} and sid={}'''.format(cid,mid,sessionID))
    dbreturn=cursor.fetchone()
    # it means the movie already started or finshed watching in this session
    if dbreturn is not None:
        input('you are already watching or finshed this movie in this session\n press enter to gp back')
        return
    # else start register
    cursor.execute(txt = "insert into watch values ({}, '{}',{},{});".format(sessionID,cid,mid,'NULL'))
    userdict[mid]=time.time()
    connection.commit()
    input('your movie start watching now!')
    return

def end_watch(cid,sessionID):
    global connection, cursor,userdict
    # searcg for related sid,but no duration record
    if sessionID=='':
        input('session ID not found\n press enter to continue')
        return
    cursor.execute('''SELECT watch.mid,movies.title,movies.year 
                      FROM watch,movies
                      WHERE  movies.mid=watch.mid
                      and cid='{}' and sid={} and watch.mid is NULL'''.format(cid,sessionID))
    # start getching list of unwatch movie
    dbreturn=[cursor.fetchone()]
    if dbreturn[0] is None:
        input('no watch found\n press enter to continue')
        return
    # fetch multi line info
    while dbreturn[-1] is not None:
        dbreturn.append(cursor.fetchone())
    dbreturn.pop()
    o2=cursor.information
    # get tittle (orginally dim(3) array)
    title=[]
    for i in range(len(o2)):
        title.append(o2[i][0])
    header=[len(dbreturn),5,title,False,'select the, movie that you want to watch','']
    re=select_menu(dbreturn,header)
    # if respo
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

def fetch_info(run_txt):
    # dissription:
    # gets the querry of text,get information from database,an returb the tille and infomation
    # ----------------------------------------------------------------
    # arguments:
    # argv1 = 'select * from movie(example)
    # ----------------------------------------------------------------
    # return arguments
    # argv1: mathch information from database
    # argv2: table tittle
    # ----------------------------------------------------------------
    global cursor,connection
    # text not empty
    if run_txt==None or run_txt=='':
        return None,None
    cursor.execute(run_txt)
    # get all related movie
    data_base_return = cursor.fetchall()
    title_return=cursor.description
    # tittle fetching
    adj_tittle=[]
    for i in range(len(title_return)):
        adj_tittle.append(title_return[i][0])
    #data_base_return.pop()
    return data_base_return,adj_tittle


def list_input_menu(print_format,user_input):
    # dissription:
    # This function intented to allow user input their information, User are able to input the blank they want.
    # However this function only do gerenal check,They input will return and the orginal function will fetch information and connect
    # ----------------------------------------------------------------
    # arguments:
    # argv1=[num input,[name of input],[entry that need to be hideen],msg1(before list),msg2(after text)]
    # argv2=[previously input] this allow system compare the infomation and still able to change from the last answer
    # ----------------------------------------------------------------
    # example of entry
    # argv1(print_format)=[2,['user name: ', 'password:'],['password'],'log in','']
    # argv2(user input)=['c100','password']
    # user login:
    # --------------------
    #1: user name    c100
    #2: password    ******

    #B: go back
    #S: submit
    # ----------------------------------------------------------------
    # return arguments
    # argv1: same as input argv in input
    # argv2: selection, it lets the caller know if user promote back

    # when user promote select (B)back or (S)select it means user finish their input and ready to exit
    selection =''
    # while use did not quite or submit
    while selection.lower() not in ['b','s']:
        # header printing
        os.system('clear') #screen clear
        print(print_format[3])
        print('-'*20)
        # each line completed information printing
        # this information are from print_format 2
        for i in range(print_format[0]):
            if (print_format[1][i] not in print_format[2]) or user_input[i]=='':
                print('{}: {:<15}    {}'.format(i+1,print_format[1][i],user_input[i]))  #regular information showing
            else:
                print('{}: {:<15}    {}'.format(i+1,print_format[1][i],'*****'))   # hidden password
        # after inforation printing
        print(print_format[-1])
        # instruction printing
        print('B: go back\nS: submit\n')
        # user promote their input and input check
        selection=input('your selection> ')
        # user who select numbers to input will be transfer here
        if selection>='0' and selection<='9':
            # number validation
            # this case will appear when user select something that outof range
            # to avoid index errors
            if int(selection)>print_format[0] or (int(selection)<=0):
                print('invalid selection, enter to continue')
                input()
            # if password hidden
            else:
                selection=str(int(selection)-1)
                if print_format[1][int(selection)] not in print_format[2]:  # if no hidden needed go here
                    temp_input=input('{}: '.format(print_format[1][int(selection)]))
                else:   # if hidden needed go here
                    temp_input=getpass.getpass('{}: '.format(print_format[1][int(selection)]))
                # data validation need here
                # only 0-9.'a'-'z','A'-'Z' allowed
                allow_input=list(range(ord('0'),ord('9'),1))+list(range(ord('A'),ord('Z'),1))+list(range(ord('a'),ord('z'),1))
                flag_input=False
                for i in range(len(temp_input)):
                    if ord(temp_input[i]) not in allow_input:
                        input('Please input 0-9,A-Z,a-z\n enter to continue')
                        flag_input=True
                        break
                if not flag_input:
                    user_input[int(selection)]=temp_input
        # if user promote things that system unexpected,tell user to reenter
        elif selection.lower() not in ['b','s']:
            print('invalid selection, enter to continue')
            input()
    # return data
    return user_input,selection.lower()                    

def select_menu(info,header):
    # dissription:
    # This function intented to given 1 to many 2D graph to select
    # it allow user select different function page from
    # It also allow user to given multi page of information in this list as well
    # ----------------------------------------------------------------
    # arguments:
    # argv1=3D array of display information ex.  [[cid,pid],.......m[cid,pid]]
    # argv2=[len(info),3,['name','age','pp'],False,txt1,txt2]
    #   argv explanation::
    #   argv2[0]:number of total inforation
    #   argv2[1]:number of inforamation per page,0 to len(info)
    #           0->show all
    #           <int> more than argv[0] will be fix to len(info)
    #   argv2[3]: T/F show the name of each column
    #   argv2[4]: title or pre infomation printing
    #   argv2[5]: after information printing
    # ----------------------------------------------------------------
    # type1 printout   customer main panel
    # Login in as customer c100
    # --------------------
    #1   Start a session
    #2   Search for movie
    #3   end watching a movie
    #4   end the session
    #no session ID assiged this moment

    #<int> number of option
    #B back

    #indicate your choice>
    # ----------------------------------------------------------------
    # type2 printout   select movie from Morgan Freeman
    # selected your movie
    # --------------------
    #   mid                       title                     year                      runtime  < control by argv2[4]
    #1   200                       Transcendence             2014                      119
    #2   190                       Now You See Me            2013                      116
    #3   180                       The Dark Knight           2008                      152
    #4   170                       Lucy                      2014                      89
    #5   40                        Million Dollar Baby       2004                      132
    #showing 0 - 5 of 7   <----- only show more than one page
    
    #L last page        <----- only show more than one page
    #N next page        <----- only show more than one page

    #<int> number of option
    #B back

    #indicate your choice>
    # ----------------------------------------------------------------
    # return arguments
    # argv1: 'b' or <int>

    # This are used to main the loop,and allow user to back level in the function
    selected=False
    # number of current page
    page=0
    #  present index overflow change to show all
    if header[1]>header[0] or header[1]==0:
        header[1]=header[0]
    # calc finding the max page avvoiding onver page
    max_page=int(header[0]/header[1])
    if (header[0]%header[1])==0:
        max_page-=1
    # user selection input 
    selection=''
    # when not selected keeop brwing
    while not selected:
        #header printing
        os.system('clear')
        # print the text of pretext
        print(header[4])
        print('-'*20)
        # header printing requested print it out
        if header[3]:
            txt='#   '
            for i in range(len(info[0])):
                txt+='{:<25} '.format(header[2][i])
            print(txt)
        # calclate the printing index in the current page
        start=page*header[1]
        end= (page+1)*header[1]
        # sometime last page not full
        if (end>header[0]):
            end = header[0]
        # printing information from argv1 aka variable info
        for y in range(start,end,1):
            # transfer that number y to order in 1 to current page
            txt='{:<4} '.format(y-page*header[1]+1)
            # adding each coulmn
            for x in range(len(info[0])):
                if len(str(info[y][x]))<=25:
                    txt+='{:<25} '.format(info[y][x])
                else:  # avoid overflow
                    txt+='{:<23}.. '.format(info[y][x][:23])
            print(txt)
        # printing number of option key allow
        if header[-1]!=None:
            print(header[-1])
        # when page more than one, print flip page instruction
        if max_page!=0:
            print('\nshowing {} - {} of {}'.format(start,end,header[0]))
            print('''\nL last page\nN next page''')
        # everycondition need to pront condition
        print('''\n<int> number of option\nB back\n''')
        # get the user input and allow go to lower case(if appicable)
        selection=input('indicate your choice> ').lower()
        #analysis user input
        if selection == 'b':  # exit
            return selection
        elif selection == 'n' and page<max_page: # next pg
            page+=1
        elif selection =='l' and page>=1: # last pg
            page-=1
        else: # number validation
            try:
                if int(selection)-1<0:
                    input("invalid input\nenter to continue")
                    continue
                elif int(selection)-1>=header[1]:
                    input("invalid input\nenter to continue")
                    continue
            except: # all other wired staff go here
                input("invalid input\nenter to continue")
                continue
            selected=True
    # tranform back to user index
    # selection == 'b' return b,another will all return interger index
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




