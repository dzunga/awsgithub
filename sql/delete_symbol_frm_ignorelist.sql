SET @my_symbol = 'ifl';

delete from movers2 where Symbol=@my_symbol;
delete from stock where Symbol=@my_symbol;
delete from stockvma where Symbol=@my_symbol;