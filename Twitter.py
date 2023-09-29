import uuid
import Database as dB
from datetime import datetime

users_table = dB.Table("users.txt")
likes_table = dB.Table("likes.txt")
tweets_table = dB.Table("tweet.txt")
retweet_table = dB.Table("retweet.txt")


# Handeling Twitter sessions
class Twitter:
    def __init__(self):
        print("Hello, Welcome to Twitter.")
        self.user = User()
        self.initial_commands()

    def initial_commands(self):
        print("Please enter a number based on What you want to do.")
        print("1. Log in", "2. Sign up", "3. Quit", sep="\n")
        command_number = input()
        if command_number == "1":
            self.log_in()
        elif command_number == "2":
            self.sign_up()
        elif command_number == "3":
            self.quit()
        else:
            print("Please enter a valid command number!")
            self.initial_commands()

    def log_in(self):
        global users_table
        user = User()
        print("Enter Username:")
        user.username = input()
        print("Enter Password:")
        user.password = input()

        # Searching for user in database and getting its values
        data = users_table.select(
            "$ SELECT FROM users WHERE username=={} AND password=={};".format(user.username,
                                                                              user.password))
        if data == "Not Found!":
            print(
                "The username and password you entered did not match our records. Please double-check and try again.")
            self.initial_commands()
        else:
            # Filling in all the data that exist for this user in the user object that we created
            for string in data:
                user_data = string
            self.process_data(user_data, user)
            print("Welcome back! You successfully logged into your account.")
            self.show_commands()

    def process_data(self, data, user):
        if tweets_table.select("$ SELECT FROM tweet WHERE creator=={};".format(user.username)) != "Not Found!":
            tweets = list(tweets_table.select("$ SELECT FROM tweet WHERE creator=={};".format(user.username)))
            for tweet in tweets:
                id = tweet[:37]
                index = str.index(tweet, ")")
                text = tweet[38:index]
                creator = tweet.split()[-3]
                date = "  ".join(tweet.split()[-2:])
                tweet_obj = Tweet(text, creator, True)
                tweet_obj.id = id
                tweet_obj.date = date
                user.tweets.append(tweet_obj)
        if retweet_table.select("$ SELECT FROM retweet WHERE username=={};".format(user.username)) != "Not Found!":
            user.retweets = list(
                retweet_table.select("$ SELECT FROM retweet WHERE username=={};".format(user.username)))
        if data != "Not Found!":
            user.phone = data.split()[2]
        self.user = user

    def sign_up(self):
        global users_table
        user = User()
        print("Username:")
        user.username = input()
        while users_table.select("$ SELECT FROM users WHERE username=={};".format(user.username)) != "Not Found!":
            print("This username already exists, please choose another one.")
            user.username = input()
        # Checking the length of username
        username_format = users_table.fields_properties['username'][-1]
        index = str.index(username_format, "(")
        username_length = int(username_format[index + 1:-1])
        while len(user.username) > username_length or len(user.username) == 0:
            print("Please enter a valid username with a length between 0 and {}".format(username_length))
            user.username = input()
        print("Password:")
        user.password = input()
        # checking the password format
        password_format = users_table.fields_properties['password'][-1]
        index = str.index(password_format, "(")
        password_length = int(password_format[index + 1:-1])
        while len(user.password) > password_length or len(user.password) == 0:
            print("Please enter a valid password with a length between 0 and {}".format(password_length))
            user.password = input()
        print("Phone:")
        user.phone = input()
        # Checking the type of phone number:
        while True:
            try:
                int(user.phone)
                break
            except:
                print("Please enter a valid phone number:")
                user.phone = input()
        users_table.insert("$ INSERT INTO users VALUES ({},{},{});".format(user.username, user.password, user.phone))
        print("You signed in.")
        self.user = user
        self.show_commands()

    def log_out(self):
        self.user = None
        print("You logged out.")
        self.initial_commands()

    def quit(self):
        return True

    def view_tweets(self):
        with open(tweets_table.name, "r") as file:
            lines = file.readlines()[1:]
            if len(lines) == 0:
                print("No Tweets!")
                return False
            for tweet in lines:
                print(tweet, end="")
            file.close()
        print('\n')

    def show_commands(self):
        print("What do you wish to do?")
        print("1. Tweet", "2. View Tweets", "3. Like", "4. View Likes Of A Tweet", "5. View My Liked Tweets",
              "6. Retweet A Tweet",
              "7. Reset Password", "8. Log out",
              sep="\n")
        command_number = input()
        self.run_command(command_number)

    def run_command(self, command_number):
        if command_number == "1":
            print("Enter your tweet:")
            tweet_format = tweets_table.fields_properties['text'][-1]
            index = str.index(tweet_format, "(")
            tweet_length = int(tweet_format[index + 1:-1])
            text = input()
            while len(text) > tweet_length or len(text) == 0:
                print("Please enter a text with a length between 0 and {}".format(tweet_length))
                text = input()
            self.user.tweet(text)
            self.show_commands()
        elif command_number == "2":
            print("Do you wish to view (1) your own tweets or (2) all the tweets?")
            view_mode = input()
            if view_mode == "1":
                self.user.view_my_tweets()
            elif view_mode == "2":
                self.view_tweets()
            self.show_commands()
        elif command_number == "3":
            print("Please enter the tweet id: ")
            id = input()
            self.user.like(id)
            self.show_commands()

        elif command_number == "4":
            # View likes
            print("Please enter the tweet id: ")
            id = input()
            print("This tweet is liked by:", end=" ")
            self.user.view_likes(id)
            self.show_commands()
        elif command_number == "5":
            # View my likes
            self.user.view_my_likes()
            self.show_commands()
        elif command_number == "6":
            print("Please enter the tweet id: ")
            id = input()
            self.user.retweet(id)
            self.show_commands()
        elif command_number == "7":
            print("Please enter your current password:")
            current_password = input()
            print("New Password:")
            new_password = input()
            self.user.reset_password(current_password, new_password)
            self.show_commands()
            # Retweet
        elif command_number == "8":
            self.log_out()

        else:
            # Wrong command
            print("Please enter a valid command number.")
            self.show_commands()


