import pymysql
import pandas as pd
from sqlalchemy import create_engine
import numpy as np

import sys
import datetime as dt
from datetime import datetime
from datetime import timedelta

import time
import os
from os import path


from bs4 import BeautifulSoup
from urllib import request
from urllib.request import Request, urlopen
import requests
import re



#filename
myASXfile= 'asxlist.csv'
#myASXfile_input=myASXfile
#myASXfile_input = 'asxlist_temp2.csv'



stock_num=0
filename_lock='lock.txt'

#define tables to query

tablevma='stockvma'
tablestock='stock'
table_mover='movershc'

def print_my_menu(currentEOD):
    print('\n\n-----ASX DATA extract OPTIONS-----')
    print('\t\t1. backup current tables: 5 tables: stock,movershc,stockvma,watchlist,dog')
    print('\t\t2. get_current_EOD does date formatting')
    print('\t\t3. insert EOD data into stock table')
    print('\t\t4. calculate_vma')
    print('\t\t5. gainers and losers today')
    print('\t\t6. export 2d_3d_watchlist to csv')
    print('\t\t7. movershc list from HotCopper + update DB')
    print('\t\t8. Empty 3 things: stockvma, XJO rows, symbol>3 length')
    print('\t\t9. single stockcode')
    print('\t\t11. kaBOOM! do 2-6+12(hc download) ')
    print('\t\t10. to exit')
    print('\t\t. Current EOD: ' +currentEOD)
    print('----------------------------------')


def empty_vma_table(mySymbol):
    print("clearing: " + str(mySymbol))
    engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
    amySymbol="', '".join(mySymbol)
    amySymbol="'"+amySymbol+"'"
    print ("string amySymbol: " +amySymbol )
    sql_string="delete from stockvma where Symbol in("+amySymbol+")"
    print ("executing sql:" + sql_string)
    with engine.connect() as con:
        rs = con.execute(sql_string)
        print ("stockvma table cleared")


def empty_XJO_3XXX_rows():

    engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')

    sql_string1 = "delete from stock where length(Symbol) > 3; truncate stockvma"
    print("executing sql:" + sql_string1)
    with engine.connect() as con:
        rs = con.execute(sql_string1)
        print("delete Symbol length >3  from stock  table cleared  && truncate stockvma ")

    sql_string2 = "delete from stock where Symbol in ('XAF','XAO','XAT','XDI','XDJ','XEC','XEJ','XFJ','XFL','XGD','XHJ','XIJ','XJO','XJR','XKO','XLD','XMD','XMJ','XNJ','XNT','XNV','XPJ','XSJ','XSO','XTJ','XTL','XTO','XUJ','XXJ')"
    print("executing sql:" + sql_string2)
    with engine.connect() as con:
        rs = con.execute(sql_string2)
        print("removed all X[A-Z][A-Z] set of rows from stock  table cleared")


def del_lockfile(filename_lock):
   if os.path.isfile('csv/'+filename_lock):
        os.remove('csv/'+filename_lock)
        print ('deleted '+filename_lock)
   else:
       print('no lock file to delete')

def backup_current_csv(menu_stage_append):
       print('backup current_csv')
       dt = datetime.now()
       strg = dt.strftime('%Y%m%d-%H-%M')
       print('cp -r csv ' + 'csv' + menu_stage_append + strg)
       os.system('cp -r csv ' + 'csv_' + menu_stage_append + strg)
       print('files backedup:')
       os.system('ls -l ' + 'csv_' + menu_stage_append + strg + ' | wc -l')
       os.system('rm csv/*.csv')
       os.system('rm csv/*.txt')


#read stocklist
def read_stocklist(my_file):
    global stock_num
    lines=[]
    f=open(my_file,'r')
    for line in f:
        line = line.strip()  # remove carraige returns
        lines.append(line)
    my_uniq=set(lines)
    lines=sorted(my_uniq)
    print ('reading complet ASX stock file list'+myASXfile)
    print('--print sorted file that is read ---')
    print(lines)
    stock_num=len(lines)
    print('ASX STOCKS: '+ str(stock_num))
    f.close()
    return lines

