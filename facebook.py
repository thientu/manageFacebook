#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

# import libraries
import urllib2, cookielib
import httplib, time, socket
from BeautifulSoup import BeautifulSoup
import config, json
import re



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
    user = {}
    
    # define cookieJar
    cj = cookielib.CookieJar()
    
    # Headers to execute actions
    headers = dict()
    headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    headers['accept-charset'] = 'ISO-8859-2,utf-8;q=0.7,*;q=0.3'
    headers['accept-language'] = 'en-US,en;q=0.8,pl;q=0.6'
    headers['dnt'] = '1' 
    headers['host'] = 'm.facebook.com' 
    headers['method'] = 'GET'      
    headers['scheme'] = 'https'
    headers['version'] = 'HTTP/1.1'
    headers['user-agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0'
    
    # Headers to login
    h = [('Referer', 'http://login.facebook.com/login.php'),
                    ('Content-Type', 'application/x-www-form-urlencoded'),
                    ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0')]
    
    
    
    
    def __init__(self, username, password=''):
    
        """
         Initialize class functionality, connect to Facebook
          @author: Mateusz Warzyński
          @return: null
        """
    
        # init config library
        self.config = config.pantheraConfig()
        
        # get some data from json config
        self.user = self.config.getKey(username, json.loads('{ "username": "'+username+'"}'))
        
        # login to Facebook / check if already logged
        self.login(password)
    
    
    
    def isLogged(self):
    
        """
         Check if user is logged to Facebook (has active session)
          @author: Mateusz Warzyński
          @return: bool
        """
    
        # get response from home page
        response = self.getContent('m.facebook.com', '/home.php')
        
        # if there is option to logout, we must be connected
        if "Logout" in response.read():
            self.logged = True
            return True

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
        
        # check if last used session is still active
        try:
            if len(self.user['cookie']) > 0:
                self.headers['cookie'] = self.user['cookie']
                self.cj.set_cookie(self.user['cookie'])
                
                if self.isLogged():
                    return True
        except:
            self.user['cookie'] = None
            self.logged = False
        
        # check if password is not empty, otherwise get it from config
        if password is '':
            password = str(self.user['password'])
        
        # create urllib2 instance to estabilish a connection with Facebook server
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        opener.addheaders = self.h
        
        # define variables needed to have succussfull results
        usock = opener.open('http://www.facebook.com')
        usock = opener.open('https://login.facebook.com/login.php?login_attempt=1', "locale=en_US&non_com_login=&email="+str(self.user['username'])+"&pass="+password+"&lsd=20TOl")
        
        # get html code from response
        response = usock.read()
        
        # if there is option to logout, we are logged in
        if "Logout" in response:
            
            # create string which contains session cookie 
            wholeCookie = ''
            for cookie in self.cj:
                wholeCookie =  wholeCookie+cookie.name+"="+cookie.value+"; "
            self.headers['cookie'] = str(wholeCookie)
            
            # set user session variables
            self.user['password'] = str(password)
            self.user['cookie'] = str(wholeCookie)
            self.user['id'] = str(self.getID())
            
            # save them to config
            self.saveUserSession()
            
            self.logged = True
            return True
        
        else:
            return False
    
    
    
    def getID(self):
    
        response = self.getContent('m.facebook.com', "/home.php")
        soup = BeautifulSoup(response.read())
        string = soup.prettify()

        user = re.findall('"owner":(.*),"_pmc_":', string)

        return user[0]
        
    
    
    def deleteActivity(self, link=''):
    
        if (link == ''):
            url = "/"+self.user['id']+"/allactivity?refid=17"
            self.done = []
        else:
            url = link
    
        domain = "m.facebook.com"
        response = self.getContent(domain, url)
    
        try:
            soup = BeautifulSoup(response.read())
        except:
            return False
        
        firstItems = soup.findAll('a', { 'class' : 'sec' })
        
        for item in firstItems:
            
            if ('action=remove_content' in str(item['href'])):
                self.getContent(domain, item['href'])
                print item['href']
            
            if ('action=remove_comment' in str(item['href'])):
                self.getContent(domain, item['href'])
                print item['href']
            
            if ('action=unlike' in str(item['href'])):
                self.getContent(domain, item['href'])
                print item['href']
            
            if ('action=hide' in str(item['href'])):
                self.getContent(domain, item['href'])
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
        domain = "m.facebook.com"
        url = "/janusz.kowalski.73997861"
        response = self.getContent(domain, url)
        
        try:
            soup = BeautifulSoup(response.read())
        except:
            return False
        
        items = soup.findAll('a')
        
        for item in items:
            
            if ('timeline/remove/confirm' in item['href']):
                self.deleteFromTimeline(str(item['href']))
        
    
    
    def deleteFromTimeline(self, link):

        domain = "m.facebook.com"
        response = self.getContent(domain, link)
        
        try:
            soup = BeautifulSoup(response.read())
        except:
            return False
            
        deletes = soup.findAll('a', { 'class' : 'btn btnN' })
        
        for delete in deletes:
        
            print delete['href']
            self.getContent(domain, delete['href'])
            return True
        
        hides = soup.findAll('a', { 'class' : 'btn btnC' })
        
        for hide in hides:
            
            print hide['href']
            self.getContent(domain, hide['href'])
            return True
        

    
    
    def getDTSG(self):
    
        # get form to post a new content
        response = self.getContent('m.facebook.com', '/home.php')
        soup = BeautifulSoup(response.read())
        
        # parse html, get token
        token = soup.findAll('input', { "name" : "fb_dtsg" })
        
        # token[0]['value']
        
        return "AQAlPET1"
    
    
    def getContent(self, domain, url):
    
        """
         Get url, return html response!
          @author: Mateusz Warzyński
          @param: domain (string), eg. 'facebook.com'
          @param: url (string) eg. '/home.php'
          @return: string
        """
        
        # create connection to domain+url using httplib library
        try:
            connection = httplib.HTTPSConnection(domain, 443, timeout=10)
            connection.request("GET", url, headers=self.headers)
            response = connection.getresponse()
            
            # check if response is correct
            if self.checkResponse(response):
                return response
        
        # display error and return empty string
        except (httplib.HTTPException, socket.error) as ex:
            print "Error: %s" % ex
            return ''
    
    
    
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
    
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        opener.addheaders = self.h
        usock = opener.open(str(url), str(data))
        
        return usock.read()
    
    
    
    def pokeBack(self, toPoke=[], message=''):
        
        """
         Poke back
          @author: Mateusz Warzyński
          @param: idUser (string), if you want to poke back only specified acquaintance(s)
          @param: message (string), send a message to poked friend back (eg. 'I will win the poke war!')
          @return: bool
        """
    
        import re # we don't need this library every time we are using Facebook class
                    # therefore I imported it here
        
        # check if there are any pokes
        response = self.getContent('m.facebook.com', '/pokes')
        
        # parse html code with BeautifulSoup, get pokes as array items
        soup = BeautifulSoup(response.read())
        links = soup.findAll('a', { "class" : "touchable _56bz _56bs _56bu" })
        
        # let's poke our opponents
        for a in range(len(links)):
            
            # check if the button name is valid...
            if links[a].span.contents[0] != 'Poke Back':
                continue
            
            # get url to poke friend back
            url2 = links[a]['href']
            
            # get friend ID
            user = re.findall(r'\&poke_target=(.*?)\&ext=', url2)
            
            # check if our friend is set in array
            if user not in toPoke:
                continue
                            
            # check if link is correct
            if str(url2[0:15]) == '/pokes/inline/?':
                # poke!
                self.getContent('m.facebook.com', str(url2))
                
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
        response = self.getContent('m.facebook.com', "/messages/compose/?ids="+str(userId))
        soup = BeautifulSoup(response.read())
        
        # parse code, find token
        token = soup.findAll('input', { "name" : "fb_dtsg" })
        
        # create appropiate POST query
        data = "ids["+userId+"]="+userId+"&body="+message+"&Send=Send&fb_dtsg="+str(token[0]['value'])+"&charset_test='€,´,€,´,水,Д,Є"
        
        # send message
        response = self.requestPOST('https://m.facebook.com/messages/send/?icm=1', data)
        
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
        response = self.getContent('m.facebook.com', '/home.php')
        soup = BeautifulSoup(response.read())
        
        # parse html, get token
        token = soup.findAll('input', { "name" : "fb_dtsg" })
        privacy = soup.findAll('input', { "name" : "privacy" })
        
        # create POST query
        data = "status="+message+"&fb_dtsg="+str(token[0]['value'])+"&charset_test='€,´,€,´,水,Д,Є&update=Share&privacy="+str(privacy[0]['value'])
        
        # post to the wall!
        response = self.requestPOST('https://m.facebook.com/a/home.php', data)
        
        # return bool, depends on what Facebook returned
        if message[0:5] in response:
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
            response = self.getContent('m.facebook.com', "/findfriends/browser/?fb_ref=swp&tid=u_0_0&__ajax__=")
            resp = response.read()
            
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
                response = self.getContent('m.facebook.com', str(urlAdd))
                
                # get reponse, change referer (may help to avoid banning)
                responseBody = response.read()
                self.headers['referer'] = response.getheader('location')
                
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