CREATE TABLE movers2(
    Symbol varchar(3),
    Date DATE,
    Close float,
    Prev_close float,
    gain float,
 	 percent_gain float,
    Volume int
	);
	
	ALTER TABLE `movers2`
	ADD UNIQUE INDEX `Symbol_Date` (`Symbol`, `Date`);