def download_EOD(inputEOD):

    myDate=inputEOD
    #download file
    CSV_URL = 'http://www.cooltrader.com.au/members/0730/data/csv/eod/' + inputEOD+ '.csv'

    print('Downloading: '+CSV_URL)
#format to download 'http://www.cooltrader.com.au/members/0730/data/csv/eod/20180207.csv'

    df = pd.read_csv(CSV_URL, names=['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'],skipinitialspace=True)

    # df['Date']=df['Date'].dt.strftime('%Y-%m-%d')  #date format default is  to format  format DD-MM-YY
    #df['Date']=pd.to_datetime(df['Date'],format='%YYY%Mm%dd')

    myfilename=inputEOD+".csv"
    print('--- columns raw ---')
    #df['Date']=pd.to_datetime(df['Date'],format='%Y%m%d').dt.strftime("%Y%m%d")
    print(df.head(2))
   # print("....rearrange YYYMMDD....")
    #df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')  # the  d is acutally month in the CSV as raw csv format is DDMMYYYY
    print("....")
    print(df.tail(2))

    df.to_csv(myfilename,index=False,header=False, date_format='%Y%m%d')

def format_inputEOD(inputEOD,eod_file, old_word, new_word):
    # $1=inputcsv  20180213  | inputEOD
    # $2=output file after format asxeod.csv  eod_file
    # $3=original raw format 13/02/2018  old_word
    # $4=new format 20180213   new_word
    os.system('fc.sh '+inputEOD+'.csv ' +eod_file + " " + old_word + " " + new_word)
    print("greped into new eodfile:"+eod_file)

