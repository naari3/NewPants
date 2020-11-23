import config
import time
import asyncio
import datetime
import math
import sys
import os
import random
import json
import subprocess
import pytz
from discord.ext import commands, tasks
import discord
from pathlib import Path
from pykakasi import kakasi

# -----------------------------------------------------------------------------------------
TOKEN = config.AT
tz = config.TZ
client = discord.Client()
kakasi = kakasi()
CHANNEL_ID = int(config.VC_id1)
SOUND_BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
PRE_SOUND_BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/pre/'
POST_SOUND_BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
# -----------------------------------------------------------------------------------------

tokyo_timezone = pytz.timezone('Asia/Tokyo')

bot = commands.Bot(command_prefix='_')
# print(dir(bot))

@bot.event
async def on_ready():
    global channel,now,dice,M_dice,D_dice,N_dice
    
    channel = bot.get_channel(CHANNEL_ID)
    now = datetime.datetime.now(pytz.timezone(tz)).strftime('%H:%M:%S')
    dice = random.randint(0, 9)
    M_dice = random.randint(1,7)
    D_dice = random.randint(8, 11)
    N_dice = random.randint(12, 15)

    print('--------------------')
    print('ログインしました')
    print(bot.user.name)
    print(bot.user.id)
    print(discord.__version__)
    print('起動時刻')
    print(config.TZ)
    print(now)
    print(dice)
    print('--------------------')
    await bot.change_presence(activity=discord.Game(tz))

@bot.command()
async def boin(ctx, *arg):
    #漢字・ひらがなをカタカナに変換
    arg = str(arg)
    mojiretsu = arg.translate(str.maketrans({"(":"", "'":"", ",":"" ,")":""}))
    kakasi.setMode('J', 'K') 
    kakasi.setMode("H", "K") 
    conv = kakasi.getConverter()
    katakana = conv.do(mojiretsu)
    text = katakana
    #大文字とゥの変換リスト
    large_tone = {
        'ア' :'ア', 'イ' :'イ', 'ウ' :'ウ', 'エ' :'エ', 'オ' :'オ',
        'ヴ': 'ウ',
        'カ' :'ア', 'キ' :'イ', 'ク' :'ウ', 'ケ' :'エ', 'コ' :'オ',
        'サ' :'ア', 'シ' :'イ', 'ス' :'ウ', 'セ' :'エ', 'ソ' :'オ',
        'タ' :'ア', 'チ' :'イ', 'ツ' :'ウ', 'テ' :'エ', 'ト' :'オ',
        'ナ' :'ア', 'ニ' :'イ', 'ヌ' :'ウ', 'ネ' :'エ', 'ノ' :'オ',
        'ハ' :'ア', 'ヒ' :'イ', 'フ' :'ウ', 'ヘ' :'エ', 'ホ' :'オ',
        'マ' :'ア', 'ミ' :'イ', 'ム' :'ウ', 'メ' :'エ', 'モ' :'オ',
        'ヤ' :'ア', 'ユ' :'ウ', 'ヨ' :'オ',
        'ラ' :'ア', 'リ' :'イ', 'ル' :'ウ', 'レ' :'エ', 'ロ' :'オ',
        'ワ' :'ア', 'ヲ' :'オ', 'ン' :'ン',
        'ガ' :'ア', 'ギ' :'イ', 'グ' :'ウ', 'ゲ' :'エ', 'ゴ' :'オ',
        'ザ' :'ア', 'ジ' :'イ', 'ズ' :'ウ', 'ゼ' :'エ', 'ゾ' :'オ',
        'ダ' :'ア', 'ヂ' :'イ', 'ヅ' :'ウ', 'デ' :'エ', 'ド' :'オ',
        'バ' :'ア', 'ビ' :'イ', 'ブ' :'ウ', 'ベ' :'エ', 'ボ' :'オ',
        'パ' :'ア', 'ピ' :'イ', 'プ' :'ウ', 'ペ' :'エ', 'ポ' :'オ'
    }

    # 大文字を母音に変換
    text = list(text)
    for i, v in enumerate(text):
        if v in large_tone:
            text[i] = large_tone[v]
    text = ''.join(text)

    #残った小文字を母音に変換
    for k,v in zip('ヮャュョ','ァァゥォ'):
        text = text.replace(k,v)

    await ctx.send(text)

@bot.command()
async def nowtime(ctx):
    await ctx.send(now)

@bot.command()
async def timezone(ctx):
    await ctx.send(tz)

@bot.command()
async def list_timezone(ctx):
    timeZoneList = pytz.common_timezones
    timeZoneListJoined = '\n'.join(timeZoneList)

    discordTextMaxLength = 1950
    if len(timeZoneListJoined) <= discordTextMaxLength :
        #2000以下
        await ctx.send(f'```{timeZoneList}```')
    else :
        partMessageBody = ""
        partMessageNum = 1

        for line in timeZoneList :
            if len(partMessageBody) + len(line) >= discordTextMaxLength :
                await ctx.send(f'```{partMessageBody}```')
                partMessageBody = ""
                partMessageNum += 1
            partMessageBody += line + '\n'

        await ctx.send(f'```{partMessageBody}```')

@bot.command()
async def set_timezone(ctx, new_timezone: str):
    if new_timezone in pytz.common_timezones:
        global tz, now
        tz = new_timezone
        now = datetime.datetime.now(pytz.timezone(tz)).strftime('%H:%M:%S')
        await ctx.send('新しいタイムゾーンを' + tz + 'にセットしました')
        await bot.change_presence(activity=discord.Game(tz))
    else:
        await ctx.send("そんなもの存在しませ〜んw")


