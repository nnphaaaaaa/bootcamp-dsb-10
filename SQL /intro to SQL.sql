--  intro to basic SQL

  -- # 1. create table 
 CREATE TABLE employee (
  id INT UNIQUE, 
  name text,
  department text, 
  posiontion text,
  salary real 
);	


 -- # 2. Insert data
insert into employee VALUES
    (1, 'David', 'Marketing', 'CEO',100000), 
    (2, 'Jonh', 'Marketing',     'VP',85000),
    (3, 'Marry', 'Sales', 'Manager', 60000)
    ;


-- # 3. Select data
SELECT * 
/* SELECT name, salary, dapartment, position  */
from employee
;


-- # 4. Transform column
SELECT 
  name, 
  alary,
  salary*1.15 as new_salary,
  lower(name) || '@company.com' as company_email
from employee
;


-- # 5. Filter data
SELECT 
    name, 
    salary,
    salary*1.15 as new_salary,
    lower(name) || '@company.com' as company_email
from employee

select *
from employee
where department = 'Marketing' and salary >90000 

select *
FROM employee
--where department ='IT' OR department = 'Marketing'
WHERE department in ('Marketing', 'IT')
;


--# 6. Update data
UPDATE employee 
set salary =99000
WHERE id =1 
;


-- # 7. Delete record
DELETE from employee
--WHERE id = 5
--WHERE name = 'Walker'  --assume Walker is onlyone. 
WHERE id in (2,4) --delete หลายคนพร้อมกัน
;

select * 
from employee
;


-- # 8.  Alter table
alter table employee rename to Myemployee ;
select * from Myemployee
;


-- # 9. backup data and drop table
create table Myemployee_backup AS
	SELECT * from Myemployee
    
--drop table Myemployee_backup
drop TABLE Myemployee
;
