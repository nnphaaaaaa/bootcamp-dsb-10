# basic programming for data analyst
# 1.variable
# 2.data types
# 3.data structures
# 4.function
# 5.control flow



## [1] variables

new_income <- 35000 * 1.2
expense <- 22000
saving <- new_income - expense


## remove variables

rm(income)


## [2] data types
## numeric, character, logical, date

money_in_my_pocket <- 150
my_name <- "nnphaaa"
my_age <- 28
movielover <- TRUE #FALSE
today_date <- as.Date("2024-07-02")

## check data types

class(my_age)
class(my_name)
class(movielover)
class(today_date)


## change data types

as.numeric("100")
as.numeric(TRUE)
as.numeric(FALSE)

as.character(100)

as.logical(1)
as.logical(0)


## [3] data structures
## 1. vector
## 2. matrix
## 3. list
## 4. dataframe


## [3.1] vector, contains only single data type

friend <- c("nnphaa", "john", "jane", "anne", "marry")
ages <- c(27, 30, 33, 35, 45)
marvel_lover <- c(T, T, F, T)
my_specail_vector <- c(a=1, b=2, d=3)


#subset by position
friend[6]
friend[1:3]
friend[c(1,3,5)]

#subset by condition
ages >= 30
ages[ages >= 30]
friend[ages >= 30]

#subset by name 
my_specail_vector["a"]


## [3.2] matrix

m1 <- matrix(1:4, ncol=2)
m2 <- matrix(5:8, ncol=2, byrow = TRUE) 

my_vec <- 1:25
matrix(my_vec, nrow=5,byrow = T)

# Vectorization  
m1 +100
m1 * m2
m1 %% m2


## [3.3] list

jon <- list(
  first_name = "jon",
  last_name = "wick",
  age = 45,
  city ="Bangkok",
  occupation = "teacher",
  salary =100000,
  mavel_fan = TRUE,
  mavel_movie = c("Thor" , 
                  "Loki Series",
                  "Infinity war")
)

#subset by position output key:value
jon[3]

#subset by position output value
jon[[3]]

#subset by position 
jon$city
jon$mavel_movie[2]
jon$mavel_movie[c(2,3)]

#subset by name 
jon[["occupation"]]


# assign new key = value data structure ##JSON
mary <- list(
  full_name = "mary anne",
  age =28,
  city = "London",
  football_fan = T,
  fav_team = "Liverpool", "Chelsea"
)


#nested list
custumer <- list(id01 =jon,
                 id02 = mary)



## [3.4] data frame

id <- 1:5
friends <- c("nnphaa", "john", "anna", "david", "mary")
ages <- c(28,34,29,30,34)
dog_lover <- c(T,T,F,F,F)
city <- c("BKK", "LON","LON","TOK","TOK")

#create the data frame
df <- data.frame(id, friends,ages, dog_lover, city)

#structure of this df
str(df)

#dimension
dim(df)

#summary
summary(df)

#subset dataframe #df[row, column]
df[3, 2]
df[5, 2]
df[1:3, ]
df[1:3, 4:5]
df[1:2, c(2,5)]
df[1:3, c("friends","city")]

#subset by condition
df[df$ages <30, ]

#three ways that we can subset in R
# []
# 1. by position 
# 2. by name
# 3. by condition

df[df$dog_lover == T, ]
df[df$friends == "nnphaa", ]
df[df$city != "LON", ]


# working with dataframe
# create new column
df$fav_manu <- c("somtum", "hotdog", "pizza", "french fried", "hotdog")

#remove column
df$fav_manu <- NULL 

##append data
df2 <- data.frame(
  id =6:7,
  friends = c("wick", "dada"),
  ages =c(25,26),
  dog_lover =c(T, T),
  city = c("SEOUL","SEOUL")
)

## row bind
full_df <- rbind(df,df2)

#write CSV file to exort 
write.csv(full_df, "result.csv", row.names = F)

#read CSV file
read.csv("result.csv")


## [4] function

hello <- function(){
  print("hello world")
}

my_stupid_func <- function() {
  hello()
  hello()
  hello()
}


## create a new function 'cube'
cube <- function(base, power){
  base** power
}

  # create your own function
greeting <- function() {
  print("hello world")
}

greeting_name <- function(name) {
  text <- paste0("Hello! ", name)
  print(text)
}

  # simple function
add_two_num <- function(x,y) {
  return(x + y)
}

  #default argument
add_two_num <- function(x=10 ,y=12) {
  return(x + y)
}

cube <- function(base, power=3){
  base ** power
}

cube <- function(base , power = 3)  base ** power 

  #function call another function(s)
hi1 <- function() print("hi ")
hi2 <- function() print("hi hi! ")
hi3 <- function() print("hello! ")

all_hi <- function(){
  hi1()
  hi2()
  hi3()
}


## [5] control flow : if for while
## if for while

ifelse( "Hi" == "hi", T, F)

score = 180 
if( score >= 200 ) {
  print("passed")
} else {
  print("failed")
}

#IFS() in googlesheets
score = 50

if( score >= 80) {
  print("A")
} else if (score >= 70) {
  print("B")
} else if(score >= 60) {
  print("C")
} else if(score >= 50) {
  print("C")
} else if(score >= 50) {
  print("D")
} else {
  print("F")
}


##create function + if else 
grading  <- function(score) {
  if( score >= 80) {
    return("A")
  } else if (score >= 70) {
    return("B")
  } else if(score >= 60) {
    return("C")
  } else if(score >= 50) {
    return("C")
  } else if(score >= 50) {
    return("D")
  } else {
    return("F")
  }
}

grading(40)


##for loop

1:20 

1:20 %% 2 == 0

#vectorization

for (i in 1:10) {
  print(i*2)
}

num <- c(25, 30, 40, 100, 1225)
for (i in num) {
  if (i %% 2 == 0) {
    print(paste0(i,": even number"))
  } else {
    print(paste0(i,": odd number"))
  }
}

ifelse(num %%2 ==0, "even", "odd")


## while loop
count <- 0 
while(count < 5) {
  print("forget me not ")
  count = count + 1
  if ( count == 5) {
    print("fogive me now")
  }
}

## take in put from a user 
## user input is character  
user_name <- readline("what's your name :" )
print(user_name)
user_pw <- readline("your password")

## Facebook login logic
users <- c("toy", "john" , "mary")
pw <- 1234

fb_login <- function() {
  print("Welcome to Facebook")
  username <- readline("Username: ")
  password <- readline("Pasword : ")
  if((username %in% users) & (password == pw)) {
    print("login successfully")
  } else {
    print("Try again")
  }
}

###fruits <- c("apple","orange", "grape")
### "apple " %in% fruits
###[1] FALSE
###"apple" %in% fruits
###[1] TRUE




###homework 
###chat bot order pizza

###game rock paper scissor




