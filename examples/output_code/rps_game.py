import random

CHOICES = ['rock', 'paper', 'scissors']
RESULTS = {
    'rock': {'win': 'scissors', 'lose': 'paper'},
    'paper': {'win': 'rock', 'lose': 'scissors'},
    'scissors': {'win': 'paper', 'lose': 'rock'}
}

def generate_computer_choice():
    return random.choice(CHOICES)

def determine_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return 'tie'
    elif RESULTS[player_choice]['win'] == computer_choice:
        return 'player'
    else:
        return 'computer'

def display_help():
    print("Welcome to Rock-Paper-Scissors!")
    print("To play, enter your choice (rock, paper, scissors) or 'q' to quit.")

def get_user_choice():
    while True:
        choice = input("Enter your choice: ").lower()
        if choice in CHOICES + ['q']:
            return choice
        else:
            print("Invalid choice. Please try again.")

def display_result(player_choice, computer_choice, winner):
    print(f"Player chose {player_choice}.")
    print(f"Computer chose {computer_choice}.")
    if winner == 'tie':
        print("It's a tie!")
    else:
        print(f"The {winner} wins!")

def main():
    display_help()
    while True:
        player_choice = get_user_choice()
        if player_choice == 'q':
            break
        computer_choice = generate_computer_choice()
        winner = determine_winner(player_choice, computer_choice)
        display_result(player_choice, computer_choice, winner)

if __name__ == "__main__":
    main()