# Essential concept in Python

# - lambda
# - map. filter
# - import module
# - regular expression
# - pandas & numpy
# - json



## ---------------------------------------- ##
## Lambda

    # create a new function in python (basic)
def hello() :
    return "Hello World"

hello()

def add_two_num(a, b) :
    return a + b

add_two_num(2,5)



    # lambda (shortcut to create function)
test = lambda x : print(x)
test("toy")

add_two = lambda num: print(num+2)
add_two(3)

test2 = lambda a,b : a+b
test2(5,6)

test3 = lambda name, fev_food : f"{name} love {fev_food}"
test3("Any", "patthai")


## ---------------------------------------- ##
# map / filter

## map
    #iterable

scores = [82, 78, 81, 66, 50]

for score in scores :
    if score > 80 :
        print('passed')
    else :
        print('failed')



    # define function ที่เราต้องการจะใช้ขึ้นมาสำหรับ items แต่ละตัวที่อยู่ใน list (scores) เสร็จแล้ว เราจะใช้ `map`
    # map ตัว grading เข้าไปที่ scores

def grading(score):
    if score > 80 :
        return "Passed🌞"
    else :
        return "Failed😕"

result = list(map(grading, scores))
print(result)

    # add five to scores
list(map(lambda x : x +5, scores))


## filter

scores

    # filter no function filter
students_scores_over_80 = []
for score in scores :
    if score > 80 :
        students_scores_over_80.append(score)
print(students_scores_over_80)

    # filter with lambda
list(filter(lambda x: x > 80, scores))

    ## more example

scores = [("toy", 2), ("top", 5), ("tap", 10), ("tank", 12)]
    # filter >= 5
print(
    list(filter(lambda x: x[1] >= 5, scores))
)


## ---------------------------------------- ##
## module / library

import random
class ATM :
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

    def __str__(self):
        return f"Name: {self.name}, Balance: {self.balance}"

    def get_otp(self):
        otp = random.randint(1, 100)
        return f"Your requested otp is {otp}"

    # get ATM method
my_account = ATM("orn", 100)
print(my_account)
print(my_account.get_otp())

    # standard python modules
import random
fruits = ["apple", "banana", "orange"]
for i in range(10):
    random.seed(42) # ล็อกผลลัพท์
    print(random.choice(fruits))


## ---------------------------------------- ##
# Regular expression

    ## import regular expression (re)
import re
text = "a duck cost $80 usd per piece duck"

print(re.search("duck", text))
text[2:6]

print(re.findall("duck", text))
print(re.findall("[0-9]{2}", text ))




## ---------------------------------------- ##
##Install new library / module


# pip install pandas
# pip install numpy
# pip list # see all library

    # server cannot connect to internet
    # cannot install pandas
import csv
with open("filename.csv", "r") as file :
    pass

## ---------------------------------------- ##
## working with JSON
 # Javascript Object Notation

profile = {
    "name": "toy",
    "age": 24,
    "movie" : ["toy story", "toy monster"],
    "city" : "San Francisco",
    "state" : "CA"
}

type(profile)


#import json
import json

    # write json file
with open("profile.json", "w") as file :
    json.dump(profile, file)


    # read json on file
with open("profile.json", "r") as file :
    data = json.load(file)

print(data)
data["movie"][1]


## ---------------------------------------- ##
## numpy
## numerical python  = matrix + computing

import random

nums = []

for i in range(10):
    nums.append(random.randint(1, 100))

print(nums)

    # not numpy
sum(nums)/ len(nums)

    # get numpy
import numpy as np
print(np.sum(nums),
      np.mean(nums),
      np.std(nums))


    # change to numpy array
    # array == vector in R

nums = np.array(nums)
type(nums)
nums

    # numpy mehod
print(nums,sum(),
      nums.max())


    # import pandas and numpy
import numpy as np
import pandas as pd

df = pd.DataFrame({
    "name": ["toy", "top", "tap"],
    "income": [1,2,3]
})

df["income"].median()


## ---------------------------------------- ##
## Web scrapping

# pip install gazpacho

#import library
import requests
from gazpacho import Soup


url = "https://raw.githubusercontent.com/toyeiei/python-test-bc12/refs/heads/main/index.html"

response = requests.get(url)
response.status_code

web = soup(response.text)
web

web.find("h1")

for h2 in web.find("li"):
    print(h2.strip()) # delete html text ทั้งหมด