@bot.command()
async def set_dice(ctx,*args):
    global dice
    if len(args) == 0:
        dice = random.randint(0,9)
    else:
        try:
            dice = int(args[0])
        except:
            await ctx.send('数字を入力してね')
            return
    await ctx.send(dice)

@bot.command()
async def ping(ctx):
    await ctx.send('PONG {0}'.format(
        tokyo_timezone.localize(
            (ctx.message.created_at + datetime.timedelta(hours=9))
        ).strftime('%Y-%m-%d %H:%M:%S.%f')
    ))

@bot.command()
async def toggle_channel(ctx):
    global CHANNEL_ID,channel
    if CHANNEL_ID == 610568928233521152:
        CHANNEL_ID = 618082304484442123
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 618082304484442123:
        CHANNEL_ID = 769665765283463208
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 769665765283463208:
        CHANNEL_ID = 610569245025239080
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 610569245025239080:
        CHANNEL_ID = 610568928233521152
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')

@bot.command()
async def now_channel(ctx):
    global channel
    await ctx.send(channel.name + 'です。')

@bot.command()
async def SV(ctx):
    await discord.VoiceChannel.connect(channel)

@bot.command()
async def test_join(ctx, *args):
    global M_dice,D_dice,N_dice
    now_datetime = datetime.datetime.now(pytz.timezone(tz)).strftime('%H:%M:%S')
    split_time = now_datetime.split(':')
    if '05' <= split_time[0] <= '10':
        pre_filepath = PRE_SOUND_BASE_PATH + '{}.wav'.format(M_dice)
        post_filepath = POST_SOUND_BASE_PATH + '{}.wav'.format(split_time[0])
        M_dice = random.randint(1,7)
    elif '11' <= split_time[0] <= '17':
        pre_filepath = PRE_SOUND_BASE_PATH + '{}.wav'.format(D_dice)
        post_filepath = POST_SOUND_BASE_PATH + '{}.wav'.format(split_time[0])
        D_dice = random.randint(8, 11)
    elif '18' <= split_time[0] <= '24' or '01' <= split_time[0] <= '04' :
        pre_filepath = PRE_SOUND_BASE_PATH + '{}.wav'.format(N_dice)
        post_filepath = POST_SOUND_BASE_PATH + '{}.wav'.format(split_time[0])
        N_dice = random.randint(12, 15)

    await play_audio(pre_filepath,post_filepath)

async def play_audio(pre_filepath,post_filepath):
    audio1 = discord.FFmpegPCMAudio(pre_filepath)
    audio2 = discord.FFmpegPCMAudio(post_filepath)
    voice = await discord.VoiceChannel.connect(channel)
    voice.play(audio1)

    while voice.is_playing():
        await asyncio.sleep(1)
    
    audio1.cleanup()
    voice.play(audio2)
    
    while voice.is_playing():
        await asyncio.sleep(1)

    audio2.cleanup()
    await voice.disconnect()

    return


@tasks.loop(seconds=1)
async def loop():
    global M_dice,D_dice,N_dice
    now_datetime = datetime.datetime.now(pytz.timezone(tz)).strftime('%H:%M:%S')
    split_time = now_datetime.split(':')
    if split_time[1] == '00' and split_time[2] == '00':
        if '05' <= split_time[0] <= '10':
            pre_filepath = PRE_SOUND_BASE_PATH + '{}.wav'.format(M_dice)
            post_filepath = POST_SOUND_BASE_PATH + '{}.wav'.format(split_time[0])
            M_dice = random.randint(1,7)
        elif '11' <= split_time[0] <= '17':
            pre_filepath = PRE_SOUND_BASE_PATH + '{}.wav'.format(D_dice)
            post_filepath = POST_SOUND_BASE_PATH + '{}.wav'.format(split_time[0])
            D_dice = random.randint(8, 11)
        elif '18' <= split_time[0] <= '24' or '01' <= split_time[0] <= '04' :
            pre_filepath = PRE_SOUND_BASE_PATH + '{}.wav'.format(N_dice)
            post_filepath = POST_SOUND_BASE_PATH + '{}.wav'.format(split_time[0])
            N_dice = random.randint(12, 15)
        await play_audio(pre_filepath,post_filepath)

@bot.event
async def on_message(message):
    if message.content.startswith('PONG ') and message.author.id == bot.user.id:
        time_now = message.content.replace('PONG ', '')
        ping_time = tokyo_timezone.localize(
            datetime.datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S.%f'))
        post_time = tokyo_timezone.localize(message.created_at +
                                            datetime.timedelta(hours=9))
        diff_time = post_time - ping_time
        await message.edit(content='PONG({0}ms)'.format((diff_time.seconds * 1000) + int(str(diff_time.microseconds)[:3])))
    # on_messageをつかうと裏で暗黙に動いていたprocess_commandが上書きされてしまうので、明示的にprocess_commandsを呼ぶ
    # https://github.com/Rapptz/discord.py/blob/v1.2.5/discord/ext/commands/bot.py#L900-L901
    await bot.process_commands(message)

# MyBotのインスタンス化及び起動処理。
if __name__ == '__main__':
    loop.start()
    bot.run(TOKEN)  # Botのトークン
    
