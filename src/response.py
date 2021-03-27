import re
import requests
import json
import time
import json
from urllib.request import urlopen

class ResponseGenerator:    
    def __init__(self, url): 
        self.history={}
        self.url=url
        self.normalize_chars={'Š':'S', 'š':'s', 'Ð':'Dj','Ž':'Z', 'ž':'z', 'À':'A', 'Á':'A', 'Â':'A', 'Ã':'A', 'Ä':'A',
            'Å':'A', 'Æ':'A', 'Ç':'C', 'È':'E', 'É':'E', 'Ê':'E', 'Ë':'E', 'Ì':'I', 'Í':'I', 'Î':'I',
            'Ï':'I', 'Ñ':'N', 'Ń':'N', 'Ò':'O', 'Ó':'O', 'Ô':'O', 'Õ':'O', 'Ö':'O', 'Ø':'O', 'Ù':'U', 'Ú':'U',
            'Û':'U', 'Ü':'U', 'Ý':'Y', 'Þ':'B', 'ß':'Ss','à':'a', 'á':'a', 'â':'a', 'ã':'a', 'ä':'a',
            'å':'a', 'æ':'a', 'ç':'c', 'è':'e', 'é':'e', 'ê':'e', 'ë':'e', 'ì':'i', 'í':'i', 'î':'i',
            'ï':'i', 'ð':'o', 'ñ':'n', 'ń':'n', 'ò':'o', 'ó':'o', 'ô':'o', 'õ':'o', 'ö':'o', 'ø':'o', 'ù':'u',
            'ú':'u', 'û':'u', 'ü':'u', 'ý':'y', 'ý':'y', 'þ':'b', 'ÿ':'y', 'ƒ':'f',
            'ă':'a', 'î':'i', 'â':'a', 'ș':'s', 'ț':'t', 'Ă':'A', 'Î':'I', 'Â':'A', 'Ș':'S', 'Ț':'T',}
        self.alphabets=urlopen("https://raw.githubusercontent.com/JEF1056/clean-discord/master/src/alphabets.txt").read().decode("utf-8").strip().split("\n")
        self.emojis=json.loads(urlopen("https://raw.githubusercontent.com/JEF1056/clean-discord/master/src/emojis.json").read().decode("utf-8"))
        for alphabet in self.alphabets[1:]:
            for ind, char in enumerate(alphabet):
                try:self.normalize_chars[char]=self.alphabets[0][ind]
                except: print(alphabet, len(alphabet), len(self.alphabets[0]));break
        self.normalize_chars.update({i:i for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'})
        
        self.r1=re.compile(r'[\U00003000\U0000205F\U0000202F\U0000200A\U00002000-\U00002009\U00001680\U000000A0\t ]{2,}')
        self.r3=re.compile(r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)|:.+?:|[\w\-\.]+@(?:[\w-]+\.)+[\w-]{2,4}|(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}|```.+?```\n?|(?:\\n)+|(?<=[.,!?()]) (?=[.,!?()])|\b(?:a*ha+h[ha]*|o?l+o+l+[ol]*)\b|(?![:;][3DP])[^a-z0-9.,\'@!?\s\/'+''.join(emojis)+r']+|([a-z])\s([.,\'!?\/])', flags=re.DOTALL | re.IGNORECASE)
        self.r4=re.compile(r"([a-z.])\1{3,}|([,\'@!?\s\/])\2+", re.IGNORECASE)
        
    def register(self, id, timestamp):
        if id in self.history:
            if timestamp-self.history[id]["timestamp"] >= 600:
                self.history[id]={"history":[],"timestamp":timestamp}
            else:
                self.history[id]["timestamp"]=timestamp
        else:
            self.history[id]={"history":[],"timestamp":timestamp}
        return self.history[id]
    
    def reset(self, id):
        self.history[id]={"history":[],"timestamp":time.time()}
        
    def convemojis(self, i):
        if i in self.emojis: return self.emojis[i]
        return i
        
    def clean(self, text, author=False):        
        text=text.translate(self.normal_map)#handle special chars from other langs
        text=re.sub(self.r1, " ", text) #handle... interesting spaces
        text= re.sub(self.r3, r"\2\3", text.strip()) #remove urls, emails, code blocks, custom emojis, non-emoji, punctuation, letters, and phone numbers
        text= re.sub(self.r4, r"\1\1\1\2", text) #handle excessive repeats of punctuation, limited to 3, repeated words, excessive spaces or excessive punctuation, spaces before punctuation but after text
        text= "".join(list(map(self.convemojis,text))) #translate emojis to their `:text:` shorthand form
        text= text.strip().replace("\n","\\n").strip("\t") #handle newlines
            
        if text != "\\n" and text != " " and text != "" and author==None:
            return text
        elif text != "\\n" and text != " " and text != "" and author!=None:
            return " ".join(text.split(" ")[-2:])
        else:
            return None

    def response(self, user, inp, debug=False):
        self.register(user.id, time.time())
        inp= self.clean(user.display_name, author=True)+": "+self.clean(inp)
        inpdata = '{"inputs": ["Input: '+'/b'.join(self.history[user.id]["history"]+[inp])+'"]}'
        response = requests.post(self.url.encode("utf-8"), data=inpdata.encode("utf-8"))
        message = json.loads(response.text)
        if "error" in message or debug: 
            print(f"{message}")
            if "error" in message: return str(message)
        self.history[user.id]["history"].append(inp)
        self.history[user.id]["history"].append("Jade: "+message["outputs"]["outputs"][0])
        self.history[user.id]["history"] = self.history[user.id]["history"][-10:]
        return message["outputs"]["outputs"][0].replace("/n", "\n")