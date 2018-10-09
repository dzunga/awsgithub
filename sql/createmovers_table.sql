CREATE TABLE movers(
    Symbol varchar(3),
    Date DATE,
    mover varchar(10)mydev
);
ALTER TABLE `movers`
	ADD UNIQUE INDEX `Symbol_Date` (`Symbol`, `Date`);