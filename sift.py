
#outputfile = f.open('output.txt', 'w')
import pandas
import io
import random, re
from tqdm import tqdm



outputfile = io.open('output.txt', 'w')
messageArray = []

csv_file = pandas.read_csv('counselchat-data.csv')


for index in tqdm(csv_file.index):
    cleaned_string = (str(csv_file['questionText'][index]) + "\t" + str(csv_file['answerText'][index]))
    messageArray.append(cleaned_string)
    
r8=re.compile(r"([\s!?@\"\'])\1+")

random.shuffle(messageArray)
for i in tqdm(range(len(messageArray)), desc="Writing"):
    newString = messageArray[i].replace("\n"," ")
    newerString = re.sub(r8, r"\1", newString)
    outputfile.write(newerString + '\n')



git add .
git commit -m "Put whatever you want in your commit message here"
git push