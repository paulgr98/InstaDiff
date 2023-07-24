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
from instagrapi.types import UserShort
from getpass import getpass
import json
import os


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
    print("3. Save current followers to file")
    print("4. Show diff between current followers and saved followers")
    print("5. Exit")

    while True:
        choice = input("> ")
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        else:
            print("Invalid choice")


def save_to_json(data: list[UserShort], filename: str) -> None:
    save_dict = {}
    for user in data:
        save_dict[user.pk] = user.username
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(save_dict, f, indent=4)


def load_from_json(filename: str) -> dict:
    # check if file exists, if not, create it
    if os.path.isfile(filename) is False:
        with open(filename, "w", encoding='utf-8') as f:
            json.dump({}, f)

    with open(filename, "r", encoding='utf-8') as f:
        data = json.load(f)
    return data


def show_diff(old_dict: dict, new_list: list[UserShort]) -> None:
    new_followers = []
    lost_followers = []
    changed_followers = []

    new_dict = {user.pk: user.username for user in new_list}

    for _id, _username in old_dict.items():
        if _id not in new_dict.keys():
            lost_followers.append(_username)
        elif _username != new_dict[_id]:
            changed_followers.append((_username, new_dict[_id]))

    for _id, _username in new_dict.items():
        if _id not in old_dict.keys():
            new_followers.append(_username)

    for _username in new_followers:
        print(f" + {_username}")

    for _username in lost_followers:
        print(f" - {_username}")

    for _old_username, _new_username in changed_followers:
        print(f" * {_old_username} -> {_new_username}")


cl = Client()
while True:
    ok, username = login()
    if ok:
        break

print("Login success!\nPlease wait...\n")

followers_dict = cl.user_followers(cl.user_id_from_username(username))
followers_us = list(followers_dict.values())
followers = [user.username for user in followers_us]

following_dict = cl.user_following(cl.user_id_from_username(username))
following_us = list(following_dict.values())
following = [user.username for user in following_us]

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
    elif option == "3":
        # save current followers to file
        save_to_json(followers_us, "followers.json")
        print("\nCurrent followers saved to file")
    elif option == "4":
        # show diff between current followers and saved followers
        saved_followers_dict = load_from_json("followers.json")
        show_diff(saved_followers_dict, followers_us)

    else:
        exit(0)
