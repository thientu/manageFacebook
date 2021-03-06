# manageFacebook #

Project allows to manage Facebook account from console. There are several methods you may appreciate.
Code is simulating *human being* to avoid banning.
Python is used, because of its beauty of coding. I did my best to keep everything clear and readable.

-----------------------------------------------

## Login ##

First usage must contain a password as a second argument. If login process will finish successfully, your password will be storaged in *config.json* file.
Next time only username is required.

```python
""" First usage """
f = Facebook("username", "password")

""" Later """
f = Facebook("username")
```

When your session expire, class will renew connection using saved password.

-----------------------------------------------

## Functionality ##

```python
""" Use if you want to be sure, that session is active. """
f.isLogged() # returns bool

""" Share 'I am blissfully happy.' on user's timeline. """ 
f.share('I am blissfully happy.')

""" Send 'What is up?' to Mark Zuckerberg. """
f.sendMessage('4', 'What is up?')

""" Excited about randomness? Meet 5 new people. """
f.sendFriendRequests(amount_of_requests_to_send=5)

""" Poke back id1 and id2 (if emty poke back everyone). Also send them message 'hi'. """
f.pokeBack(toPoke=['id1', 'id2'], message='hi')

""" Delete everything from your timeline """
while True:
    f.cleanTimeline()
    
""" Delete ~90% of your activity """
while True:
    f.deleteActivity()
    
""" Get posts from given site (uid) """
posts = f.getPosts('/uid', iteration=10)
```
