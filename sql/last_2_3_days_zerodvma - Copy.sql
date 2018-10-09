

/*** this only works for mondays  ***/
SET @today = '2018-04-19';
SET @yesterday = '2018-04-18';
SET @db4 = '2018-04-17';

  
	select * from stockvma where Symbol IN(
		select Symbol from stockvma where Symbol IN(
			select Symbol from stockvma where 
			Date=@db4 
			AND Volume >80000
			AND R9DVMA=0
			AND R21DVMA=0
			AND R50DVMA=0
			AND R100DVMA=0
			AND R200DVMA=0
			AND R250DVMA=0)
			
		AND Date =@yesterday
		AND Volume >75000
		AND R9DVMA=0
		AND R21DVMA=0
		AND R50DVMA=0
		AND R100DVMA=0
		AND R200DVMA=0
		AND R250DVMA=0)
	AND Date=@today
	AND Volume >250000
	AND R9DVMA>0
	AND R21DVMA>0
	AND R50DVMA>0
	AND R100DVMA>0
	AND R200DVMA>0
	AND R250DVMA>0
	AND Close < 1
	
	UNION
	
	select * from stockvma where Symbol IN(
		select Symbol from stockvma where 
		Date =@yesterday
		AND Volume >75000
		AND R9DVMA=0
		AND R21DVMA=0
		AND R50DVMA=0
		AND R100DVMA=0
		AND R200DVMA=0
		AND R250DVMA=0)
	AND Date=@today
	AND Volume >250000
	AND R9DVMA>0
	AND R21DVMA>0
	AND R50DVMA>0
	AND R100DVMA>0
	AND R200DVMA>0
	AND R250DVMA>0
	AND Close < 1
