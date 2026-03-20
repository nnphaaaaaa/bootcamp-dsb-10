#Essencial Python for DA


#- OOP (object Oriented Programming)
#- Try Except
#- Read and write file
#- context manager
#- Pandas & Numpy (on demand)
#- Request API


## ---------------------------------------- ##
## OOP
    # crate a new class
class Dog :
    # create method
    # init == initialization
    def __init__ (self, name, age, breed) :
        self.name = name
        self.age = age
        self.breed = breed

    def bark(self):
        print(f"{self.name} is barking woof woof !")

    def hbd(self):
        self.age +=1
        print(f" hbd {self.name} is {self.age} years old")



    # create a new attribute e.g. name, age, breed
dog1 = Dog("milo", 1, "Chihuahua")
dog2 = Dog("david", 2, "Husky")

    # call methods  e.g. function (bark(, hbd() )
print(f"{dog1.name} is {dog1.breed}")
dog2.bark()
dog1.hbd()


### super class เป็นส่วนหนึ่งของ OOP , software engineer จะใช้บ่อยกว่า

class Person :
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # extension
class Employee(Person):
    def __init__(self, name, age, salary):
        super().__init__(name, age)
        self.salary = salary

    def greeting(self):
        print("Hello world")

person1 = Person("Milo", 24)
person2 = Employee("David", 24, "Google")

person2.greeting()



## ---------------------------------------- ##
## Try Except

try:
    result = 1/0
except:
    print("this is an error message!")



## ---------------------------------------- ##
## Read & Write Files

## read csv file

import csv
#try:
#    file = open("hotel.csv", "r")
#    data = csv.reader(file)
#    for row in data :
#        print(row)

#    file.close()
#except :
#    print("Error")
#finally :
#    print("DONE")



read_data = []
with open("hotel.csv", "r") as file :
    data = csv.reader(file)
    for row in data :
        read_data.append(row)

read_data

    ### header
read_data[0]

    ### body data
read_data[1: ]

    ### for loop to calculate average  price per night
#prices = []

#for row in read_data[1: ]:
#  prices.append(int(row[-1]))

#print(f"AVG price per night: {sum(prices)/ len(prices)}")





    ## ---------------------------------------- ##
## Write Files

import csv

head = ["id", "name", "city"]
body = [
    [1,"CU", "BK"],
    [2, "LSC", "LD"],
    [3, "reading", "reading"]

]

    # write file + context manager
with open("school.csv", "w") as file :
    writer = csv.writer(file)
    writer.writerow(head)
    writer.writerows(body)



## ---------------------------------------- ##
## Pandas & Numpy (modern python)

import pandas as pd

df = pd.read_csv("hotel.csv")
df.head()

df1 = pd.read_csv("hotel.csv")
df1.head()

df.to_csv("hotel2.csv") # export csv file


    ## read data from internet
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/refs/heads/master/penguins.csv"

df_penguins = pd.read_csv(url)
df_penguins.head()
print(df_penguins.head())

    # select column
print(df_penguins[["species", "island", "body_mass_g"]])

    # filter rows
print(
    df_penguins[["species","body_mass_g","island"]]\
  .query("species == 'Adelie' and island == 'Dream' ")\
  .head(10)
)

    # filter without query
print(
    df_penguins[df_penguins["body_mass_g"] >= 4500 ][["species", "sex", "body_mass_g"]]
)


## ---------------------------------------- ##
# Requests

# requests api
import requests

    # api endpoint
url = "https://swapi.info/api/people/1"

response =  requests.get(url)
response.json()

response.json()["name"]
response.json()["mass"]


        # for loop
import requests
import time

#names = []
characters = []

for i in range(5) :
    url = f"https://swapi.info/api/people/{i+1}"
    response = requests.get(url)
    response_json = response.json()
    data = [
        response_json["name"],
        response_json["height"],
        response_json["mass"]
    ]
    #names.append(response_json["name"])
    characters.append(data)
    #print(response_json["name"])
    print(f" Success : { i+1 }")
    time.sleep(5)

print(names)

## ---------------------------------------------------------------------------------------------------------------##



