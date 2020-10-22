import praw
import pandas as pd
import rconstants

class RedditClient():
    def __init__(self):
        self.reddit = praw.Reddit(client_id=rconstants.constants['client_id'], client_secret=rconstants.constants['secret_key'], user_agent=rconstants.constants['user_agent'])
        self.client_id = rconstants.constants['client_id']
        self.user_agent = rconstants.constants['user_agent']
        self.posts = {}
    
    def getHot(self, subreddit, limit=10):
        hot_posts = self.reddit.subreddit(subreddit).hot(limit=limit)
        for post in hot_posts:
            print(post.title)
        return hot_posts

        




if __name__ == "__main__":
    client = RedditClient()
    
   