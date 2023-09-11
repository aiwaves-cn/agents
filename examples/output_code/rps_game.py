import random

def get_user_choice():
    while True:
        user_choice = input("Enter your choice (rock, paper, scissors): ").lower()
        if user_choice in ["rock", "paper", "scissors"]:
            return user_choice
        else:
            print("Invalid choice. Please enter 'rock', 'paper', or 'scissors'.")

def determine_winner(user1_choice, user2_choice):
    if user1_choice == user2_choice:
        return "It's a tie!"
    elif (
        (user1_choice == "rock" and user2_choice == "scissors")
        or (user1_choice == "paper" and user2_choice == "rock")
        or (user1_choice == "scissors" and user2_choice == "paper")
    ):
        return "Player 1 wins!"
    else:
        return "Player 2 wins!"

def main():
    print("Welcome to Rock-Paper-Scissors Game!")
    while True:
        user1_choice = get_user_choice()
        user2_choice = get_user_choice()
        print(f"Player 1 chose {user1_choice}")
        print(f"Player 2 chose {user2_choice}")
        result = determine_winner(user1_choice, user2_choice)
        print(result)

        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again != "yes":
            break

if __name__ == "__main__":
    main()
