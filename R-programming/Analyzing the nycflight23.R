# install packages 
install.packages("nycflights23")
install.packages("dplyr")


# load library
library(dplyr)
library(nycflights23)
library(tidyverse)


#preview dataset
glimpse(flights) 
glimpse(airlines)
glimpse(airports)
glimpse(planes)
glimpse(weather)


# clean dataset
flights23  <- drop_na(flights)
glimpse(flights23)

airlines23 <- drop_na(airlines)
glimpse(airlines23)

airports23 <- drop_na(airports)
glimpse(airports23)

planes23  <- drop_na(planes)
glimpse(planes23)

weather23 <- drop_na(weather)
glimpse(weather23)


## Which airlines have the longest average departure delays?

    # Join the flights and airlines datasets, then calculate the average departure delay
longest_delays <- flights23 %>%
   filter(!is.na(dep_delay)) %>%
   group_by(carrier) %>%
   summarise(
    avg_delay  = mean(dep_delay, na.rm = TRUE )
    ) %>%
   left_join(airlines, by = "carrier" ) %>%
   arrange(desc(avg_delay)) %>%
   select (name, avg_delay)
 
    # Print the top 10 airlines with the longest average departure delays
 print(longest_delays, n =10)


## What is the relationship between weather conditions (e.g., wind speed or precipitation) and flight delays?

    # Join the flights and weather datasets
flight_weather <- flights23 %>%
  inner_join(weather23 , by = c("year", "month", "day", "hour", "origin"))

    # Analyze the relationship between wind speed and departure delay
    # group by wind speed, filter out missing delay values, and then summarize the average delay
wind_delay_analysis <- 
  flight_weather %>%
  filter(!is.na(dep_delay)) %>%
  group_by(wind_speed) %>%
  summarise(
    avg_delay = mean(dep_delay, na.rm = TRUE) ,
    num_flights = n()
  ) %>%
    arrange(desc(wind_speed))

# Display the results
print(wind_delay_analysis)

## ----------- ## 
  # Analyze the relationship between precipitation and departure delay
precip_delay_analysis <- flight_weather %>%
  filter(!is.na(dep_delay), precip > 0) %>% # Focus on days with precipitation
  group_by(precip) %>%
  summarise(
    avg_delay = mean(dep_delay, na.rm = TRUE),
    num_flights = n()
  ) %>%
  arrange(desc(precip))

# Display the results
print(precip_delay_analysis, n = 15)


## Which planes (by tail number) are the most reliable, and which have the most delays?

    # find the most reliable planes (lowest  averge delay)
most_reliable_planes <- 
  flights23 %>%
  filter(!is.na(dep_delay) , !is.na(tailnum)) %>%
  group_by(tailnum) %>%
  summarise(
    avg_delay = mean(dep_delay), 
    total_flights =  n()
  ) %>%
    filter(total_flights >= 25) %>% # Filter for planes with at least 25 flights
    arrange(desc(avg_delay)) %>%
    head(10 ) 
  
    # Print the top 10 most reliable planes
print(most_reliable_planes)


 ## What are the most popular destinations for flights departing from a specific NYC airport?

    # Choose the airport you want to analyze (JFK, LGA, or EWR)
airport_code <- "JFK"

popular_destinations <-
  flights23 %>%
  filter(origin == airport_code ) %>%
  group_by(dest) %>%
  summarise(num_flights = n()) %>%
  arrange(desc(num_flights)) %>%
  left_join(airports , by = c("dest" = "faa")) %>%
  select(dest_code = dest, dest_name = name, num_flights ) %>%
  head(10)

print(popular_destinations)






