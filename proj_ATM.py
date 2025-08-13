class ATM:

    def __init__(self, name, bank, balance):
        self.balance = balance
        self.name = name
        self.bank = bank

    # deposit
    def deposit(self, amt):
        self.balance += amt
        print(f"You just deposited {amt:.2f} THB.")
        print(f"Your balance: {self.balance}")

    #withdraw
    def withdraw(self, amt):
        if self.balance >= amt:
            self.balance -= amt
            print(f"You just withdrew {amt:.2f} THB.")
            print(f"Your balance: {self.balance}")
        else:
            print(f"Your balance: {self.balance}")
            print("not enough money.")

    # check_balance
    def check_balance(self):
        return(f"Your balance: {self.balance}")

    #otp
    def otp(self):
        otp = choice(range(1000,9999))
        print(f"Your otp is {otp}.")
        user_otp = input("input your otp: ")
        if int(user_otp) == otp:
            print("otp is correct.")
        else:
            print("otp is incorrect.")

    #identity_check
    def identity_check(self):
        return f"ATM Card Holder: {self.name}, Bank: {self.bank}, Balance: THB {self.balance}"

    # transfer 
    def transfer(self, amt, recipient ):
        if  self.balance >= amt:
            self.balance -= amt
            print(f"Transfer THB {amt} to {recipient}")
        else:
            print("Insufficient funds")

