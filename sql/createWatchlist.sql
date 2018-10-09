CREATE TABLE watchlist(
    Symbol varchar(3),
    Date DATE,
    Open float,
    High float,
    Low float,
	Close float,
    Volume int,
	9DVMA float,
	21DVMA float,
	50DVMA float,
	100DVMA float,
	200DVMA float,
	250DVMA float,
	R9DVMA float,
	R21DVMA float,
	R50DVMA float,
	R100DVMA float,
	R200DVMA float,mydev
	R250DVMA float
	);mydevinformation_schemamydev
	
	ALTER TABLE `watchlist`
	ADD UNIQUE INDEX `Symbol_Date` (`Symbol`, `Date`);