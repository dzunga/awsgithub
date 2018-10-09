CREATE TABLE stock(
    Symbol varchar(3),
    Date DATE,
    Open float,
    High float,
    Low float,
	Close float,
    volume int
);

ALTER TABLE `stock`
	ADD UNIQUE INDEX `Symbol_Date` (`Symbol`, `Date`);