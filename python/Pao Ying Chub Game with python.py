import random

def game():
    print("Welcome to the Pao Ying Chub Game!")
  # Define game choices
    hands =["hammer", "paper", "crissor"]
    score = { "win " : 0  , "draw": 0, "lost ": 0 }
    rounds = 1
  
  ##Create control flow
    while rounds <= 10:
        #Greeting
        print("------------------")
        print(f"Round#{rounds}")

    # Computer and User  makes a random choice
        user_hand = input("Please choose one option (paper, scissor, hammer or quit): ").lower()
        comp_hand = random.choice(hands)
      
    # Check if the player wants to quit
        if user_hand == "quit":
            break
          
    # Validate player's input
        if user_hand not in hands:
            print("Invalid input. Please try again.")
            continue  # Skips the rest of the loop and starts over
            
        print(f"You chose {user_hand}!")
        print(f"Comp chose {comp_hand}!")
        
        # Determine the winner
        if user_hand == comp_hand:
            print("DRAW!!")
            score["draw"] += 1
        elif (user_hand == "hammer" and comp_hand == "scissor") or \
             (user_hand == "paper" and comp_hand == "hammer") or \
             (user_hand == "scissor" and comp_hand == "paper"):
            print("You WIN!!")
            score["win "] += 1
        else:
            print("You LOSE!!")
            score["lost "] += 1
            
        rounds += 1
    
    # Final game summary
    print("==================")
    print(f"You played for {rounds - 1} round(s).")
    print(f"Win: {score['win ']}, Draw: {score['draw']}, Lose: {score['lost ']}")
    print(f"Your score is {score['win ']}")

game()
