# Blockbyte
My version of BlockBit for Scratch


(Scratch is a project of the Scratch Foundation, in collaboration with the Lifelong Kindergarten Group at the MIT Media Lab. It is available for free at [https://scratch.mit.edu](https://scratch.mit.edu))

# Setup
1. Download the repository at `https://github.com/BigGreenHat14/Blockbyte/archive/refs/heads/main.zip`
2. Extract the zip file
3. `cd` into / open the extracted zip
4. Configure the `.env` file for the account the server will use 
5. Run `python main.py -p id` to start the server (where python is your python executable and id is the [project id](https://github.com/BigGreenHat14/Blockbyte/wiki/How-to-get-project-id) of your **shared** remix)
6. Configure `restart_blockbyte.bat` (Windows) or `restart_blockbyte.sh` (Unix) files

**If you need to, [create a venv](https://www.w3schools.com/python/python_virtualenv.asp)**

Bonus:
Run `python main.py -p id -m` to start the menu (where python is your python executable and id is the [project id](https://github.com/BigGreenHat14/Blockbyte/wiki/How-to-get-project-id) of your **shared** remix)

If this doesn't work create an issue and i might help

# Admins
Admins can login to other people's accounts, they cannot however, change their balance excluding transfers.

To login to another person's account as an admin, press the "." key, then type "viewas&username" (without quotes) where username is the target users name (without @)

To login to your own account again, login to another persons account, but use your username instead

If you are not an admin, you will not be logged in to another account and will temporarially have the message "haxx0r not haxx0r" (without quotes) in your notifications until you reload
