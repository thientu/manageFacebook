import json, os

class pantheraConfig:
    """
        Manage Facebook Config library
            (based on Panthera-Desktop - https://github.com/Panthera-Framework/Panthera-Desktop)
        
        Simple json based key-value storage
        
    """

    memory = {}
    configPath = "config.json"
    configurationChanged = False
    
    def __init__(self):
        self.loadConfig()
    
    def createConfig(self):
        import sys
        
        try:
            w = open(self.configPath, "w")
            w.write("{}")
            w.close()
        except Exception as e:
            print("Cannot create "+self.configPath+"/config.json, please check permissions (details: "+e.strerror+")")
            sys.exit(5)
    
    
    def loadConfig(self):
        """
            Load configuration from JSON file to memory
            
        """
        
        if not os.path.isfile(self.configPath):
            self.createConfig()
    
        t = open(self.configPath, "rb")
        
        try:
            self.memory = json.loads(t.read())
        except Exception as e:
            import sys
            print("Cannot parse configuration file, "+e.strerror)
            sys.exit(5) # errno.EIO = 5
            
        t.close()
        
    
        
    def getKey(self, key, defaultValue=None):
        """
            Get configuration key
        
            key - name
            defaultValue - default value to set if key does not exists yet
        
        """
    
        if not self.memory:
            self.loadConfig();
    
        if key in self.memory:
            return self.memory[key]
            
        # if key does not exists in key-value database yet, create it with default value
        if defaultValue is not None:
            self.setKey(key, defaultValue)

        return defaultValue
            
    """
        Set configuration key
        
        key - name
        value - value
        
    """
            
    def setKey(self, key, value):
        if type(key) is not str:
            return False
    
        self.configurationChanged = True
        self.memory[key] = value
        
    """
        Save configuration right back to json file
        
    """
        
    def save(self):
        if self.configurationChanged:
            w = open(self.configPath, "wb")
            w.write(json.dumps(self.memory))
            w.close()
        
        
    
    
