import discord,re,datetime,requests,os,time,pypandoc
from bs4 import BeautifulSoup

def convert(s):
    result=0
    for c in s:
        result*=10
        result+=int(c,10)
    return result

def filewrite():
    f=open("current.txt","r")
    current=[]
    difficulty=0
    iter=0
    for line in f:
        current.append(line)
    if(len(current)==2):
        difficulty=convert(current[0].rstrip())
        iter=convert(current[1].rstrip())
    f.close()
    f=open("current.txt","w")
    f.write(str((difficulty+1)%4)+"\n")
    f.write(str(iter+1 if(difficulty==3) else iter)+"\n")
    f.close()
    return difficulty,iter

def getQuestion(difficulty,iter):
    file=open('easy'+str(difficulty)+'.txt','r')
    for idx,line in enumerate(file):
        if(idx==iter):
            return 'https://codeforces.com'+line

def getQuestionText(re):
    soup=BeautifulSoup(re.content,'html.parser')
    header=BeautifulSoup(pypandoc.convert_text(soup.findAll('div',{'class':'title'})[0],'gfm',format='html'),features='lxml').text
    statement=BeautifulSoup(pypandoc.convert_text(soup.findAll('div',{'class':'problem-statement'})[0].find_all('div')[10],'gfm',format='html'),features="lxml").text
    statement+='\n'
    inputtext=soup.findAll('div',{'class':'input-specification'})[0].find_all('p')
    input=""
    for line in inputtext:
        input+=pypandoc.convert_text(line,'gfm',format='html') 
    input=BeautifulSoup(input,features="lxml").text
    outputtext=soup.findAll('div',{'class':'output-specification'})[0].find_all('p')
    output=""
    for line in outputtext:
        output+=pypandoc.convert_text(line,'gfm',format='html')
    output=BeautifulSoup(output,features="lxml").text
    statement=statement.replace("$$$","***")
    input=input.replace("$$$","***")
    output=output.replace("$$$","***")
    return "\n**Title**"+header+"**Statement**"+statement+"**Input**\n"+input+"**Output**\n"+output


def get_question(difficulty,iter):
    link=getQuestion(difficulty,iter)
    re=requests.get(link,'html.parser')
    text="**Difficulty**:-"
    if(difficulty==0):
        text+="```css\nVery Easy```"
    elif(difficulty==1):
        text+="```css\nEasy```"
    elif(difficulty==2):
        text+="```fix\nMedium```"
    elif(difficulty==3):
        text+="```diff\n-Hard```"
    text+="\n"
    text+=getQuestionText(re)
    text+='\n'+link
    print(text);
    return text;


client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await send_daily()

    

async def send_daily():
        modifieddate=datetime.datetime.fromtimestamp(float(os.path.getmtime('current.txt'))).date().day
        currentdate=datetime.datetime.now().date().day
        if(currentdate!=modifieddate):
            (difficulty,iter)=filewrite()
            text=get_question(difficulty,iter)
            print(text)
            await client.get_channel(config.channel_key).send(text)
        else:
            print("Done for today")

@client.event
async def on_message(message):
    if(message.content=='!markdown'):
        (difficulty,iter)=filewrite()
        text=get_question(difficulty,iter)
        print(text);
        await message.channel.send(text)
            
client.run(config.client_key)
