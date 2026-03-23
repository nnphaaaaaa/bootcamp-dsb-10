## Matplotlib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

    # create a plot
coffee = np.array([0, 1, 2, 3, 4, 5])
energy = np.array([3, 6, 8, 9, 8.5, 7])
#plt.show()

    # setting up the canvas
plt.figure()                     # 1. Set up the canvas
plt.plot(coffee, energy)   # 2. Create the plot
#plt.show()                       # 3. Display the plot

    # setting a Titles & Axis labels
plt.title('Emails received on the week of 12/2')
plt.xlabel('Day of the Week')
plt.ylabel('Number of Emails')
#plt.show()

    # setting a Line colors & Line styles
plt.plot(coffee, energy, color = "skyblue", linestyle = "--", linewidth = 2)
#plt.show()


    # for example : Points for NBA teams


games = np.array( [1, 2, 3, 4, 5])

# Points for the NBA teams
bulls_points = np.array([89, 104, 132, 203, 115])
lakers_points = np.array([102, 110, 95, 108, 115])
celtics_points = np.array([98, 105, 100, 112, 107])
warriors_points = np.array([110, 99, 105, 120, 115])


plt.figure()
plt.plot(games, bulls_points, label='Chicago Bulls',  color = 'purple', linestyle = '--')
plt.plot(games, lakers_points,label='Boston Celtics',  color = 'red', linestyle = '-.')
plt.plot(games, celtics_points,label='Golden State Warriors',  color = 'green', linestyle = ':')
plt.plot(games, warriors_points, label='Los Angeles Lakers',  color = 'blue', linestyle = '-')

plt.title('Bulls vs. Celtics vs. Warriors vs. Lakers')
plt.xlabel('Game')
plt.ylabel('Points')

plt.legend()
plt.show()


    # import files
        # import pandas dataframes


df = pd.DataFrame({
  'month': ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  'adoptions': [45000, 52000, 48000, 43000, 38000, 41000]
})

plt.figure()
plt.plot(df['month'], df['adoptions'], color = 'pink', linestyle = ':')
plt.title('Adoption Rate of Kittens')
plt.xlabel('Month')
plt.ylabel('Adoptions')
plt.grid(True)
plt.show()


        # import CSV file


df = pd.read_csv('./data/gearsparks_emporium_weekly_sales.csv')

plt.figure()
plt.plot(df['Day'], df['Weapon'])
plt.title('Weapon Sales at Gearspark\'s Emporium')
plt.xlabel('Day of the Week')
plt.ylabel('Number of Weapons Sold')
plt.show()



    ## scatter plot

data = {
  'hours': [1, 2, 3, 4, 5, 6, 7, 8],
  'scores': [55, 30, 56, 70, 72, 81, 81, 92]
}

df = pd.DataFrame(data)

plt.scatter(df['hours'], df['scores'])

plt.title('Study Time vs. Test Score')
plt.xlabel('Study Time (Hours)')
plt.ylabel('Test Score')
plt.show()


     ## Bar chart

df = pd.DataFrame({
  'aquarium': ['Monterrey Bay', 'Georgia Aquarium', 'Shedd Aquarium', 'National Aquarium'],
  'shark': [5, 4, 4, 2],
  'dolphin': [8, 12, 10, 5],
  'octopus': [7, 20, 8, 4],
  'sea turtle': [12, 5, 6, 3],
  'jellyfish': [30, 25, 20, 15]
})

plt.figure()
plt.bar(df['aquarium'], df['shark'])

plt.title('Sharks in Aquariums')
plt.xlabel('Aquarium')
plt.ylabel('Number of Sharks')

plt.show()


    ## Pie chart

df = pd.DataFrame({
  'toppings': ['Pepperoni', 'Cheese', 'Mushroom', 'Pineapple', 'Prosciutto', 'Artichoke'],
  'orders': [40, 25, 20, 15, 4, 5]
})

plt.figure()

explode = [0.1, 0, 0, 0, 0, 0]
plt.pie(df['orders'], labels=df['toppings'], autopct='%d%%', explode=explode)

plt.title('Favorite Pizza Toppings')

plt.show()


## Object-Oriented plotting (OO)
    # we start to build more complex plots! OO provides us with more flexibility as we work with figure and axes objects directly.

df = pd.DataFrame({
    'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
    'The_Housemaid_Sales': [31.01, 29.82, 22.12, 15.67, 12.63],
    'Marty_Supreme_Sales': [11.55, 30.75, 19.05, 11.67, 8.57]
})

fig, ax = plt.subplots()

ax.plot(df['Week'], df['The_Housemaid_Sales'], label = 'The_Housemaid_Sales')
ax.plot(df['Week'], df['Marty_Supreme_Sales'], label = 'Marty_Supreme_Sales')

ax.set_title('Box office sales')
ax.set_xlabel('Week')
ax.set_ylabel('Sales')
ax.legend()
plt.show()




