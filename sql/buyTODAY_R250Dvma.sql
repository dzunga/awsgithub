select * from stockvma 
where Date>'2018-03-05' 
and (R21Dvma =R250Dvma)
and (R250Dvma >0)  
and (Volume >250000)
order by Date desc,  9DVMA desc