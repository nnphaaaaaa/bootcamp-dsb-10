-- ##   intermediate SQL part || 

-- # 1. Intersect & Except 
select * from book_shop
INTERSECT
select * from favourite_book
;

select * from book_shop
EXCEPT
select * from favourite_book
;


-- # 2. Union & Union All 
select * from book_shop
UNION ALL
select * from book_shop_new 
;

select * from book_shop
UNION 
select * from book_shop_new 
;


-- # 3. Subqueries
select * 
from tracks 
where milliseconds = (SELECT max(milliseconds) from tracks)
;


select firstname, lastname, country 
from (select * from customers WHERE country = 'USA')
;


-- 4. with clause 
with tmp as (
	select * from customers
)

select firstname , email, country
from tmp 
where  country = 'USA'
union 
select  firstname, email, country 
from tmp
;


with usa_customerss as (
	 select * FROM customers
	 where country = 'USA'
), invoice_y2009  AS (
	 select *  from invoices
  	 where invoicedate  between '2009-01-01' and '2009-12-31'
)

select sum(total) AS total_revenue_usa_cust_2009
from usa_customerss t1
JOIN invoice_y2009  t2
on t1.customerid =  t2.customerid
;


