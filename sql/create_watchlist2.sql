CREATE TABLE watchlist3(
    Symbol varchar(3),
    Date DATE,
    Close float,
    Prev_close float,
    gain float,
 	 percent_gain float,
    Volume int
	);
	
	ALTER TABLE `watchlist3`
	ADD UNIQUE INDEX `Symbol_Date` (`Symbol`, `Date`);