use mydev;
SET @yyyy_mm=DATE_FORMAT(now(),'%Y%m%d_%H%I');
SET @newtable = concat('watchlist',@yyyy_mm);
SET @s=CONCAT('create table  ', @newtable, ' like watchlist');
select @newtable;
select @s;

PREPARE stmt1 FROM @s; 
EXECUTE stmt1; 
DEALLOCATE PREPARE stmt1; 

SET @s=CONCAT('insert ', @newtable, ' select *  from  watchlist order by Symbol,Date');
select @s;

PREPARE stmt1 FROM @s; 
EXECUTE stmt1; 
DEALLOCATE PREPARE stmt1; 

