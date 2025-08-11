library(titanic)
library(tidyverse)
library(caret)

# Load the Titanic dataset
data(titanic_train)
head(titanic_train)

# cleandata : Drop Not use Columns
titanic_train$PassengerId <- NULL
titanic_train$Name <- NULL
titanic_train$Ticket <- NULL
titanic_train$Cabin <- NULL
titanic_train$Embarked <- NULL

## drop NA (missing value)
titanic_train <- na.omit(titanic_train)
nrow(titanic_train) 

## split data
set.seed(42)
n <- nrow(titanic_train)
id <- sample(1:n, size = n * 0.7) ## 70% train 30% test

train_data <- titanic_train[id, ]
test_data <- titanic_train[-id, ]

## Train model
train_model <- glm(Survived ~ Pclass + Age+ sex + sibsp , data = train_data, family = "binomial")

# score data
pre_test <- predict(train_model,
                    newdata = test_data,
                    type = "response")

# create new table and column
test_data_new <- test_data %>%
  select (Survived, Pclass, Age)

test_data_new$prob <- pre_test
test_data_new$pred <- ifelse(pre_test >= 0.5, 1, 0)

# create confusion matrix 
confusion_matrix <- table(test_data_new$pred, test_data$Survived, dnn = c("Predicted", "Actual"))

## model evaluation
##accuracy
accuracy <- cat("Accuracy:" , (confusion_matrix[1,1] + confusion_matrix[2,2]) / sum(confusion_matrix))

## precision
precision <- cat("Precision:" , confusion_matrix[2,2] /(confusion_matrix[2,1] + confusion_matrix[2,2]))

## recall
recall <- cat("Recall:" , confusion_matrix[2,2] /(confusion_matrix[1,2] + confusion_matrix[2,2]))

##F1-score
F1_score <- cat("F1-score: ", 2* ((0.68 * 0.48)/(0.68 + 0.48)))

