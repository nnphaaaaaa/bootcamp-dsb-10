--##  intermediate SQL commands

-- # 1. CASE WHEN 
SELECT
  country,
  CASE
    WHEN country IN ('Canada', 'USA') THEN 'America'
    WHEN country IN ('Belgium', 'France', 'Italy') THEN 'Europe'
    ELSE 'Other'
  END AS region
FROM customers
;

SELECT
        company,
        CASE 
          WHEN company IS NOT NULL THEN 'Coporate'
          ELSE 'End Customer' 
          END AS segment
FROM customers
;


-- # 2. Date time 
select 
	InvoiceDate,
	cast(strftime( '%Y', invoicedate) as int ) as YEAR,
	strftime( '%m', invoicedate) as MONTH,
	strftime( '%d', invoicedate) as DAY,
	strftime( '%Y-%m', invoicedate) as yearmonth 
from invoices
where year = 2010;


-- # 3. Select data from multiple tables
SELECT *
FROM artists
JOIN albums 
on artists.ArtistId = albums.ArtistId
WHERE artists.ArtistId = 50
;


-- # 4. Inner join 
SELECT 
	A.artistid,
	A.name,
	b,title
FROM artists as A
JOIN albums AS B
ON A.artistid = B.artistid
--ON PK = FK
;

select 
        art. ArtistId,
	art.name,
	alb.Title,
	tra.name,
	tra.Composer
from artists  as art
join albums  as alb
on art.ArtistId = alb.ArtistId
join tracks as tra
on alb.AlbumId = tra.AlbumId

where art.name like 'Aero%' 
;


SELECT 
	artists.ArtistId,
    artists.Name ArtistName,
    albums.Title AlbumName,
    tracks.name Songs,
    genres.name GenreName
from artists
INNER JOIN albums  ON artists.ArtistId = albums.artistid
INNER JOIN tracks ON albums.albumid = tracks.AlbumId
INNER JOIN genres ON tracks.GenreId = genres.GenreId
;


-- # 5. Left join 
SELECT 
	A.artistid,
	A.name,
	b,title
FROM artists as A
LEFT JOIN albums AS B
ON A.artistid = B.artistid
--ON PK = FK
;


-- # 6. Random
SELECT
	name 
--    ,RANDOM() as ran
FROM tracks
ORDER BY RANDOM() DESC
LIMIT 5
;


-- # 7. WHERE clause
SELECT * FROM customers
WHERE country = 'USA'
;

SELECT * FROM customers
WHERE country = 'USA' AND state = 'CA'
;

SELECT * FROM customers
WHERE country = 'USA' OR country = 'United Kingdom'
;

SELECT * FROM customers
WHERE country IN ('USA', 'United Kingdom')
;

SELECT * FROM customers
WHERE country NOT IN ('USA', 'United Kingdom')
;

SELECT * FROM customers
WHERE email LIKE '%@gmail.com'
;

SELECT * FROM customers
WHERE email NOT LIKE '%gmail.com'
;

SELECT * FROM customers
WHERE company IS NULL
;

SELECT * FROM customers
WHERE company IS NOT NULL
;

SELECT * FROM customers
WHERE customerid BETWEEN 10 AND 15
;

select firstname, lastname,email, phone
from customers
WHERE firstname LIKE 'Leon__'
;

SELECT 
    artists.ArtistId,
    artists.Name ArtistName,
    albums.Title AlbumName,
    tracks.name Songs,
    genres.name GenreName
from artists, albums, tracks, genres
where artists.ArtistId = albums.artistid
		AND albums.albumid = tracks.AlbumId
    and tracks.GenreId = genres.GenreId
;



-- # 8. Coalesce 
select 
        company,
        COALESCE(company, 'End customer') as Company_clean
;


-- # 9. Aggregate function 
SELECT 
  AVG(Milliseconds, 2 ) AS avg_mill,
  SUM(Milliseconds) AS sum_mill,
  MIN(Milliseconds) AS min_mill,
  MAX(Milliseconds) AS max_mill,
  COUNT(Milliseconds) AS count_mill 
FROM tracks 
;

-- # 10. COUNT Distinct
select count(DISTINCT c.country)
FROM customers c
;


-- # 11. Group by
select count(1) as count_country, country 
FROM customers
GROUP by country
;


-- # 12. Having 
select 
        genres.name,
	count(1) as count_song
from genres,tracks
where genres.genreid = tracks.GenreId and genres.name <> 'Rock'
group by genres.name
HAVING count(*) >= 100

