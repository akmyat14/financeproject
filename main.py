import optRetrieval


print("This is a program to predict the price of call options on stocks")
choice = input("Do you have a stock or a specific option in mind?")

if choice == 'option':
    next_choice = input("Please input your option you would like to check")
    optRetrieval.given_option(next_choice)
else:
    print(NotImplementedError)
