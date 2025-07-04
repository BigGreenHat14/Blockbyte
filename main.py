#   ____  _            _    ____        _                                          
#  | __ )| | ___   ___| | _| __ ) _   _| |_ ___       ___  ___ _ ____   _____ _ __ 
#  |  _ \| |/ _ \ / __| |/ /  _ \| | | | __/ _ \     / __|/ _ \ '__\ \ / / _ \ '__|
#  | |_) | | (_) | (__|   <| |_) | |_| | ||  __/     \__ \  __/ |   \ V /  __/ |   
#  |____/|_|\___/ \___|_|\_\____/ \__, |\__\___|     |___/\___|_|    \_/ \___|_|   
#  <3 bgh                         |___/                                            

#yes i did partially use chatgpt thank you for asking - every dev in 2025

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
parser.add_argument("-p","--projectid", type=int,help="Project ID")
parser.add_argument("-m","--menu", action="store_true", help="Start CLI menu instead of server")
args = parser.parse_args()

# Utility functions for persistent data storage
def save_data(project_id, users):
    with open(f"blockbytedb_{project_id}", "wb") as f:
        pickle.dump((users), f)

def load_data(project_id):
    if os.path.exists(f"blockbytedb_{project_id}"):
        with open(f"blockbytedb_{project_id}", "rb") as f:
            return pickle.load(f)
    else:
        return ({})

def lowercase_keys(d):
    return {str(k).lower(): v for k, v in d.items()}

SETTING_NAMES = ("nf_comment","nf_project")
SETTING_DEFAULTS = {"nf_comment":False,"nf_project":True}
# User class
class User:
    def __init__(self,name):
        self.name = name
        self.safe_name = fix_name(name)
        self.theme = "56.7"
        self.balance = 100
        self.notifications = ["Welcome to blockbyte!"]
        self.history = [] # Format (Incoming,User,Amount,Product)
        self.products = []
        self.settings = {}
    def get_setting(self,setting):
        return self.settings.get(setting,SETTING_DEFAULTS.get(setting,False))
    def notify(self,text):
        global session
        if self.get_setting("nf_project"):
            self.notifications.append(text)
        if self.get_setting("nf_comment"):
            user = session.connect_user(self.safe_name)
            try:
                user.post_comment(f"[Blockbyte] {text}")
            except:
                pass
def fix_name(name:str):
    return name.lstrip("@").lower()

# Project initialization
def init_project(project_id):
    users = load_data(project_id)
    def account_verify(requester):
        if requester.lower() not in users.keys():
            users[requester.lower()] = User(requester)
    @client.request
    def info():
        username = fix_name(client.get_requester())
        account_verify(username)
        toreturn = []
        user = users[username]
        toreturn.append(client.get_requester())
        toreturn.append(user.balance)
        toreturn.append(user.theme)
        for setting in SETTING_NAMES:
            toreturn.append(str(int(user.get_setting(setting))))
        toreturn += list(reversed(user.notifications))
        save_data(project_id, users)
        return toreturn

    @client.request
    def dismiss():
        name = fix_name(client.get_requester())
        account_verify(name)
        user = users[name]
        user.notifications = []
        save_data(project_id, users)
        return "k"

    @client.request
    def set_settings(settings:str):
        settings = settings.replace(" ","")[0:]
        name = fix_name(client.get_requester())
        account_verify(name)
        user = users[name]
        try:
            for name,value in zip(SETTING_NAMES,list(settings)):
                user.settings[name] = bool(int(value))
            save_data(project_id, users)
            return "k"
        except Exception as e:
            return "haxx0r not haxx0r"
    @client.request
    def transfer(othername, amount, product):
        username = fix_name(client.get_requester())
        othername = fix_name(othername)
        if othername not in users.keys():
            try:
                if not othername.startswith("test"):
                    sa.get_user(othername).name
            except sa.exceptions.UserNotFound:
                return "x"
            account_verify(othername)
        account_verify(username)
        try:
            amount = round(float(amount))
            user = users[username]
            user2 = users[othername]
            if (amount > user.balance or amount < 1) or (product not in user2.products and not product == ""):
                return "x"
            user.balance -= amount
            user2.balance += amount
            user.history.append((False,othername,amount,product))
            user2.history.append((True,username,amount,product))
            if product != "":
                user2.notify(f"{client.get_requester()} bought {product} for {amount} Blockbyte{'s' if amount != 1 else ''}")
            else:
                user2.notify(f"{client.get_requester()} sent you {amount} BlockByte{'s' if amount != 1 else ''}")
            save_data(project_id, users)
            return "k"
        except Exception as e:
            return "x"

    @client.request
    def set_theme(num):
        account_verify(fix_name(client.get_requester()))
        try:
            users[fix_name(client.get_requester())].theme = num
            save_data(project_id, users)
        except:None
        return "k"
    @client.request
    def add_product(name):
        username = fix_name(client.get_requester())
        account_verify(username)
        if not name in users[username].products:
            users[username].products.append(name)
        return "k"
    @client.request
    def discontinue(name):
        username = fix_name(client.get_requester())
        account_verify(username)
        if name in users[username].products:
            del users[username].products[users[username].products.index(name)]
        return "k"
    @client.event
    def on_ready():
        print(f"Server for project {project_id} is running :D")
    # Start the client
    client.start(thread=False)

def debug_menu(id):
    import __main__
    __main__.User = User
    def info(name):
        user = users[name]
        fullybreak = False
        while True:
            print()
            print(f"{name}'s Blockbyte Profile:")
            print(f" - Balance: {user.balance}")
            print(f" - Theme (hue value): {user.theme}")
            print(f" - Notifications")
            for notification in reversed(user.notifications):
                print(f"    > {notification}")
            print(f" - Products")
            for product in user.products:
                print(f"    > {product}")
            print(f" - Settings")
            for name in SETTING_NAMES:
                print(f"    > {name}: {user.get_setting(name)}")
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
                                    user.notify(input("Contents > "))
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
    print("Users:",", ".join(users.keys()))
    while True:
        if username := fix_name(input("Enter Username (blank to exit) > ")):
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
                        if os.name == 'nt':
                            os.system("restart_blockbyte.bat")
                        else:
                            os.system("bash restart_blockbyte.sh")
            sys.exit(0)

# Set project
if __name__ == "__main__":
    if args.menu:
        debug_menu(args.projectid)
    else:
        session = sa.login(os.getenv("USERNAME"),os.getenv("PASSWORD"))
        cloud = session.connect_scratch_cloud(args.projectid)
        client = cloud.requests()
        init_project(args.projectid)
