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
    message_first_line = message.content.splitlines().pop(0).split()
    first_word = message_first_line.pop( 0 )

    if first_word == "/oracle":
        m = oracle( message , message_first_line )
    elif first_word == "/dice":
        m = dice( message , message_first_line )

    elif first_word == "/timer":
        m = timer_function( message , message_first_line )
        
    if m != "":
        await client.send_message(message.channel, m)


def is_message_self(message):
    return client.user == message.author

def choice_list( list ):
    return list.pop(random.randint( 0 , len(list)-1 ))

def oracle( message , function_param ):
    priority_mode = False
    message_option_lines = message.content.splitlines()
    message_option_lines.pop( 0 )

    if len( function_param ) >= 1 :
        if function_param[0] == "-p":
            priority_mode = True

    
    todo_list = make_todo_list( message_option_lines )
    if len( todo_list ) <= 0 :
        m = "迷ってる事をリストアップして、それぞれの頭に「-」を付けて言ってみてね。"
    elif len( message_option_lines ) == 1 :
        m = "…\n「"+message_option_lines[0]+"」しかやる事ないなら、さっさとやらないと！"
    else :
        m =  "ふむふむ…\nそれじゃあ\n"
        if priority_mode:
            counter = 0
            while( len( todo_list ) ):
                m += str( counter ) + "-" + choice_list( todo_list ) + "\n"
                counter += 1
            m += "の順番でやってみよう！"
        else:
            m += choice_list( todo_list )+"\nをやってみよう！"
    return m

def dice( message , function_param ):
    return_message = "コロコロ…\n「 "
    n = 0
    dice_num = 1
    dice_range = 6
    for n in range( dice_num ):
        return_message += str(random.randint( 1 , dice_range )) + " "

    return_message +="」が出たよ！"
    return return_message

def timer_function( message , param_array ):
    if len(param_array) >= 1:
        if param_array[0] == "stop" :
            return stop_timer( message , param_array )
        else:
            return begin_timer( message , int( param_array[0] ) )
    else:
        return begin_timer( message )

def begin_timer( message , timeout_minute ):
    global timer
    if ( timeout_minute > 0 ):
        return_message = ""+str(timeout_minute)+"分後にお知らせするね！"
    elif ( timeout_minute == 0 ):
        timeout_minute = 30
        return_message = "とりあえず"+timeout_minute+"分後にお知らせするね"
    else:
        return_message = ""+str(timeout_minute)+"分後はもうとっくに過ぎてるよ…"
        
    user = message.author.id
    timer = {message.channel.id : {message.author.id : CallTimer(timeout_minute * 60 ,message.channel,user)}}
    print("タイマー生成"+message.channel.id+" "+message.author.id )

    return return_message

def stop_timer( message , function_param ):
    global timer
    print("タイマー中止"+message.channel.id+" "+message.author.id )
    try:
        timer[message.channel.id][message.author.id].cancel()
        timer[message.channel.id].pop( str(message.author.id) )
        return_message = "タイマーを中止したよ！"
        print('成功')
    except:
        return_message = "あれ？タイマー動かしてた？"
        print("失敗")
    return return_message

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
            #複数行項目フラグが立っている場合は先頭に"-"が付いていなくても項目に含める
            todo_list[ len( todo_list ) - 1 ] += "\n" + todo
    return todo_list


client.run( settings.TOKEN )
