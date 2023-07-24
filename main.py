from instagrapi import Client
from instagrapi.exceptions import (
    ClientLoginRequired,
    ClientError,
    ClientForbiddenError,
    ClientNotFoundError,
    BadPassword,
    LoginRequired,
    PrivateAccount,
    TwoFactorRequired)
from getpass import getpass


def login() -> tuple[bool, str]:
    print("\nLogin to Instagram")
    user = input("Username: ")
    password = getpass("Password: ")
    two_factor = str(input("2FA (optional): ")).strip()

    success = (True, user)
    fail = (False, "")

    print(f"\nLogging in as {user}\n")

    try:
        if two_factor == "":
            cl.login(user, password)
        else:
            cl.login(user, password, verification_code=two_factor)
        return success
    except BadPassword:
        print("Bad password")
        return fail
    except TwoFactorRequired:
        print("Two factor code is required")
        return fail
    except (ClientForbiddenError, PrivateAccount):
        print("Account is private")
        return fail
    except ClientNotFoundError:
        print("User not found")
        return fail
    except ClientError as e:
        print(e)
        return fail
    except (LoginRequired, ClientLoginRequired):
        print("Login required")
        return fail


def menu() -> str:
    print("1. See who doesn't follow you back")
    print("2. See who you don't follow back")
    print("3. Exit")

    while True:
        choice = input("> ")
        if choice in ["1", "2", "3"]:
            return choice
        else:
            print("Invalid choice")


cl = Client()
while True:
    ok, username = login()
    if ok:
        break

print("Login success!\nPlease wait...\n")

followers_dict = cl.user_followers(cl.user_id_from_username(username))
followers_ids = followers_dict.keys()
followers = followers_dict.values()
followers = [user.username for user in followers]

following_dict = cl.user_following(cl.user_id_from_username(username))
following_ids = following_dict.keys()
following = following_dict.values()
following = [user.username for user in following]

while True:
    print()
    option = menu()

    if option == "1":
        # find all users that are not following you back
        not_following_back = [user for user in following if user not in followers]

        print("\nUsers that don't follow you back:\n")
        for user in not_following_back:
            print(user)
    elif option == "2":
        # find all users that you are not following back
        not_following = [user for user in followers if user not in following]

        print("\nUsers that you don't follow back:\n")
        for user in not_following:
            print(user)
    else:
        exit(0)
