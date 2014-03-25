#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

# import library
from facebook import Facebook


# create user object
# f = Facebook("username/email", "password")

# Aleksandra
# f = Facebook("john.garcia-cvv8ney@yopmail.com", "pbv5FzZuhx")

# Jakub
f = Facebook("janusz.kowalski73@onet.pl")



""" List of available functionality """
# f.isLogged() # return bool 
# f.share('link')
# f.sendMessage('id_of_recipient', 'message')
# f.sendFriendRequests(amount_of_requests_to_send=5)
# f.pokeBack()
# f.cleanTimeline() (while True: f.cleanTimeline())
# f.deleteActivity()