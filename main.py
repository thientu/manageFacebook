#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

# import library
from facebook import Facebook


# create user object
f = Facebook("username/email", "password")


""" List of available functionality """
# f.isLogged() # return bool 
# f.share('link')
# f.sendMessage('id_of_recipient', 'message')
# f.sendFriendRequests(amount_of_requests_to_send=5)
# f.pokeBack()