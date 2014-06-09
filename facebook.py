#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

# import libraries
import requests
import time
from BeautifulSoup import BeautifulSoup
import config, json


class Facebook:
    
    """
     Facebook class
        @author: Mateusz Warzyński
        @version: 1.0.0
    """
    
    """ Define variables """
    
    # control variables
    logged = False
    config = None
    session = None
    user = {}
    i = 0 # iteration variable
    headers = {
            "host": "m.facebook.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-encoding": "gzip,deflate,sdch",
            "accept-language": "pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4",
            "cache-control": "max-age=0",
            "content-length": "256",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": "reg_fb_gate=https%3A%2F%2Fwww.facebook.com%2F; datr=fCF9U0svgb81q-QjT57Axku7; m_ts=1400709968; reg_fb_ref=https%3A%2F%2Fm.facebook.com%2F; m_pixel_ratio=1",
            "dnt": "1",
            "origin": "https://m.facebook.com",
            "referer": "https://m.facebook.com/?_rdr",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36"
    }
    
    
    def __init__(self, username='', password=''):
    
        """
         Initialize class functionality, connect to Facebook
          @author: Mateusz Warzyński
          @return: null
        """
    
        # init config library
        self.config = config.pantheraConfig()
        
        if len(username) > 0:
        
            # get some data from json config - getKey(key, defaultValue)
            self.user = self.config.getKey(username, json.loads('{ "username": "'+username+'"}'))
            
            if not self.createSession():            
                self.login(password) # login to Facebook / check if already logged
    
    
    def createSession(self):
        
        """
         Creates requests session
          @author: Mateusz Warzyński
          @return: bool
        """
        
        self.session = requests.session()
        
        try:
            self.user['cookie'] = json.loads(self.user['cookie'])
        except:
            self.user['cookie'] = {}
        
        if self.user['cookie']:
            
            if self.isLogged():
                return True
        
        return False
        
    
    def isLogged(self):
    
        """
         Check if user is logged to Facebook (has active session)
          @author: Mateusz Warzyński
          @return: bool
        """
    
        # get response from home page
        response = self.getContent('https://m.facebook.com', '/home.php')
        
        # if there is option to logout, we must be connected
        if "Logout" in response.content:
            self.logged = True
            return True
        
        self.logged = False
        return False
    
    
    
    def getUserCookie(self):
    
        """
         Return cookie for current session
          @author: Mateusz Warzyński
          @return: string
        """
    
        return self.user['cookie']
    
    
    
    def getUserInfo(self):
    
        """
         Return information about current user in json (username, password, cookie)
          @author: Mateusz Warzyński
          @return: string (json)
        """
    
        return self.user
    
    
    
    def saveUserSession(self):
    
        """
         Save user session to config, in case of future using these account
          @author: Mateusz Warzyński
          @return: null
        """
    
        self.config.setKey(str(self.user['username']), self.getUserInfo())
        self.config.save()
    
    
    
    def login(self, password=''):
        
        """
         Login to Facebook!
          @author: Mateusz Warzyński
          @param: password (string)
          @return: bool
        """
        
        print "Try to login"
        
        # reset not valid variables
        self.user['cookie'] = None
        self.logged = False
        
        # check if password is not empty, otherwise get it from config
        if password is '':
            password = str(self.user['password'])
        
        # login using requests library
        payload = { "locale": "en_US", "non_com_login": "", "email": str(self.user['username']), "pass": password, "lsd": "AVo-YSR3"} # TODO: check lsd code
        
        post = self.session.post('https://login.facebook.com/login.php?login_attempt=1', data=payload, headers=self.headers)
        
        if "Cookies Required" in post.content:
            print "Error with cookies"
        
        # if there is option to logout, we are logged in
        if "Logout" in post.content:
            
            # create string which contains session cookie 
            
            cookie = self.getCookieFromRequestsObject(self.session)
            print cookie
            print post.cookies.items()
            
            # set user session variables
            self.user['password'] = str(password)
            self.user['cookie'] = json.dumps(cookie)
            self.user['id'] = str(self.getID())
            
            # save them to config
            self.saveUserSession()
            
            self.logged = True
            return True
        
        else:
            return False
    
    
    
    def getID(self):
        
        """
         Get user's ID
          @author: Mateusz Warzyński
          @return: string
        """
    
        response = self.getContent("https://m.facebook.com", "/home.php")
        
        try:
            soup = BeautifulSoup(response.content)
            string = soup.prettify()
            user = re.findall('"owner":(.*),"_pmc_":', string)
    
            return user[0]
        
        except:
            return False
        
    
    
    def deleteActivity(self, link=''):
        
        """
         Delete everything what is in activity log (except friends)
          @author: Mateusz Warzyński
          @param: link (string), link to get contents from other period of time
          @return: string
        """
    
        if (link == ''):
            url = "/"+self.user['id']+"/allactivity?refid=17"
            self.done = []
        else:
            url = link
    
        response = self.getContent(url)
    
        try:
            soup = BeautifulSoup(response.content)
        except:
            return False
        
        firstItems = soup.findAll('a', { 'class' : 'sec' })
        
        for item in firstItems:
            
            if ('action=remove_content' in str(item['href'])):
                self.getContent(item['href'])
                print item['href']
            
            if ('action=remove_comment' in str(item['href'])):
                self.getContent(item['href'])
                print item['href']
            
            if ('action=unlike' in str(item['href'])):
                self.getContent(item['href'])
                print item['href']
            
            if ('action=hide' in str(item['href'])):
                self.getContent(item['href'])
                print item['href']
        
        sectionContents = soup.findAll('a')
        
        for section in sectionContents:
            
            try:
            
                if ('&sectionLoadingID=m_timeline_loading_div_' in str(section['href'])):
                    
                    user = re.findall('&sectionID=(.*)', str(section['href']))

                    if str(user[0]) in self.done:
                        continue
                    else:
                        self.done.append(str(user[0]))
                   
                    print section['href']
                    self.deleteActivity(section['href'])
            except:
                print 'error'
    
    
    
    def cleanTimeline(self):
        
        """
         Clean your timeline, delete posts / messages about you
          @author: Mateusz Warzyński
          @return: null
        """
        
        url = "/"+self.user['id']
        response = self.getContent('https://m.facebook.com', url)
        
        try:
            soup = BeautifulSoup(response.content)
        except:
            return False
        
        print soup.prettify()
        
        items = soup.findAll('a')
        
        for item in items:
            print item['href']
            if ('timeline/remove/confirm' in item['href']):
                self.deleteFromTimeline(str(item['href']))
        
    
    
    def deleteFromTimeline(self, link):
        
        """
         Delete posts from timeline
          @author: Mateusz Warzyński
          @return: bool
        """

        domain = "m.facebook.com"
        response = self.getContent('https://m.facebook.com', link)
        
        try:
            soup = BeautifulSoup(response.content)
        except:
            return False
        
        print soup.prettify()
            
        deletes = soup.findAll('a', { 'class' : 'btn btnN' })
        
        for delete in deletes:
        
            print delete['href']
            self.getContent('https://m.facebook.com', delete['href'])
            return True
        
        hides = soup.findAll('a', { 'class' : 'btn btnC' })
        
        for hide in hides:
            
            print hide['href']
            self.getContent('https://m.facebook.com', hide['href'])
            return True
        

    
    def getDTSG(self):
        
        """
         Get fb_dtsg string from share form
          @author: Mateusz Warzyński
          @return: string
        """
    
        # get form to post a new content
        response = self.getContent('/home.php')
        soup = BeautifulSoup(response.content)
        
        # parse html, get token
        token = soup.findAll('input', { "name" : "fb_dtsg" })
        
        return token[0]['value']
    
    
    
    def getContent(self, domain, url):
    
        """
         Get url, return html response!
          @author: Mateusz Warzyński
          @param: url (string) eg. '/home.php'
          @return: string
        """
        
        # create connection to domain+url using httplib library
        try:
            return self.session.get(domain+url, cookies=self.user['cookie'])
        
        except:
            return None
    
    
    
    def checkResponse(self, response=''):
        
        """
         Check if response got via httplib is correct
          @return: True
        """
        
        # TODO: implement checkResponse function (httplib)
        return True
    
    
    
    def requestPOST(self, url, data):
    
        """
         Make a POST request, needed to post content or send message
          @author: Mateusz Warzyński
          @param: url (string) eg. 'http://www.facebook.com/send.php'
          @param: data (string)
          @return: string
        """
    
        postResponse = self.session.post(url, data, headers=self.headers, cookies=self.user['cookie'])
        
        return postResponse.content
    
    
    
    def pokeBack(self, toPoke=[], message=''):
        
        """
         Poke back
          @author: Mateusz Warzyński
          @param: idUser (string), if you want to poke back only specified acquaintance(s)
          @param: message (string), send a message to poked friend back (eg. 'I will win the poke war!')
          @return: bool
        """
    
        import re # we don't need this library every time we are using Facebook class
                    # therefore I imported this here
        
        # check if there are any pokes
        response = self.getContent('https://m.facebook.com', '/pokes')
        
        # parse html code with BeautifulSoup, get pokes as array items
        soup = BeautifulSoup(response.content)
        links = soup.findAll('a', { "class" : "_56bz _56bs _56bu" })
        
        # let's poke our opponents
        for a in range(len(links)):
            
            # check if the button name is valid...
            if links[a].span.contents[0] != 'Poke Back':
                continue
            
            # get url to poke friend back
            url2 = links[a]['href']
            
            # get friend ID
            user = re.findall(r'\&poke_target=(.*?)\&ext=', url2)
            
            print user
            
            # check if our friend is set in array
            if user not in toPoke and len(toPoke) > 0:
                continue
                            
            # check if link is correct
            if str(url2[0:15]) == '/pokes/inline/?':
                # poke!
                self.getContent('https://m.facebook.com', str(url2))
                
                # optionally send message
                if message is not '':
                    self.sendMessage(str(user[0]), message)
        
        return True
    
    
    
    def sendMessage(self, userId, message):
    
        """
         Send message to other user
          @author: Mateusz Warzyński
          @param: userId (string), recipient id
          @param: message (string), content of message
          @return: bool
        """
        
        # check if user has active session
        if self.logged == False:
            return False
        
        # get html code with form to send new messages
        response = self.getContent('https://m.facebook.com', "/messages/compose/?ids="+str(userId))
        soup = BeautifulSoup(response.content)
        
        # parse code, find token
        token = soup.findAll('input', { "name" : "fb_dtsg" })
        
        # create appropiate POST query
        query = {
            "ids["+userId+"]": userId,
            "body": message,
            "Send": "Send",
            "fb_dtsg": str(token[0]['value']),
            "charset_test": "'€,´,€,´,水,Д,Є"
        }
        
        # send message
        response = self.requestPOST('https://m.facebook.com/messages/send/?icm=1', query)
        
        # return bool, depends of what Facebook returned
        if message[0:5] in response:
            return True
        
        return False
    
    
    
    def share(self, message):
    
        """
         Share message on our wall
          @author: Mateusz Warzyński
          @param: message (string), text to post (eg. 'wow, amazing weather!')
          @return: bool
        """
        
        # check if we are logged in
        if self.logged == False:
            return False
        
        # get form to post a new content
        response = self.getContent('https://m.facebook.com', '/home.php')
        soup = BeautifulSoup(response.content)
        
        # parse html, get token
        token = soup.findAll('input', { "name" : "fb_dtsg" })
        privacy = soup.findAll('input', { "name" : "privacy" })
        
        # create POST query
        query = {
            "status": message,
            "fb_dtsg": str(token[0]['value']),
            "charset_test": "'€,´,€,´,水,Д,Є",
            "update": "Share",
            "privacy": str(privacy[0]['value'])            
        }
        
        # post to the wall!
        response = self.requestPOST('https://m.facebook.com/a/home.php', query)
        
        # return bool, depends on what Facebook returned
        if message[0:5] in response.content:
            return True
        
        return False
    
    
    
    def sendFriendRequests(self, amount=15):
    
        """
         Send a friend request to unknown person
          @author: Mateusz Warzyński
          @param: amount of requests to send (integer), eg. 15
          @return: bool
        """
        
        # check if user is logged in
        if self.logged == False:
            return False
        
        # define control variable
        countSentRequests = 0
        
        # loop which sends friend requests
        while countSentRequests < amount:
            
            # get people that I may potentionally know
            response = self.getContent('https://m.facebook.com', "/findfriends/browser/?fb_ref=swp&tid=u_0_0&__ajax__=")
            resp = response.content
            
            # we got list in ajax, parse it using json library
            ajaxData = json.loads(resp[9:])
            
            # search for links which sends friend request (using BeautifulSoup)
            soup = BeautifulSoup(ajaxData['payload']['actions'][0]['html'])
            links = soup.findAll('a', { "class" : "touchable right" })
            
            # if something went wrong, return 0 as count of send requests
            if len(links) == 0:
                return 0
            
            for a in range(len(links)):
                
                # if we send enough request, break the loop
                if countSentRequests >= amount:
                    break
                
                # 10sec pause, we should not send requests too fast (be like human being!)
                time.sleep(10)
                
                # get link to send request
                urlAdd = links[a]['href']
                
                # check if link is valid
                if str(urlAdd[0:36]) != '/a/mobile/friends/add_friend.php?id=':
                    continue
                
                # send request!
                response = self.getContent('https://m.facebook.com', str(urlAdd))
                
                # get reponse, change referer (may help to avoid banning)
                responseBody = response.content
                
                # check if got error, compare with popular messages
                if "Friend requests are for connecting with people you know well" in responseBody:
                    continue
                elif "Already Sent Request" in responseBody:
                    continue
                elif "Please slow down, or you could be blocked from using it." in responseBody:
                    print "Warning about being blocked"
                    return countSentRequests
                elif str(response.status) == '302':
                    countSentRequests = countSentRequests+1
                else:
                    continue
        
        # should be the same amount as param (unless you send too much - avoid great numbers)
        return countSentRequests
    
    
    
    def getCookieFromRequestsObject(self, object):
        
        """
         Return requests cookies as dict
          @author: Mateusz Warzyński
          @param: requests object
          @return: dict
        """
        
        cookies = {}
        
        for k, v in object.cookies.items():
            cookies[k] = v
            
        return cookies
    
    
    def getPosts(self, url, iteration=10):
        
        """
         Get posts from given uid
          @author: Mateusz Warzyński
          @param: string uid, id to page/user
          @return: dict
        """
        
        import string
        
        array = []
        
        response = self.getContent("https://m.facebook.com", str(url))
        
        soup = BeautifulSoup(response.content)
        
        feed = soup.findAll('div', {'class': 'feed'})
        posts = feed[0].findAll('div', {'class': "_55wo"})
        
        for post in posts:
            #print post.prettify()
            dateDiv = post.findAll('div', {'class': 'tlHeaderMetadata'})
            date = dateDiv[0].find('span', {'class': 'mfss'})
            text = post.findAll('span', {'class': 'tlActorText'})
            
            datetime = filter(lambda x: x in string.printable, date.text)
            
            # self.getDateTime(datetime).isoformat(' ')
            
            if len(text):
                a = {}
                a['text'] = text[0].text
                a['date'] = datetime 
                array.append(a)
        
        if self.i == iteration:
            return array
        
        self.i = self.i + 1
        
        aps = feed[0].findAll('div', {'class': 'aps'})
        nextLink = aps[0].a['href']
        
        arrayNext = self.getPosts(str(nextLink))
        array = array + arrayNext
        
        return array
    
    
    
    def getDateTime(self, s):
        
        """
         Change date from "x days/whatever ago" to datetime
          @author: Mateusz Warzyński
          @param: string s, "x days ago"
          @return: datetime
        """
        
        import datetime
        
        print s
        if 'Yesterday' in s:
            s = '1 days ago'

        parsed_s = [s.split()[:2]]
        time_dict = dict((fmt,float(amount)) for amount,fmt in parsed_s)
        dt = datetime.timedelta(**time_dict)
        past_time = datetime.datetime.now() - dt
        
        return past_time