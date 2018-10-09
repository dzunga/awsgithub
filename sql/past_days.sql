SELECT CAST(CURRENT_DATE() AS CHAR(50)) INTO @today;
SELECT CAST(DATE_ADD(CURRENT_DATE, INTERVAL -1 DAY) AS DATE) INTO @yesterday;
SELECT CAST(DATE_ADD(CURRENT_DATE, INTERVAL -2 DAY) AS DATE) INTO @db4;
SELECT @today, @yesterday,@db4;


SELECT CAST((CASE WEEKDAY(CURRENT_DATE) 
                             WHEN 0 THEN SUBDATE(CURRENT_DATE,3)
                             WHEN 6 THEN SUBDATE(CURRENT_DATE,2) 
                             WHEN 5 THEN SUBDATE(CURRENT_DATE,1)
                             ELSE SUBDATE(CURRENT_DATE,1) 
                        END)   AS DATE) INTO @buss_yesterday2;

                                      
SELECT CAST((CASE WEEKDAY(CURRENT_DATE) 
                             WHEN 0 THEN SUBDATE(CURRENT_DATE,4)
                             WHEN 1 THEN SUBDATE(CURRENT_DATE,4)
                             WHEN 6 THEN SUBDATE(CURRENT_DATE,3) 
                             WHEN 5 THEN SUBDATE(CURRENT_DATE,2)
                             ELSE SUBDATE(CURRENT_DATE,2) 
                        END)   AS DATE) INTO @buss_db4_2;
                                      SELECT @buss_yesterday2,@buss_db4_2;
                                      
/*** TEST  each day 
0=Mon
1=Tues=ok
2=wed ok 
3=thurs ok
...
6=Sun

Sat
Sun
Mon

Tuesday = ok
***/