class User:
    def __init__(self):
        self.username = None
        self.password = None
        self.phone = None
        self.tweets = []
        self.retweets = []
        self.my_likes = []

    def tweet(self, text):
        tweet_obj = Tweet(text, self.username)
        self.tweets.append(tweet_obj)
        if len(self.tweets) == 1:
            print("Congrats! You twitted your first Tweet!")
        else:
            print("Sent!")

    def like(self, id):
        # Checking if the user has liked this tweet already or not
        liked_by = likes_table.select("$ SELECT FROM likes WHERE tweet_id=={};".format(id))
        if liked_by != "Not Found!":
            for username in liked_by:
                if username.split()[1] == self.username:
                    print("You can't like a tweet twice!")
                    return False
        liked_tweet = tweets_table.select("$ SELECT FROM tweet WHERE tweet_id=={};".format(id))
        if liked_tweet == "Not Found!":
            print("There is no tweet with this id.")
            return False
        likes_table.insert("$ INSERT INTO likes VALUES ({},{});".format(id, self.username))
        self.my_likes.append(liked_tweet)
        print("You liked this tweet: ", liked_tweet)

    def retweet(self, id):
        retweeted_by = retweet_table.select("$ SELECT FROM retweet WHERE tweet_id=={};".format(id))
        if retweeted_by != "Not Found!":
            for username in retweeted_by:
                if username.split()[1] == self.username:
                    print("You can't retweet a tweet twice!")
                    return False
        retweeted_tweet = tweets_table.select("$ SELECT FROM tweet WHERE tweet_id=={};".format(id))
        if retweeted_tweet == "Not Found!":
            print("There is no tweet with this id.")
            return False
        retweet_table.insert("$ INSERT INTO retweet VALUES ({},{});".format(id, self.username))
        self.retweets.append(retweeted_tweet)
        print("You retweeted this tweet:", retweeted_tweet)

    def view_likes(self, tweet_id):
        likes = likes_table.select("$ SELECT FROM likes WHERE tweet_id=={};".format(tweet_id))
        if likes == "Not Found!":
            print("0 likes.")
            return False
        for like in likes:
            print(like.split()[1], end=" ")
        print("\n")

    def view_my_likes(self):
        if len(self.my_likes) == 0:
            print("You haven't liked any tweet yet!")
            return False
        print("These are your liked tweets:")
        for tweet in self.my_likes:
            print(tweet)

    def view_my_tweets(self):
        if len(self.tweets) == 0:
            print("No tweets!")
        for tweet in self.tweets:
            print("id:", tweet.id, ", tweet:", tweet.text, "by", self.username, "at", tweet.date, sep=" ")
        for retweet in self.retweets:
            print("retweeted:", retweet)

    def reset_password(self, current_password, new_password):
        while not self.check_password(current_password):
            print("The current password that you entered is not correct! Try again.")
            print("Current Password:")
            current_password = input()
        password_format = users_table.fields_properties['password'][-1]
        index = str.index(password_format, "(")
        password_length = int(password_format[index + 1:-1])
        while len(new_password) > password_length or len(new_password) == 0:
            print("Please enter a valid password with a length between 0 and {}".format(password_length))
            new_password = input()
        self.password = new_password
        users_table.update(
            "$ UPDATE users WHERE username=={} VALUES ({},{},{});".format(self.username, self.username, self.password,
                                                                          self.phone))
        print("Password Updated!")

    def check_password(self, password):
        if password == self.password:
            return True
        else:
            return False


class Tweet:
    def __init__(self, text, creator, already_in_database=False):
        # Setting the initial values
        self.id = self.generate_id()
        self.creator = creator
        self.text = '({})'.format(text)
        self.date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        # Updating the database
        if not already_in_database:
            self.add_tweet_to_database()

    def add_tweet_to_database(self):
        global tweets_table
        tweets_table.insert(
            "$ INSERT INTO tweets VALUES ({},{},{},{});".format(self.id, self.text, self.creator, self.date))

    def generate_id(self):
        return uuid.uuid4()


def main():
    twitter = Twitter()
    print("End.")
    return 0


main()
