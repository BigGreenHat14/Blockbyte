#   ____  _            _    ____        _                                          
#  | __ )| | ___   ___| | _| __ ) _   _| |_ ___       ___  ___ _ ____   _____ _ __ 
#  |  _ \| |/ _ \ / __| |/ /  _ \| | | | __/ _ \     / __|/ _ \ '__\ \ / / _ \ '__|
#  | |_) | | (_) | (__|   <| |_) | |_| | ||  __/     \__ \  __/ |   \ V /  __/ |   
#  |____/|_|\___/ \___|_|\_\____/ \__, |\__\___|     |___/\___|_|    \_/ \___|_|   
#  <3 bgh                         |___/                                            

import pickle
import os
import sys
import scratchattach as sa
import requests
import math
import argparse
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser(description="Blockbyte Server")
parser.add_argument("-p","--project", type=int, help="Project ID")
parser.add_argument("-m","--menu", action="store_true", help="Start CLI menu instead of server")
args = parser.parse_args()

def save_data(project_id, users):
    with open(f"blockbytedb_{project_id}", "wb") as f:
        pickle.dump((users), f)

def load_data(project_id):
    if os.path.exists(f"blockbytedb_{project_id}"):
        with open(f"blockbytedb_{project_id}", "rb") as f:
            return pickle.load(f)
    else:
        return ({})

# User class
class User:
    def __init__(self):
        self.theme = "56.7"
        self.balance = 100
        self.notifications = ["Welcome to blockbyte!"]
        self.history = [] # Format (Incoming, Username, Amount, Product)

# Project initialization
def init_project(project_id):
    cloud = sa.login(os.getenv("USERNAME"),os.getenv("PASSWORD")).connect_scratch_cloud(project_id)
    client = cloud.requests()

    users = load_data(project_id)
    def account_verify(requester):
        if requester not in users.keys():
            users[requester] = User()
    @client.request
    def info():
        username = client.get_requester()
        account_verify(username)
        try:
            toreturn = []
            user = users[username]
            toreturn.append(username)
            toreturn.append(user.balance)
            toreturn.append(user.theme)
            toreturn += list(reversed(user.notifications))
        except Exception as e:
            toreturn = ["Error : check notifications", "0", "Copy everything into the comments pls:",str(type(e)), str(e)]
        save_data(project_id, users)
        return toreturn

    @client.request
    def dismiss():
        account_verify(client.get_requester())
        users[client.get_requester()].notifications = []
        save_data(project_id, users)
        return "k"

    @client.request
    def transfer(othername, amount, product):
        username = client.get_requester()
        if othername not in users.keys():
            try:
                if not othername.startswith("test"):
                    sa.get_user(othername)
            except sa.exceptions.UserNotFound:
                return "x"
            account_verify(othername)
        account_verify(username)
        try:
            amount = round(float(amount))
            user = users[username]
            user2 = users[othername]
            if amount > user.balance or amount < 1:
                return "x"
            user.balance -= amount
            user2.balance += amount
            user.history.append((False,othername,amount,product))
            user2.history.append((True,username,amount,product))
            if product != "":
                user2.notifications.append(f"{username} bought {product} for {amount} Blockbyte{'s' if amount != 1 else ''}")
            else:
                user2.notifications.append(f"{username} sent you {amount} BlockByte{'s' if amount != 1 else ''}")
            save_data(project_id, users)
            return "k"
        except Exception as e:
            user.notifications.append(str(type(e)) + " " + str(e))
            return "x"

    @client.request
    def set_theme(num):
        account_verify(client.get_requester())
        try:
            users[client.get_requester()].theme = num
            save_data(project_id, users)
        except:None
        return "k"
    # Leaderboard feature
    @client.event
    def on_ready():
        print(f"Server for project {project_id} is running :D")
    # Start the client
    client.start(thread=False)

def menu(id):
    def info(name):
        user = users[name]
        fullybreak = False
        while True:
            print()
            print(f"{name}'s Blockbyte Profile:")
            print(f" - Balance: {user.balance}")
            print(f" - Theme (hue value): {user.theme}")
            print(f" - Notifications:")
            for notification in reversed(user.notifications):
                print(f"    > {notification}")
            print(f" - Transactions")
            for transaction in reversed(user.history):
                if transaction[0]:
                    if transaction[3]:
                        print(f"    > {transaction[1]} --{transaction[2]}--> This User's \"{transaction[3]}\"")
                    else:
                        print(f"    > {transaction[1]} --{transaction[2]}--> This User")
                else:
                    if transaction[3]:
                        print(f"    > This User --{transaction[2]}--> {transaction[1]}'s \"{transaction[3]}\"")
                    else:
                        print(f"    > This User --{transaction[2]}--> {transaction[1]}")
            print()
            if input("Modify? (y/N) > ").lower() == "y":
                while True:
                    print()
                    print("(B)alance")
                    print("(N)otifications")
                    print("(T)heme")
                    print("(D)elete")
                    print("(E)xit user")
                    match input("? > ").lower():
                        case "b":
                            user.balance = int(input("Set balance to > "))
                        case "n":
                            match input("(C)lear or (A)ppend > ").lower():
                                case "c":
                                    user.notifications = []
                                case "a":
                                    user.notifications.append(input("Contents > "))
                        case "t":
                            user.theme = input("Enter hue value > ")
                        case "e":
                            break
                        case "d":
                            if input("Are you sure? (y/N) > ").lower() == "y":
                                del users[name]
                                fullybreak = True
                                break
            if fullybreak:
                break

            else:
                break
    users = load_data(id)
    while True:
        if username := input("Enter Username (blank to exit) > "):
            if username in users.keys():
                info(username)
            else:
                if input("No profile, Create one? (Y/n) > ").lower() != "n":
                    users[username] = User()
                    info(username)
        else:
            if input("Save? (Y/n) > ").lower() != "n":
                save_data(id,users)
                if os.path.exists("restart_blockbyte.sh"):
                    if input("Restart server? (Y/n) > ").lower() != "n":
                        os.system("bash restart_blockbyte.sh")
            sys.exit(0)

# Set project
if __name__ == "__main__":
    if args.menu:
        menu(args.projectid)
    else:
        init_project(args.projectid)
