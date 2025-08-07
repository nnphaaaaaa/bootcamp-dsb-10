## paper scissor hammer  - DSB11
## Pao Ying Chub
play_game <- function() {
  message("Welcome to the Pao Ying Chub Game!")
  hands <- c("paper", "scissor", "hammer")
  rounds <- 1
  result <- c(0,0,0)
  while(rounds <= 10) {
    message("------------------")
    message("Round#", rounds)
    comp_hand <- sample(hands, 1)
    user_hand <- readline("Please choose one option (paper, scissor, hammer or quit): ")
    
    #quit
    if (user_hand == "quit") 
      break
    
    message("You choose ", user_hand, "!")
    message("Comp choose ", comp_hand, "!")
    
    #result
    if (user_hand == comp_hand) {
      message("DRAW!!")
      result[2] <- result[2]+1
    } else if (
      (user_hand == "hammer"  && comp_hand == "scissor")||
      (user_hand == "paper"   && comp_hand == "hammer")   ||
      (user_hand == "scissor" && comp_hand == "paper")
    ) {
      message("You WIN!!")
      result[1] <- result[1]+1
    } else {
      message("You LOSE!!")
      result[3] <- result[3]+1
    }
    rounds <- rounds + 1
  }
message("==================")
message("You played for ", rounds -1, " round(s).")
message("Win: ", result[1], ", Draw: ", result[2], ", Lose: ", result[3])
message("Your score is ", result[1])
}