def update_stock_eod(eod_file):
    #update stoc table  with latest eod
    engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
    dt = datetime.now()
    strg = dt.strftime('%Y%m%d_%H_%M')
    print("loading eod file:"+eod_file)

    df = pd.read_csv(eod_file, names=['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

    df.set_index('Symbol', inplace=True)  #drops the default index that pandas has and makes symbol the index
    cols = list(df.columns.values)
    print('--- loading these columns --- \n\n' + str(cols))  # this is what will load

    print("--head: --\n")
    print(df.head(5))
    print (".....")
    print("--tail: --\n")
    print(df.tail(5))

    df.to_sql(con=engine, name=tablestock, if_exists='append')

    print("updated eod table:"+tablestock)

def replace_word(eod_file,old_word,new_word):  # no longer needed as got shell script to work: fc.sh
    print("checking eod_file exist:" + eod_file)
    if os.path.isfile(eod_file):
        print("eod file exist:" + eod_file)
        #os.system('touch ' +  infile)
        f1=open(eod_file,'r').read()
        f2=open("f_"+eod_file,'w')
        m=f1.replace(old_word,new_word)
        #print(m)
        f2.write(m)
        print("finish date replace")
    else:
        print ("Error on replace_word, not a regular file: "+eod_file)

def get_stocklist_db():
    engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
    df = pd.read_sql_query("SELECT Symbol FROM " + tablestock + " group by  Symbol", engine)
    df.set_index('Symbol', inplace=True)
        # now have the result in df.head
    with open(myASXfile, 'w') as f:
        print('--- writing asxlist file: '+ myASXfile)
        # write output to file
        df.to_csv(f, header=False, date_format='%Y-%m-%d')  # just append
    # resamplin data here

def get_singlestock_db(mySymbol):
        global stock_num;
        print("--inside get_singlestock_db---:" +  mySymbol)

        engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
        df = pd.read_sql_query("SELECT * FROM " + tablestock + " where Symbol='" + mySymbol + "'", engine)
        # now have the result in df.head
        df.set_index('Date', inplace=True)
        df = df.replace(0,np.NaN)  # replace zeros  as NaN, so it ignores the  value to calculate, as Zero is counted as ZERO! have to reset at end

        df['9DVMA'] = df['Volume'].rolling(window=9, min_periods=0).mean()
        df['21DVMA'] = df['Volume'].rolling(window=21, min_periods=0).mean()
        df['50DVMA'] = df['Volume'].rolling(window=50, min_periods=0).mean()
        df['100DVMA'] = df['Volume'].rolling(window=100, min_periods=0).mean()
        df['200DVMA'] = df['Volume'].rolling(window=200, min_periods=0).mean()
        df['250DVMA'] = df['Volume'].rolling(window=250, min_periods=0).mean()

        df['R9Dvma'] = np.where(df['Volume'] > df['9DVMA'], df['Volume'] / df['9DVMA'], 0)
        df['R21Dvma'] = np.where(df['Volume'] > df['21DVMA'], df['Volume'] / df['21DVMA'], 0)
        df['R50Dvma'] = np.where(df['Volume'] > df['50DVMA'], df['Volume'] / df['50DVMA'], 0)
        df['R100Dvma'] = np.where(df['Volume'] > df['100DVMA'], df['Volume'] / df['100DVMA'], 0)
        df['R200Dvma'] = np.where(df['Volume'] > df['200DVMA'], df['Volume'] / df['200DVMA'], 0)
        df['R250Dvma'] = np.where(df['Volume'] > df['250DVMA'], df['Volume'] / df['250DVMA'], 0)

        df['R9Dvma'] = df['R9Dvma'].round(4)
        df['R21Dvma'] = df['R21Dvma'].round(4)
        df['R50Dvma'] = df['R50Dvma'].round(4)
        df['R100Dvma'] = df['R100Dvma'].round(4)
        df['R200Dvma'] = df['R200Dvma'].round(4)
        df['R250Dvma'] = df['R250Dvma'].round(4)

        df = df.replace(np.NaN, 0)

        # reader put the RXXXDVMA  columns after the Volumne column.

        df = df[['Symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'R9Dvma', 'R21Dvma', 'R50Dvma', 'R100Dvma',
                 'R200Dvma', 'R250Dvma', '9DVMA', '21DVMA', '50DVMA', '100DVMA', '200DVMA', '250DVMA']]
        cols = list(df.columns.values)
        print('--- reordered  columns --- \n\n' + str(cols))

        # not writing to csv as no longer need as updting to db with .to_sql comand command out
        # with open('csv/' + mySymbol + 'vma.csv', 'w') as f:
        # print('--- writing vma file:' + mySymbol + 'vma.csv')
        # write output to file
        # df.to_csv(f, header=True, date_format='%Y-%m-%d')  # just append
        # resamplin data here

        print('---last 5 VMA---')
        print(df.tail(5))
        df.to_sql(con=engine, name=tablevma, if_exists='append')  # appends to table df results
        print('update table:'+tablevma)

def get_allstock(mystocklist):
    global stock_num;
    print( "--inside get_allstock---")
    print (mystocklist)

    if os.path.isfile('csv/' + filename_lock):
        # file exist
        with open('csv/' + filename_lock, 'r') as f:
            last_code = f.readline()
            last_code = last_code.strip()
            print('last stock:' + last_code)
            last_position = mystocklist.index(last_code)
            print('last position:' + str(last_position))
            #stocklist_empty=mystocklist[last_position:]
            #print("this is list to db clear:")
            #empty_vma_table(mystocklist[last_position:])  #doesnt work
    else:
        last_position = 0
        print ("last position  zero")

    try:
        for mySymbol in mystocklist[last_position:]:
           pc= (mystocklist.index(mySymbol)/stock_num)*100  # gives percent
           print ("print mySymbol:" + str(mySymbol) + " , " + str(mystocklist.index(mySymbol))+ "  of " + str(round(stock_num,1))+" , " + str(round(pc,2)) + "%") #prints symbol to read and position in list to read
           with open('csv/' + filename_lock, 'w') as f:
                print('--- creating lock file,  insert symbol: '+ mySymbol)
                f.write(mySymbol)

           engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
           df = pd.read_sql_query("SELECT * FROM " + tablestock + " where Symbol='" + mySymbol + "'", engine)
           # now have the result in df.head
           df.set_index('Date', inplace=True)
           df = df.replace(0,
                            np.NaN)  # replace zeros  as NaN, so it ignores the  value to calculate, as Zero is counted as ZERO! have to reset at end

           df['9DVMA'] = df['Volume'].rolling(window=9, min_periods=0).mean()
           df['21DVMA'] = df['Volume'].rolling(window=21, min_periods=0).mean()
           df['50DVMA'] = df['Volume'].rolling(window=50, min_periods=0).mean()
           df['100DVMA'] = df['Volume'].rolling(window=100, min_periods=0).mean()
           df['200DVMA'] = df['Volume'].rolling(window=200, min_periods=0).mean()
           df['250DVMA'] = df['Volume'].rolling(window=250, min_periods=0).mean()

           df['R9Dvma'] = np.where(df['Volume'] > df['9DVMA'], df['Volume'] / df['9DVMA'], 0)
           df['R21Dvma'] = np.where(df['Volume'] > df['21DVMA'], df['Volume'] / df['21DVMA'], 0)
           df['R50Dvma'] = np.where(df['Volume'] > df['50DVMA'], df['Volume'] / df['50DVMA'], 0)
           df['R100Dvma'] = np.where(df['Volume'] > df['100DVMA'], df['Volume'] / df['100DVMA'], 0)
           df['R200Dvma'] = np.where(df['Volume'] > df['200DVMA'], df['Volume'] / df['200DVMA'], 0)
           df['R250Dvma'] = np.where(df['Volume'] > df['250DVMA'], df['Volume'] / df['250DVMA'], 0)

           df['R9Dvma']=df['R9Dvma'].round(4)
           df['R21Dvma'] = df['R21Dvma'].round(4)
           df['R50Dvma'] = df['R50Dvma'].round(4)
           df['R100Dvma'] = df['R100Dvma'].round(4)
           df['R200Dvma'] = df['R200Dvma'].round(4)
           df['R250Dvma'] = df['R250Dvma'].round(4)



           df = df.replace(np.NaN, 0)

            # reader put the RXXXDVMA  columns after the Volumne column.

           df = df[['Symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'R9Dvma', 'R21Dvma', 'R50Dvma', 'R100Dvma', 'R200Dvma','R250Dvma', '9DVMA', '21DVMA', '50DVMA', '100DVMA', '200DVMA', '250DVMA']]
           cols = list(df.columns.values)
           print('--- reordered  columns --- \n\n' + str(cols))
           print('---last 5 VMA---')
           print(df.tail(5))
           df.to_sql(con=engine, name=tablevma, if_exists='append')  # appends to table df results
           print('updated table: '+tablevma)

    except Exception as e:  # (as opposed to except Exception, e:) # catch all

        # ^ that will just look for two classes, Exception and e
        print(e)  # for the repr
        print(str(e))  # for just the message
        print(e.args)  # the arguments that the exception has been called with.
        # the first one is usually the message.
        print('--lock file exist ---:  ' + filename_lock)

def backup_table(inputEOD,frmtable,order_by):
    #backup the 2 tables with suffix tablenameYYYMMDD_HHMIN: stock, stockvma
    engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
    dt = datetime.now()
    strg = dt.strftime('%Y%m%d_%H_%M')
    tablename=frmtable+'_'+strg

    sql_string1 = "create table "+ tablename+ " like " + frmtable
    print("\nexecuting sql:" + sql_string1)
    with engine.connect() as con:
        rs = con.execute(sql_string1)
        print("creating table: "+tablename)

    sql_string2 = "insert " + tablename + " select *  from  " + frmtable + " " + order_by
    print("executing sql:" + sql_string2)
    with engine.connect() as con:
        rs = con.execute(sql_string2)
        print("backup data into  table complete: " + tablename)

def gainers_losers(inputEOD,mystocklist,tablestock):
    global db4
    print('procesing gainers_losers for EOD: '+ inputEOD)
    engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
    count=0
    cols = ['Symbol','Date','Close','Prev_Close','gain','percent_gain','Volume']
    gl_df = pd.DataFrame(columns = cols)
    gl_df.set_index('Symbol', inplace=True)
    print('--new data frame for gainers _losers -- ')
    print(gl_df)

    print ("stocklist: " + str(mystocklist))
    #use mystocklist[0:2]  to cucle through rows
    for mySymbol in mystocklist:
        print('getting symbol:'+ mySymbol)
      # use this line for fixed length, incause you delete accidently a single day
      #  df = pd.read_sql_query("SELECT * FROM " + tablestock + " where Symbol='" + mySymbol + "' AND Date between '2018-04-05' AND '2018-04-07' "+ "order by Date desc limit 2", engine)  u
        df = pd.read_sql_query("SELECT * FROM " + tablestock + " where Symbol='" + mySymbol + "'"+ " and Date > '" +db4 +"'"  + " order by Date desc limit 2", engine)
        print('--- sql data frame for last 2 rows---')
        total_rows=len(df.index)
        print(df)
        print("total_rows: "+str(total_rows))
        if (total_rows <2): # break if there is no previous data
            with open('ignore'+inputEOD+'.csv', 'a') as f:
                print('Symbol:' + mySymbol + ' cannot be processed')
                # write output to file
                df.to_csv(f, header=False, date_format='%Y-%m-%d')  # just append
        else:

         try:
            store_symbol = df['Symbol'].values[0]
            today_date=df['Date'].values[0]
            nan_today_close = df['Close'].isnull()
            print("nan_today_close: " + str(nan_today_close))
            null_columns = df.columns[df.isnull().any()]        #check for null in column
            print("null_columns: " + str(null_columns))
            print(df[df["Close"].isnull()][null_columns])        # check for null in row
            today_close=df['Close'].values[0]

            prev_close=df['Close'].values[1]
            gain=today_close-prev_close
            per_gain=(gain/prev_close)*100

            today_volume = df['Volume'].values[0]
            # appending values into gainer_losers_df,  use a dict here  Fieldname:variable
            gl_df = gl_df.append(
                {'Symbol': store_symbol, 'Date': today_date, 'Close': today_close, 'Prev_Close': prev_close, 'gain': gain,
                 'percent_gain': per_gain, 'Volume': today_volume}, ignore_index=True)

            print('Processing Symbol: ' + mySymbol)
            print('Date:'+ str(today_date))
            print('today close: '+str(today_close))
            print('prev close: '+str(prev_close))
            print('gain: ' + str(gain) + " , " +str(per_gain) +"%" )
            print( 'today volume:' +str(today_volume))
            print(df.head(2))

         except Exception as e:  # (as opposed to except Exception, e:) # catch all
             # ^ that will just look for two classes, Exception and e
             print(e)  # for the repr
             print(str(e))  # for just the message
             print(e.args)  # the arguments that the exception has been called with.
             # the first one is usually the message.
             print('--invalid error ---:  ' + mySymbol)

    print('content of  WHOLE gainers_losers dataframe\n')
    print(gl_df)
        #populate into watchlist2
        # gain, %gain, prevclose,today
    tablename='movers_gainers'
    gl_df.set_index('Symbol', inplace=True)
    with open('movers_gainers'+inputEOD+'.csv', 'w') as f:
        print('--- writing movers_gainers file: ' + 'movers_gainers'+inputEOD)
        # write output to file
        gl_df.to_csv(f, header=False, date_format='%Y-%m-%d')  # just append
        # resamplin data here

    gl_df.to_sql(con=engine, name=tablename, if_exists='append')  # appends to table df results
    print ("updated movers_gainers table")


def get_watchlist(my_day):
    #enhancement need to replace SQL with a  file
        print(" Preparing watchlist for: " + str(inputEOD))
        engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
        dt = datetime.now()
        strg = dt.strftime('%Y%m%d_%H_%M')
        print("day before: {dayb4}")

        stmt = """\
                  INSERT watchlist select * from stockvma where Symbol IN( \
                      select Symbol from stockvma where Symbol IN( \
                        select Symbol from stockvma where Date={dayb4}\
                            AND Volume >80000 \
                            AND R9DVMA=0 \
                            AND R21DVMA=0 \
                            AND R50DVMA=0 \
                            AND R100DVMA=0 \
                            AND R200DVMA=0 \
                            AND R250DVMA=0) \
                        AND Date ={yesterday} \
                        AND Volume >75000 \
                        AND R9DVMA=0 \
                        AND R21DVMA=0 \
                        AND R50DVMA=0 \
                        AND R100DVMA=0 \
                        AND R200DVMA=0 \
                        AND R250DVMA=0)\
                    AND Date={today} \
                    AND Volume >250000 \
                    AND R9DVMA>0 \
                    AND R21DVMA>0 \
                    AND R50DVMA>0 \
                    AND R100DVMA>0 \
                    AND R200DVMA>0 \
                    AND R250DVMA>0 \
                    AND Close < 1

                    UNION \
                    select * from stockvma where Symbol IN( \
    		            select Symbol from stockvma where  \
    		            Date ={yesterday} \
    		            AND Volume >7000 \
    		            AND R9DVMA=0 \
    		            AND R21DVMA=0 \
    		            AND R50DVMA=0 \
    		            AND R100DVMA=0 \
    		            AND R200DVMA=0 \
    		            AND R250DVMA=0) \
    		        
    		        AND Date={today} \
    		        AND Volume >250000 \
    		        AND R9DVMA>0 \
    		        AND R21DVMA>0 \
    		        AND R50DVMA>0 \
    		        AND R100DVMA>0 \
    		        AND R200DVMA>0 \
    		        AND R250DVMA>0 \
    		        AND Close < 1 \
    		        order by Close asc"""
        f_stmt = stmt.format(**my_day)
        print(f_stmt)
        with engine.connect() as con:
            rs = con.execute(f_stmt)
            print("sql statment executed")


def download_direct_hc(my_file,inputEOD,url):
    print('using import requests: ' + url)
    # user-agent part is important
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    # print(r.text)
    my_webpage = r.text

    with open('direct' + my_file, 'w', encoding='utf-8') as f:
        f.write(my_webpage)
    f.close()

    return my_webpage

def get_hc_content(my_file,inputEOD,my_webpage):
#make beautiful soup read the file, its more efficient as read only once.
    my_soup=BeautifulSoup(my_webpage,'html.parser')
    heading_name='ticker-item'
    my_tag='span'
    my_gainers_losers=''
    #need to pump this into gainers_losers list and display all gainers first and then all negative
    gain=[]
    lose=[]

    cnt=0
    gainer=0
    loser=0
    with open(my_file, 'w', encoding='utf-8') as f:
        for my_story_heading in my_soup.find_all(my_tag,{'class',heading_name}) : #my_tag being the tag passed into this function,  i.e. heading type
            cnt=cnt+1
            #print(str(cnt)+ str(my_story_heading))
            #print(my_story_heading)
            line=str(my_story_heading)
            my_symbol=line.lstrip('"symbol">')
            print('my_symbol: ' +my_symbol)
            line1=line.rstrip("</span></span></a></span>")

            print ('line1: ' + line1)
            line2=line1[-4:-1].strip(">")
            print ('line2 after4 strip:' + line2)
            line2 = line2.strip("\">")

            print('line2: ' + line2)

            if int(line2)>0:
                print(line[66:69]+","+inputEOD+","+"GAINER"+","+line2)
                f.write(line[66:69]+","+inputEOD+","+"GAINER"+","+line2+"\n")
                gain.append(line)
                gainer=gainer+1
            else:
                print(line[66:69]+","+inputEOD+","+"LOSER"+","+line2)
                f.write(line[66:69] + "," + inputEOD + "," + "LOSER" + "," + line2+"\n")
                lose.append(line)
                loser=loser+1
        print("number of gainers:" +  str(gainer))
        print("number of losers:" + str(loser))
    f.close()

def  update_movershc_table_from_csv(my_file):
    engine = create_engine('mysql+pymysql://root:password@localhost:3306/mydev')
    dt = datetime.now()
    strg = dt.strftime('%Y%m%d_%H_%M')
    print("loading eod file:"+my_file+ " into movershc table")

    df = pd.read_csv(my_file, names=['Symbol', 'Date', 'mover', 'percent'], skipinitialspace=True)
    df.set_index('Symbol', inplace=True)  # drops the default index that pandas has and makes symbol the index
    cols = list(df.columns.values)
    print('--- loading these columns --- \n\n' + str(cols))  # this is what will load

    print("--head: --\n")
    print(df.head(15))
    print(".....")
    print("--tail: --\n")
    print(df.tail(15))
    print("attempting to update table: "+table_mover)
    df.to_sql(con=engine, name=table_mover, if_exists='append')

    print("updated eod table: "+table_mover)

##sed 1d ASXEQUITIESCSV-20180919.csv > ASXEQUITIESCSV-20180919.csv
##sed -i 's/19 Sep 2018/2018-09-19/g' ASXEQUITIESCSV-20180919.csv
my_day={'today':"'2018-10-09'",'yesterday':"'2018-10-08'",'dayb4':"'2018-10-05'"}

inputEOD='20181009'
yday='2018-10-08'
db4='2018-10-05'
eod_file = 'ASXEQUITIESCSV-'+inputEOD+'.csv'

url='https://hotcopper.com.au'
my_file='hc'+inputEOD+'.csv'

new_word=inputEOD

#finding old_word
my_year=inputEOD[:4]  ## first 4
my_mm=inputEOD[4:6]  ## 5 and 6 position
my_dd=inputEOD[-2:]  ## last 2
print("ddmmyyyy:  " +my_dd+my_mm+my_year)
old_word = my_dd+'/'+my_mm+'/'+my_year

print("printing old_world concatenate by / : "+str(old_word))

print_my_menu(inputEOD)
my_selection=int(input('Select option:'))
while True:
    cont=False
    if my_selection==1 or cont:
        #creating the backup table
        dt_start=datetime.now()
        strg=dt_start.strftime('%Y%m%d-%H-%M')
        order_by_str=' order by Symbol, Date'
        backup_table(inputEOD, 'watchlist',order_by_str )
        backup_table(inputEOD, 'movershc',order_by_str)
        backup_table(inputEOD, 'dog',order_by_str)
        backup_table(inputEOD, 'stock', order_by_str)
        backup_table(inputEOD, 'movers_gainers', order_by_str)
        backup_table(inputEOD, 'stockvma', order_by_str)

        print("time start: " + strg)
        dt_end = datetime.now()
        strg2 = dt_end.strftime('%Y%m%d-%H-%M')

        print("time end:   " + strg2)

        time_difference = dt_end - dt_start
        time_difference_in_minutes = time_difference / timedelta(minutes=1)

        print("time taken in min:" + str(time_difference_in_minutes))

        completed_action='backed up table ' +'#'+str(my_selection)
    elif my_selection==2 or cont:
        download_EOD(inputEOD)
        format_inputEOD(inputEOD,eod_file, old_word, new_word)
        #replace_word(eod_file, old_word, new_word)
        completed_action='downloaded EOD '+ '#'+str(my_selection) +' ' +inputEOD
    elif my_selection==3 or cont:
        print("update eod into stock table")
        update_stock_eod(eod_file)
        print("empty rows: XJO rows and all XXX Symbols")
        empty_XJO_3XXX_rows()
        completed_action='updated EOD: '+inputEOD+'  into stock table' +'#'+str(my_selection)
    elif my_selection == 4 or cont:
        dt = datetime.now()
        strg = dt.strftime('%Y%m%d-%H-%M')
        print("4: calculate vma")
        backup_current_csv('stockvma')
        get_stocklist_db()  # 1 gets the list from the databse and write to single file myASXfile. This is COMPLETE list of ASX stocks
        mystocklist = read_stocklist(myASXfile)  # reads stocklist and puts into a list
        # 3- run to update vma
        get_allstock( mystocklist)  # this gets vma, need to separate this  function and calls empty_vma_table  for stocks in question, where last lock file placed
        print("start: "+strg)
        dt_end=datetime.now()
        strg2 = dt_end.strftime('%Y%m%d-%H-%M')
        print("end:   " +strg2)

        time_difference = dt_end - dt
        time_difference_in_minutes = time_difference / timedelta(minutes=1)

        print("time taken in min:" + str(time_difference_in_minutes))

        completed_action='Updated stockvma table #'+str(my_selection)
        print("symbol processed total: " + str(stock_num))

    elif my_selection==5 or cont:
        get_stocklist_db()  # 1 gets the list from the databse and write to single file myASXfile. This is COMPLETE list of ASX stocks
        mystocklist = read_stocklist(myASXfile)  # reads stocklist and puts into a list
        gainers_losers(inputEOD, mystocklist, 'stockvma')
        completed_action = 'get gainers and losers ' + '#' + str(my_selection)
        print("Stock number today: " + str(stock_num))
    elif my_selection == 6 or cont:
        # todo  have to validate query on  today, yesterday, db4 variables
        print('get 2d_3d_watchlist from today')
        get_watchlist(my_day)
        completed_action = 'get 2d_3d_watchlist ' + '#' + str(my_selection)
    elif my_selection == 7 or cont:
        my_webpage = download_direct_hc(my_file, inputEOD, url)
        print("\n\ncontent mypage:" + my_webpage)
        get_hc_content(my_file, inputEOD, my_webpage)
        update_movershc_table_from_csv(my_file)
        completed_action = 'update HC gainers and losers into movershc table #' + str(my_selection)
    elif my_selection==8 or cont:
        print("empty rows: XJO rows and all XXX Symbols")
        empty_XJO_3XXX_rows()
        completed_action='empty rows: XJO rows and all XXX Symbols ' +'#'+str(my_selection)
    elif my_selection==9 or cont:
        # get
        dt = datetime.now()
        strg = dt.strftime('%Y%m%d-%H-%M')
        # 3- run to update vma
        get_singlestock_db('agy')
        dt_end=datetime.now()
        strg2 = dt_end.strftime('%Y%m%d-%H-%M')
        print("end:   " + strg2)
        completed_action ='update single stock '+'#'+str(my_selection)
        print("Stock number today: " + str(stock_num))
    elif my_selection ==10:
        cont = True
        print('you choose to exit')
        break
    elif my_selection == 11:
        ##download section no longer need. Mannual download from commsec -> Quotes -> EOD -> CSV format
        # print("--- downloading EOD:" + inputEOD + "---")
        # download_EOD(inputEOD)
        # format_inputEOD(inputEOD, eod_file, old_word, new_word)
        #
        # print( 'downloaded EOD ' + inputEOD)
        print("--- update eod into stock table ---")
        print("eod_File: "+eod_file)
        time.sleep(20)
        update_stock_eod(eod_file)
        print("empty rows: XJO rows and all XXX Symbols")
        empty_XJO_3XXX_rows()
        print('updated EOD: ' + inputEOD + '  into stock table')

        print("---calculate stockvma --")
        dt = datetime.now()
        strg = dt.strftime('%Y%m%d-%H-%M')
        print("4: calculate vma")
        backup_current_csv('stockvma')
        get_stocklist_db()  # 1 gets the list from the databse and write to single file myASXfile. This is COMPLETE list of ASX stocks
        mystocklist = read_stocklist(myASXfile)  # reads stocklist and puts into a list
        # 3- run to update vma
        get_allstock(mystocklist)  # this gets vma, need to separate this  function and calls empty_vma_table  for stocks in question, where last lock file


        print("symbol processed total: " + str(stock_num))
        print( 'Updated stockvma table')

        print("--- get gainers and losers today ---")
        get_stocklist_db()  # 1 gets the list from the databse and write to single file myASXfile. This is COMPLETE list of ASX stocks
        mystocklist = read_stocklist(myASXfile)  # reads stocklist and puts into a list
        gainers_losers(inputEOD, mystocklist, 'stockvma')
        print('get gainers and losers ')
        print("Stock number today: " + str(stock_num))

        print("--- get 2d_3d_watchlist ---")
        get_watchlist(my_day)


        print("update movershc table download HC webpage from url ")
        my_webpage = download_direct_hc(my_file, inputEOD, url)
        print("\n\ncontent mypage:"+ my_webpage)
        get_hc_content(my_file, inputEOD, my_webpage)
        update_movershc_table_from_csv(my_file)
        print("end processing of all functions kaBOOM")

        print("time start: " + strg)
        dt_end = datetime.now()
        strg2 = dt_end.strftime('%Y%m%d-%H-%M')

        print("time end:   " + strg2)

        time_difference = dt_end - dt
        time_difference_in_minutes = time_difference / timedelta(minutes=1)

        print ("time taken in min:" + str(time_difference_in_minutes))


        print("symbol processed total: " + str(stock_num))

        completed_action = 'You chose all kaBOOM #'+str(my_selection)

    else:
        print('wrong selection')

    print_my_menu(inputEOD)
    print('Last action: '+completed_action)
    my_selection = int(input('Select option:'))


exit()
