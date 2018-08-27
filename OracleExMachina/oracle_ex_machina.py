import random
import threading
import discord
import asyncio
import settings

client = discord.Client()
timer = {}


class CallTimer:
    def __init__(self, timeLength,channel,user):
        self.timeLength = timeLength
        self.task = asyncio.ensure_future(self.timer())
        self.channel = channel
        self.user = user
        
    async def timer( self ):
        await asyncio.sleep(self.timeLength)
        await client.send_message(self.channel, "<@!"+self.user+"> 時間だよ！")
        print('タイマー完了'+str(self.channel)+" "+str(self.user) )
   
    def cancel(self):
        self.task.cancel()

@client.event
async def on_ready():
    print('ready...')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    
    #botは無視する
    if is_message_self(message):
        return

    m = ""
    message_split_lines = message.content.splitlines()
    if message_split_lines[0].startswith("/oracle"):
        if len( message_split_lines ) <= 1 :
            m = "迷ってる事をリストアップして、それぞれの頭に「-」を付けて言ってみてね。"
        elif len(message_split_lines ) == 2 :
            m = "…\n「"+message_split_lines[1]+"」しかやる事ないなら、さっさとやらないと！"
        else :
            message_split_lines.pop( 0 )
            todo_list = make_todo_list(message_split_lines )
            m =  "ふむふむ…"
            m += "じゃあ\n"+choice_list( todo_list )+"\nをやってみよう！"
    elif message_split_lines[0].startswith("/dice"):
        m = "コロコロ…\n「"+str(random.randint( 1 , 6 ))+"」が出たよ"
    elif message_split_lines[0].startswith("/timer"):
        words = message_split_lines[0].split(" ")
        global timer
        timer_timeout = -1

        if len(words) >= 2:
            if ( words[1] == "stop") :
                print("タイマー中止"+message.channel.id+" "+message.author.id )
                try:
                    timer[message.channel.id][message.author.id].cancel()
                    timer[message.channel.id].pop( str(message.author.id) )
                    m = "タイマーを中止したよ！"
                    print('成功')
                except:
                    m = "あれ？タイマー動かしてた？"
                    print("失敗")
            else:
                timer_timeout = int( words[1] )
                if ( timer_timeout > 0 ):
                    m = ""+str(timer_timeout)+"分後にお知らせするね！"
                elif ( timer_timeout == 0 ):
                    timer_timeout = 30
                    m = "よく分からないから"+timer_timeout+"分後にお知らせするね"
                else:
                    m = ""+str(timer_timeout)+"分後はもうとっくに過ぎてるよ…"
        else:
            timer_timeout = 30
            m = "とりあえず、"+str(timer_timeout)+"分後にお知らせするね！"

        if timer_timeout > 0:
            user = message.author.id
            timer = {message.channel.id : {message.author.id : CallTimer(timer_timeout * 60 ,message.channel,user)}}
            print("タイマー生成"+message.channel.id+" "+message.author.id )
	if m != "":
		await client.send_message(message.channel, m)


def is_message_self(message):
    return client.user == message.author

def choice_list( list ):
    return list[random.randint( 0 , len(list)-1 )]

def make_todo_list( arg_string_list ):
    is_neibour_todo = False
    todo_list = []
    for todo in arg_string_list:
        if todo == "":
            is_neibour_todo = False
            continue
        elif todo.startswith("-"):
            todo_list.append( todo )
            is_neibour_todo = True
        elif is_neibour_todo:
            todo_list[ len( todo_list ) - 1 ] += "\n" + todo
    return todo_list


client.run( settings.TOKEN )
