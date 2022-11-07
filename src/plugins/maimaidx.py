from collections import defaultdict
from tkinter import Image

from nonebot import on_command, on_message, on_notice, require, get_driver, on_regex
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from nonebot.adapters.cqhttp import Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from src.plugins.guild import GuildMessageEvent

from src.libraries.tool import hash
from src.libraries.maimaidx_music import *
from src.libraries.image import *
from src.libraries.maimai_best_40 import *

from src.libraries.maimai_plate import *

import re
import datetime
import time
import math
from io import BytesIO
import os
from src.libraries.maimaidx_guess import GuessObject
from nonebot.permission import Permission
from nonebot.log import logger
import requests
import json
import random
from urllib import parse
import asyncio
from nonebot.rule import to_me
from src.libraries.config import Config
from PIL import Image, ImageDraw, ImageFont, ImageFilter

driver = get_driver()

@driver.on_startup
def _():
    logger.info("Kiba Kernel -> Load \"DX\" successfully")

help_mai = on_command('maimai.help')

@help_mai.handle()
async def _(bot: Bot, event: Event, state: T_State):
    help_str = '''▼ 舞萌模块可用命令 | Commands For Maimai                                               
------------------------------------------------------------------------------------------------------------------------------
今日舞萌/今日运势                                                               查看今天的舞萌运势

XXXmaimaiXXX什么                                                           随机一首歌

随个[dx/标准][绿黄红紫白]<难度>                                      随机一首指定条件的乐曲

随<数量>个[dx/标准][绿黄红紫白]<难度1>                       随机指定首指定条件的乐曲（不超过4个）
[至]<难度2>                                                                        可以设置两个难度，会从其中随机歌曲

查歌<乐曲标题的一部分>                                                    查询符合条件的乐曲

[绿黄红紫白]id<歌曲编号>                                                  查询乐曲信息或谱面信息

<歌曲别名>是什么歌                                                            查询乐曲别名对应的乐曲

定数查歌 <定数下限> <定数上限>                                      查询定数对应的乐曲

分数线 <难度+歌曲id> <分数线>                                       详情请输入“分数线 帮助”查看

jrrp/人品值                                                                           查看今天的人品值。

今日性癖/jrxp                                                                       看看你今天性什么东西捏？

猜歌                                                                                       开始一轮猜歌                                                         

b40 / b50                                                                              根据查分器数据生成你的 Best 40 /Best 50。

[@我]<出勤店铺><人数/几>人                                             设置或者显示当前店铺的出勤人数

[@我]<出勤店铺>位置                                                           显示店铺的位置

段位模式 <Expert/Master> <初级/中级/上级/超上级>        模拟Splash Plus的随机段位模式。
                                                                                            详情请输入“段位模式 帮助”查看


<牌子名>进度                                                                     查询您的查分器，获取对应牌子的完成度。

                                                                                             查询您的查分器，获取对应等级的完成度。
<等级><Rank/Sync/Combo状态>进度                             * Rank: S/S+/SS/SS+/SSS/SSS+等
                                                                                             Sync: FS/FS+/FDX/FDX+ Combo: FC/FC+/AP/AP+

我要在<等级>上<分值>分                                                   犽的锦囊 - 快速推荐上分歌曲。

查看排名/查看排行                                                               查看查分器网站 Rating 的 TOP50 排行榜！

底分分析/rating分析 <用户名>                                           Best 40 的底分分析

/kiba 早 
/kiba [上午/中午/晚上]好                                                             进行一波签到，然后可以得到今天的运势歌曲。                                          
签到

setplate                                                                                        更改在您自主查询B40/B50时在姓名框显示的牌子。
------------------------------------------------------------------------------------------------------------------------------

▼ 管理员设置 | Administrative                                             
------------------------------------------------------------------------------------------------------------------------------
店铺设置 <店铺名> <店铺位置（可选）>

猜歌设置 <启用/禁用>
------------------------------------------------------------------------------------------------------------------------------'''
    await help_mai.send(Message([{
        "type": "image",
        "data": {
            "file": f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}"
        }
    }]))

def song_txt(music: Music):
    try:
        fileimage = f"https://www.diving-fish.com/covers/{get_cover_len4_id(music.id)}.jpg"
        imagedata = Image.open(BytesIO(fileimage.content)).convert('RGBA')
        sentimagedata = f"base64://{str(image_to_base64(imagedata), encoding='utf-8')}"
    except:
        try:
            fileimage = f"https://www.diving-fish.com/covers/{get_cover_len4_id(music.id)}.png"
            imagedata = Image.open(BytesIO(fileimage.content)).convert('RGBA')
            sentimagedata = f"base64://{str(image_to_base64(imagedata), encoding='utf-8')}"
        except:
            try:
                fileimage = Image.open(os.path.join('src/static/mai/cover/', f"{music['id']}.jpg"))
                sentimagedata = f"base64://{str(image_to_base64(fileimage), encoding='utf-8')}"
            except:
                try:
                    fileimage = Image.open(os.path.join('src/static/mai/cover/', f"{music['id']}.png"))
                    sentimagedata = f"base64://{str(image_to_base64(fileimage), encoding='utf-8')}"
                except:
                    fileimage = Image.open(os.path.join('src/static/mai/pic/', f"noimage.png"))
                    sentimagedata = f"base64://{str(image_to_base64(fileimage), encoding='utf-8')}"
    return Message([
        {
            "type": "image",
            "data": {
                "file":  sentimagedata
            }
        },
        {
            "type": "text",
            "data": {
                "text": f"♪{music.type} - {music.id}\n"
            }
        },
        {
            "type": "text",
            "data": {
                "text": f"{music.title}"
            }
        },
        {
            "type": "text",
            "data": {
                "text": f"\n分类: {music.genre}\n等级: {' ▸ '.join(music.level)}"
            }
        }
    ])


def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key = lambda i: int(i['id'])):
        for i in music.diff:
            result_set.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


inner_level = on_command('inner_level ', aliases={'定数查歌 '})


@inner_level.handle()
async def _(bot: Bot, event: Event, state: T_State):
    argv = str(event.get_message()).strip().split(" ")
    nickname = event.sender.nickname
    if len(argv) > 2 or len(argv) == 0:
        await inner_level.finish("命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
        return
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
        s = f"▾ [Sender: {nickname}]\n Search Result | 查歌 定数: {float(argv[0])}"
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
        s = f"▾ [Sender: {nickname}]\n Search Result | 查歌 定数: {float(argv[0])} - {float(argv[1])}"
    if len(result_set) > 50:
        await inner_level.finish(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
        return
    resultnum = 0
    for elem in result_set:
        resultnum += 1
        s += f"\nNo: {resultnum} | ID {elem[0]} >\n{elem[1]} {elem[3]} {elem[4]}({elem[2]})"
    await inner_level.finish(s.strip())


pandora_list = ['我觉得您打白潘不如先去打一下白茄子。', '别潘了，别潘了，滴蜡熊快被潘跑了。', '没有精神！！转圈掉的那么多还想打15!!', '在您玩白潘之前，请您先想一下：截止2021/9，国内SSS+ 4人，SSS 18人，SS 69人。这和您有关吗？不，一点关系都没有。', '潘你🐎', '机厅老板笑着管你收砸坏键子的损失费。', '潘小鬼是吧？', '你不许潘了！']
spec_rand = on_regex(r"^随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?")


@spec_rand.handle()
async def _(bot: Bot, event: Event, state: T_State):
    nickname = event.sender.nickname
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(event.get_message()).lower())
    try:
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        if res.groups()[1] == "":
            music_data = total_list.filter(level=level, type=tp)
        else:
            music_data = total_list.filter(level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
        if len(music_data) == 0:
            rand_result = f'{nickname}，最低是1，最高是15，您这整了个{level}......故意找茬的吧？'
        else:
            rand_result = f'▾ [Sender: {nickname}]\n  Rand Track | 随机歌曲\n' + song_txt(music_data.random())
            if level == '15':
                rand_result += "\n\nPandora:\n" + pandora_list[random.randint(0,7)]
        await spec_rand.send(rand_result)
    except Exception as e:
        print(e)
        await spec_rand.finish(f"▿ Bug Check\n随机命令出现了问题。\n[Exception Occurred]\n{e}")
        
mr = on_regex(r".*maimai.*什么")


@mr.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await mr.finish(song_txt(total_list.random()))


spec_rand_multi = on_regex(r"^随([1-9]\d*)首(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?[至]?([0-9]+\+?)?")

@spec_rand_multi.handle()
async def _(bot: Bot, event: Event, state: T_State):
    nickname = event.sender.nickname
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随([1-9]\d*)首((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)([至]?)([0-9]+\+?)?"   
    res = re.match(regex, str(event.get_message()).lower())
    cf_list = [f'国行DX最多就四首，所以我们不能随{res.groups()[0]}首。', f'如果你真的想打{res.groups()[0]}首歌还不喘气的话，你应该去霓虹打超新超热去，这最多就4首，你要不要吧！╰(艹皿艹 )', f'这个指令不能对日本玩家服务....这里只能支持四首，{res.groups()[0]}首真的太多了。']
    try:
        if int(res.groups()[0]) > 4:
            rand_result = cf_list[random.randint(0,2)]
            await spec_rand_multi.send(rand_result)
        else:
            if res.groups()[3] == '15' and res.groups()[4] is None:
                rand_result = f'▿ [Sender: {nickname}]\n  Rand Tracks Error | Lv 15\nWDNMD....{res.groups()[0]}首白潘是吧？\n(╯‵□′)╯︵┻━┻\n 自己查 834 去！！'
                await spec_rand_multi.send(rand_result)
            else:
                rand_result = f'▾ [Sender: {nickname}]\n  Multi Rand Tracks | 多曲随机\n'
                for i in range(int(res.groups()[0])):
                    if res.groups()[1] == "dx":
                        tp = ["DX"]
                    elif res.groups()[1] == "sd" or res.groups()[0] == "标准":
                        tp = ["SD"]
                    else:
                        tp = ["SD", "DX"]
                    if res.groups()[4] is not None:
                        level = [res.groups()[3], res.groups()[5]]
                    else:
                        level = res.groups()[3]
                    if res.groups()[2] == "":
                        music_data = total_list.filter(level=level, type=tp)
                    else:
                        music_data = total_list.filter(level=level, diff=['绿黄红紫白'.index(res.groups()[2])], type=tp)
                    if len(music_data) == 0:
                        rand_result = f'▿ [Sender: {nickname}]\n  Rand Tracks Error | Lv Error\n{nickname}，最低是1，最高是15，您这整了个{level}......故意找茬的吧？\n <(* ￣︿￣)'
                    else:
                        rand_result += f'\n----- Track {i + 1} / {res.groups()[0]} -----\n' + song_txt(music_data.random())
                await spec_rand_multi.send(rand_result)
    except Exception as e:
        print(e)
        await spec_rand_multi.finish(f"▿ Bug Check\n多歌曲随机命令出现了问题。\n[Exception Occurred]\n{e}")


search_music = on_regex(r"^查歌.+")


@search_music.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await search_music.send("▿ 无匹配乐曲\n没有找到这样的乐曲。")
    elif len(res) < 50:
        search_result = "▾ 搜索结果"
        resultnum = 0
        for music in sorted(res, key = lambda i: int(i['id'])):
            resultnum += 1
            search_result += f"\nNo: {resultnum} | ♪ {music['id']} >\n{music['title']}"
        await search_music.finish(Message([
            {"type": "text",
                "data": {
                    "text": search_result.strip()
                }}]))
    else:
        await search_music.send(f"▿ 搜索结果过多\n结果太多啦...一共我查到{len(res)} 条符合条件的歌!\n缩小一下查询范围吧。")


query_chart = on_regex(r"^([绿黄红紫白]?)id([0-9]+)")

def getCharWidth(o) -> int:
        widths = [
            (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
            (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
            (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
            (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
            (120831, 1), (262141, 2), (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1
def coloumWidth(s: str):
    res = 0
    for ch in s:
        res += getCharWidth(ord(ch))
    return res
def changeColumnWidth(s: str, len: int) -> str:
     res = 0
     sList = []
     for ch in s:
         res += getCharWidth(ord(ch))
         if res <= len:
            sList.append(ch)
     return ''.join(sList)

@query_chart.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "([绿黄红紫白]?)id([0-9]+)"
    groups = re.match(regex, str(event.get_message())).groups()
    nickname = event.sender.nickname
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re:Master']
            name = groups[1]
            music = total_list.by_id(name)
            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            stats = music['stats'][level_index]
            pic_dir = 'src/static/mai/pic/'         
            baseimage =  Image.open(os.path.join(pic_dir, f'levelid.png')).convert('RGBA')
            if level_index == 0:
                pic= 'BSC'
            elif level_index == 1:
                pic = 'ADV'
            elif level_index == 2:
                pic = 'EXP'
            elif level_index == 3:
                pic = 'MST'
            else:
                pic = 'MST_Re'
            image = Image.open(os.path.join(pic_dir, f'1{pic}.png')).convert('RGBA')
            image = image.resize((int(image.size[0] * 1), int(image.size[1] * 1)))
            try:
                tag = stats['tag']
            except:
                tag = "Insufficient Difficulty Data"
            try:
                file = requests.get(f"https://www.diving-fish.com/covers/{music['id']}.jpg")
                imagedata = Image.open(BytesIO(file.content)).convert('RGBA')
                imagedata = imagedata.resize((int(600), int(600)))
            except:
                try:
                    pic_cover = 'src/static/mai/cover/'
                    try:
                        imagedata = Image.open(os.path.join(pic_cover, f"{music['id']}.jpg")).convert('RGBA')
                    except:
                        imagedata = Image.open(os.path.join(pic_cover, f"{music['id']}.png")).convert('RGBA')
                    imagedata = imagedata.resize((int(600), int(600)))
                except:
                    imagedata = Image.open(os.path.join(pic_dir, f'noimage.png')).convert('RGBA')
            if pic == 'MST_Re':
                imagedata.paste(image, (8,8), mask=image.split()[3])
            else:
                imagedata.paste(image, (5,8), mask=image.split()[3])
            baseimage.paste(imagedata, (0,0), mask=imagedata.split()[3])
            font = ImageFont.truetype('src/static/HOS.ttf', 19, encoding='utf-8')
            fontBold = ImageFont.truetype('src/static/HOS_Med.ttf', 13, encoding='utf-8')
            fontBoldL = ImageFont.truetype('src/static/HOS_Med.ttf', 28, encoding='utf-8')
            fontLV = ImageFont.truetype('src/static/HOS.ttf', 36, encoding='utf-8')
            fontBoldLV = ImageFont.truetype('src/static/HOS_Med.ttf', 12, encoding='utf-8')
            imageDraw = ImageDraw.Draw(baseimage);
            if len(chart['notes']) == 4:
                imagestandard = Image.open(os.path.join(pic_dir, f'UI_UPE_Infoicon_StandardMode.png')).convert('RGBA')
                imagestandard = imagestandard.resize((int(imagestandard.size[0] * 0.8), int(imagestandard.size[1] * 0.8)))
                baseimage.paste(imagestandard, (480,26), mask=imagestandard.split()[3])
                imageDraw.text((63, 630), f'{music["id"]}', 'white', fontBold)
                if coloumWidth(music["title"]) > 30:
                    title = changeColumnWidth(music["title"], 20) + '...'
                    imageDraw.text((33, 680), title, 'black', fontBoldL)
                else:
                    imageDraw.text((33, 680), f'{music["title"]}', 'black', fontBoldL)
                if str(level).rfind("+") == -1:
                    imageDraw.text((513, 635), f'{level}', 'white', fontLV)
                else:
                    imageDraw.text((505, 635), f'{level}', 'white', fontLV)
                imageDraw.text((523, 690), f'{ds}', (0, 162, 232), fontBoldLV)
                imageDraw.text((37, 725), f'{music["basic_info"]["artist"]}', 'black', font)
                imageDraw.text((35, 831), f'{tag}', 'black', font)
                imageDraw.text((35, 930), f'{chart["charter"]}', 'black', font)
                tap = chart['notes'][0]
                hold = chart['notes'][1]
                slide = chart['notes'][2]
                breaknote = chart['notes'][3]
                imageDraw.text((68, 1092), f'{tap}', 'white', fontLV)
                imageDraw.text((236, 1092), f'{slide}', 'white', fontLV)
                imageDraw.text((433, 1092), f'--', 'white', fontLV)
                imageDraw.text((68, 1215), f'{hold}', 'white', fontLV)
                imageDraw.text((236, 1215), f'{breaknote}', 'white', fontLV)
                imageDraw.text((433, 1215), f'{tap + slide + hold + breaknote}', 'white', fontLV)
            else:
                imagedx = Image.open(os.path.join(pic_dir, f'UI_UPE_Infoicon_DeluxeMode.png')).convert('RGBA')
                imagedx = imagedx.resize((int(imagedx.size[0] * 0.8), int(imagedx.size[1] * 0.8)))
                baseimage.paste(imagedx, (480,26), mask=imagedx.split()[3])
                imageDraw.text((63, 630), f'{music["id"]}', 'white', fontBold)
                if coloumWidth(music["title"]) > 30:
                    title = changeColumnWidth(music["title"], 20) + '...'
                    imageDraw.text((33, 680), title, 'black', fontBoldL)
                else:
                    imageDraw.text((33, 680), f'{music["title"]}', 'black', fontBoldL)
                if str(level).rfind("+") == -1:
                    imageDraw.text((513, 635), f'{level}', 'white', fontLV)
                else:
                    imageDraw.text((501, 635), f'{level}', 'white', fontLV)
                imageDraw.text((523, 690), f'{ds}', (0, 162, 232), fontBoldLV)
                imageDraw.text((37, 725), f'{music["basic_info"]["artist"]}', 'black', font)
                imageDraw.text((35, 831), f'{tag}', 'black', font)
                imageDraw.text((35, 930), f'{chart["charter"]}', 'black', font)
                tap = chart['notes'][0]
                hold = chart['notes'][1]
                slide = chart['notes'][2]
                touch = chart['notes'][3]
                breaknote = chart['notes'][4]
                imageDraw.text((68, 1092), f'{tap}', 'white', fontLV)
                imageDraw.text((236, 1092), f'{slide}', 'white', fontLV)
                imageDraw.text((433, 1092), f'{touch}', 'white', fontLV)
                imageDraw.text((68, 1215), f'{hold}', 'white', fontLV)
                imageDraw.text((236, 1215), f'{breaknote}', 'white', fontLV)
                imageDraw.text((433, 1215), f'{tap + slide + hold + breaknote + touch}', 'white', fontLV)
            await query_chart.send(Message([
                {
                    "type": "text",
                    "data": {
                        "text": f"▾ [Sender: {nickname}]\n  Details - {music['title']}\n"
                    }
                },
                {
                    "type": "image",
                    "data": {
                        "file": f"base64://{str(image_to_base64(baseimage), encoding='utf-8')}"
                    }
                }
            ]))
        except Exception as e:
            await query_chart.send(f"▿ 无匹配乐曲\n我没有找到该谱面，或者当前此歌曲刚刚上线，部分数据残缺。如果是后者等等再试试吧！\n[Exception Occurred]\n{e}")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        try:
            pic_dir = 'src/static/mai/pic/'         
            baseimage = Image.open(os.path.join(pic_dir, f'id.png')).convert('RGBA')
            try:
                file = requests.get(f"https://www.diving-fish.com/covers/{music['id']}.jpg")
                imagedata = Image.open(BytesIO(file.content)).convert('RGBA')
                imagedata = imagedata.resize((int(600), int(600)))
            except:
                try:
                    pic_cover = 'src/static/mai/cover/'
                    try:
                        imagedata = Image.open(os.path.join(pic_cover, f"{music['id']}.jpg")).convert('RGBA')
                    except:
                        imagedata = Image.open(os.path.join(pic_cover, f"{music['id']}.png")).convert('RGBA')
                    imagedata = imagedata.resize((int(600), int(600)))
                except:
                    imagedata = Image.open(os.path.join(pic_dir, f'noimage.png')).convert('RGBA')
            baseimage.paste(imagedata, (0,0), mask=imagedata.split()[3])
            font = ImageFont.truetype('src/static/HOS.ttf', 19, encoding='utf-8')
            fontBold = ImageFont.truetype('src/static/HOS_Med.ttf', 13, encoding='utf-8')
            fontBoldL = ImageFont.truetype('src/static/HOS_Med.ttf', 28, encoding='utf-8')
            fontLV = ImageFont.truetype('src/static/HOS.ttf', 36, encoding='utf-8')
            fontBoldLV = ImageFont.truetype('src/static/HOS_Med.ttf', 20, encoding='utf-8')
            fontTools = ImageFont.truetype('src/static/adobe_simhei.otf', 20, encoding='utf-8')
            imageDraw = ImageDraw.Draw(baseimage);
            imageDraw.text((70, 618), f'{music["id"]}', 'white', fontBold)
            if coloumWidth(music["title"]) > 30:
                title = changeColumnWidth(music["title"], 20) + '...'
                imageDraw.text((33, 660), title, 'black', fontBoldL)
            else:
                imageDraw.text((33, 660), f'{music["title"]}', 'black', fontBoldL)
            if int(music["basic_info"]["bpm"]) >= 100:
                imageDraw.text((511, 637), f'{music["basic_info"]["bpm"]}', 'black', fontLV)
            else:
                imageDraw.text((508, 637), f' {music["basic_info"]["bpm"]}', 'black', fontLV)
            imageDraw.text((37, 705), f'{music["basic_info"]["artist"]}', 'black', font)
            imageDraw.text((44, 810), f'{music["basic_info"]["genre"]}', 'black', font)
            imageDraw.text((44, 903), f'{music["basic_info"]["from"]}', 'black', font)
            imageDraw.text((56, 1088), f'{"  -  ".join(music["level"])}', 'white', fontLV)
            imageDraw.text((56, 1205), f'{" - ".join(str(music["ds"]).split(","))}', 'white', fontBoldLV)
            file = f"https://www.diving-fish.com/covers/{music['id']}.jpg"
            await query_chart.send(Message([
                {
                    "type": "text",
                    "data": {
                        "text": f"▾ [Sender: {nickname}]\n  Music Details - {music['title']}\n"
                    }
                },
                {
                    "type": "image",
                    "data": {
                        "file": f"base64://{str(image_to_base64(baseimage), encoding='utf-8')}"
                    }
                }
            ]))
        except Exception as e:
            await query_chart.send(f"▿ 无匹配乐曲\n啊这...我没有找到这个歌。\n换一个试试吧。\n[Exception Occurred]\n{e}")

xp_list = ['滴蜡熊', '幸隐', '14+', '白潘', '紫潘', 'PANDORA BOXXX', '排队区', '旧框', '干饭', '超常maimai', '收歌', '福瑞', '削除', 'HAPPY', '谱面-100号', 'lbw', '茄子卡狗', '打五把CSGO', '一姬', '打麻将', '光吉猛修', '怒锤', '暴漫', '鼓动', '鼓动(红)', '大司马', '电棍', '海子姐', '东雪莲', 'GIAO', '去沈阳大街', '一眼丁真', '陈睿']

jrxp = on_command('jrxp', aliases={'今日性癖'})


@jrxp.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qq = int(event.get_user_id())
    nickname = event.sender.nickname
    h = hash(qq)
    rp = h % 100
    xp = random.randint(0,32)
    s = f"▾ [Sender: {nickname}]\n  今日性癖\n{nickname}今天的性癖是{xp_list[xp]}，人品值是{rp}%.\n不满意的话再随一个吧！"
    await jrxp.finish(Message([
        {"type": "text", "data": {"text": s}}
    ]))


wm_list = ['拼机', '推分', '越级', '下埋', '夜勤', '练底力', '练手法', '打旧框', '干饭', '抓DX分', '收歌', '理论值', '打东方曲', '打索尼克曲']
bwm_list_perfect = ['拆机:然后您被机修当场处决', '女装:怎么这么好康！（然后受到了欢迎）', '耍帅:看我耍帅还AP+', '击剑:Alea jacta est!(SSS+)', '打滴蜡熊:看我今天不仅推了分，还收了歌！', '日麻:看我三倍役满!!!你们三家全都起飞!!!', '出勤:不出则已，一出惊人，当场AP，羡煞众人。', '看手元:哦原来是这样！看了手元果真推分了。', '霸机:这么久群友都没来，霸机一整天不是梦！', '打Maipad: Maipad上收歌了，上机也收了。', '唱打: Let the bass kick! ', '抓绝赞: 把把2600，轻松理论值！']
bwm_list_bad = ['拆机:不仅您被机修当场处决，还被人尽皆知。', '女装:杰哥说你怎么这么好康！让我康康！！！（被堵在卫生间角落）', '耍帅:星星全都粉掉了......', '击剑:Alea jacta est!(指在线下真实击剑)', '打滴蜡熊:滴蜡熊打你。', '日麻:我居然立直放铳....等等..三倍役满??????', '出勤:当场分数暴毙，惊呆众人。', '看手元:手法很神奇，根本学不来。', '霸机:......群友曰:"霸机是吧？踢了！"', '打Maipad: 上机还是不大会......', '唱打: 被路人拍下上传到了某音。', '抓绝赞: 啊啊啊啊啊啊啊捏妈妈的我超！！！ --- 这是绝赞(好)的音效。']
tips_list = ['在游戏过程中,请您不要大力拍打或滑动机器!', '建议您常多备一副手套。', '游玩时注意手指安全。', '游玩过程中注意财物安全。自己的财物远比一个SSS+要更有价值。', '底力不够？建议下埋！不要强行越级，手癖难解。', '文明游玩，游戏要排队，不要做不遵守游戏规则的玩家！', '人品值和宜忌每天0点都会刷新，不喜欢总体运势可以再随一次。', '疫情防护，人人有责。游玩结束后请主动佩戴口罩！', '出勤时注意交通安全。', '迪拉熊不断吃绝赞也不要大力敲打他哟。', '热知识：DX理论值是101.0000，但是旧框没有固定的理论值。', '冷知识：每个绝赞 Perfect 等级有 2600/2550/2500，俗称理论/50落/100落。']
fx_list = ['东', '西', '南', '北']
play_list = ['1P', '2P', '排队区']

jrwm = on_command('/text 今日运势', aliases={'/text 今日舞萌'})
jrwmnew = on_command('今日运势', aliases={'今日舞萌'})

@jrwmnew.handle()
async def _(bot: Bot, event: Event, state: T_State):   
    qq = int(event.get_user_id())
    nickname = event.sender.nickname
    h = hash(qq)
    rp = h % 100
    luck = hash(int((h * 4) / 3)) % 100
    ap = hash(int(((luck * 100) * (rp) * (hash(qq) / 4 % 100)))) % 100
    wm_value = []
    good_value = {}
    bad_value = {}
    good_count = 0
    bad_count = 0
    dwm_value_1 = random.randint(0,11)
    dwm_value_2 = random.randint(0,11)
    tips_value = random.randint(0,11)
    now = datetime.datetime.now()
    for i in range(14):
        wm_value.append(h & 3)
        h >>= 2
    pic_dir = 'src/static/mai/pic/'         
    baseimage =  Image.open(os.path.join(pic_dir, f'KibaTips.png')).convert('RGBA')
    font = ImageFont.truetype('src/static/HOS.ttf', 36, encoding='utf-8')
    fonttips = ImageFont.truetype('src/static/HOS.ttf', 24, encoding='utf-8')
    font1 = ImageFont.truetype('src/static/HOS.ttf', 38, encoding='utf-8')
    fontLV = ImageFont.truetype('src/static/HOS.ttf', 72, encoding='utf-8')
    fontBold = ImageFont.truetype('src/static/HOS_Med.ttf', 20, encoding='utf-8')
    fontBoldL = ImageFont.truetype('src/static/HOS_Med.ttf', 48, encoding='utf-8')
    imageDraw = ImageDraw.Draw(baseimage);
    imageDraw.text((35, 125), f"{now.year}/{now.month}/{now.day} {now.hour}:{now.strftime('%M')}:{now.strftime('%S')}", 'black', font)
    if luck >= 50:
        imageDraw.text((962, 228), f"吉", 'white', font1)
    else:
        imageDraw.text((962, 228), f"凶", 'white', font1)
    if dwm_value_1 == dwm_value_2:
        imageDraw.text((142, 565), f"并无适宜。", 'black', font)
        imageDraw.text((142, 710), f"也并无忌惮。", 'black', font)
    else:
        imageDraw.text((142, 565), f"{bwm_list_perfect[dwm_value_1]}", 'black', font)
        imageDraw.text((142, 710), f"{bwm_list_bad[dwm_value_2]}", 'black', font)
    imageDraw.text((170, 880), f"{ap}", 'white', fontLV)
    for i in range(14):
        if wm_value[i] == 3:
            good_value[good_count] = i
            good_count = good_count + 1
        elif wm_value[i] == 0:
            bad_value[bad_count] = i
            bad_count = bad_count + 1
    if good_count == 0:
        imageDraw.text((420, 925), f"出勤诸事不宜。", 'black', font)
    else:
        imageDraw.text((420, 925), f"出勤宜做以下 {good_count} 项事:", 'black', font)
        s = ""
        for i in range(good_count):
            s += f'{wm_list[good_value[i]]} '
        slist = s.split(" ")
        newslist = ""
        for i in range(len(slist)):
            if i % 7 == 0 and i != 0:
                newslist += "\n"
            newslist += f'{slist[i]} '
        imageDraw.text((350, 1000), f"{newslist}", 'black', font)
    if bad_count == 0:
        imageDraw.text((420, 1100), f"出勤一切顺利。", 'black', font)
    else:
        imageDraw.text((420, 1100), f"出勤不宜做以下 {bad_count} 项事:", 'black', font)
        s = ""
        for i in range(bad_count):
            s += f'{wm_list[bad_value[i]]} '
        slist = s.split(" ")
        newslist = ""
        for i in range(len(slist)):
            if i % 7 == 0 and i != 0:
                newslist += "\n"
            newslist += f'{slist[i]} '
        imageDraw.text((350, 1175), f"{newslist}", 'black', font)
    imageDraw.text((120, 1443), f"{tips_list[tips_value]}", 'black', fonttips)
    music = total_list[hash(qq) % len(total_list)]
    try:
        file = requests.get(f"https://www.diving-fish.com/covers/{music['id']}.jpg")
        imagedata = Image.open(BytesIO(file.content)).convert('RGBA')
        imagedata = imagedata.resize((int(400), int(400)))
    except:
         try:
             pic_cover = 'src/static/mai/cover/'
             try:
                imagedata = Image.open(os.path.join(pic_cover, f"{music['id']}.jpg")).convert('RGBA')
             except:
                imagedata = Image.open(os.path.join(pic_cover, f"{music['id']}.png")).convert('RGBA')
             imagedata = imagedata.resize((int(400), int(400)))
         except:
             imagedata = Image.open(os.path.join(pic_dir, f'noimage.png')).convert('RGBA')
             imagedata = imagedata.resize((int(400), int(400)))
    baseimage.paste(imagedata, (90,1801), mask=imagedata.split()[3])
    imageDraw.text((582, 1773), f"{music['id']}", 'black', fontBold)
    if coloumWidth(music["title"]) > 30:
        title = changeColumnWidth(music["title"], 20) + '...'
        imageDraw.text((539, 1823), title, 'black', fontBoldL)
    else:
        imageDraw.text((539, 1823), f"{music['title']}", 'black', fontBoldL)
    imageDraw.text((539, 1890), f"{music['basic_info']['artist']}", 'black', fonttips)
    imageDraw.text((539, 2040), f"{music['basic_info']['genre']}", 'black', fonttips)
    imageDraw.text((539, 2150), f"{music['basic_info']['from']}", 'black', fonttips)
    imageDraw.text((95, 2290), f'{"  -  ".join(music["level"])}', 'black', font1)
    await jrwmnew.send(Message([
            {
                "type": "image",
                "data": {
                    "file": f"base64://{str(image_to_base64(baseimage), encoding='utf-8')}"
                }
            },
            {
                    "type": "text",
                    "data": {
                        "text": f"在查找文字版本的运势板吗？输入命令 '/text 今日运势' 即可激活文字版运势。"
                    }
            }
        ]))


@jrwm.handle()
async def _(bot: Bot, event: Event, state: T_State):   
    qq = int(event.get_user_id())
    nickname = event.sender.nickname
    h = hash(qq)
    rp = h % 100
    luck = hash(int((h * 4) / 3)) % 100
    ap = hash(int(((luck * 100) * (rp) * (hash(qq) / 4 % 100)))) % 100
    wm_value = []
    good_value = {}
    bad_value = {}
    good_count = 0
    bad_count = 0
    dwm_value_1 = random.randint(0,11)
    dwm_value_2 = random.randint(0,11)
    tips_value = random.randint(0,11)
    now = datetime.datetime.now()  
    for i in range(14):
        wm_value.append(h & 3)
        h >>= 2
    s = f"▾ [Sender: {nickname}]\n  Fortune | 运势板\n◢ 查询时间\n{now.year}/{now.month}/{now.day} {now.hour}:{now.strftime('%M')}:{now.strftime('%S')}\n\n"
    s += f"◢ 占卜板\n---------------------\n"
    if rp >= 50 and rp < 70 or rp >= 70 and rp < 90 and luck < 60:
        s += "末吉: 有那么一点小幸运，打maimai吃了几分，不亏不亏~"
    elif rp >= 70 and rp < 90 and luck >= 60 or rp >= 90 and luck < 80:
        s += "吉: 今天各种顺利，是轻松满足的一天捏！"
    elif rp >= 90 and luck >= 80:
        s += "大吉: 我的天呐~在线蹲个办法让我水逆一次啊！！"
    elif rp >= 10 and rp < 30 and luck < 40:
        s += "凶: emm...粉了一串纵连。好嘛，有什么问题吗，没问题啦~"
    elif rp < 10 and luck < 10:
        s += "大凶: 今天稍微有点倒霉捏。只要能苟，问题就不大~"
    else:
        s += "小凶: 有那么一丢丢的坏运气，不过不用担心捏。莫得问题~"
    s += f"\n---------------------\n人品值: {rp}%  |  幸运值: {luck}%\n"
    s += f"\n今日出勤运势概览：\n"
    if dwm_value_1 == dwm_value_2:
        s += f'平 ▷ 今天总体上平平无常。向北走有财运，向南走运不佳....等一下，这句话好像在哪儿听过？\n'
    else:
        s += f'宜 ▷ {bwm_list_perfect[dwm_value_1]}\n'
        s += f'忌 ▷ {bwm_list_bad[dwm_value_2]}\n'
    s += f"\n◢ 推歌板\n收歌指数: {ap}%\n最佳朝向: {fx_list[random.randint(0, 3)]}\n最佳游戏位置: {play_list[random.randint(0, 2)]}\n"
    for i in range(14):
        if wm_value[i] == 3:
            good_value[good_count] = i
            good_count = good_count + 1
        elif wm_value[i] == 0:
            bad_value[bad_count] = i
            bad_count = bad_count + 1
    if good_count == 0:
        s += "今天没有任何适合做的事情...诸事不宜，小心破防..."
    else:
        s += f'出勤宜做以下 {good_count} 项事:\n'
        for i in range(good_count):
            s += f'{wm_list[good_value[i]]} '
    if bad_count == 0:
        s += '\n今天诸事顺利！没有不建议做的事情捏~\n'
    else:
        s += f'\n今天不应做以下 {bad_count} 项事:\n'
        for i in range(bad_count):
            s += f'{wm_list[bad_value[i]]} '
    s += f'\n\n◢ 运势板\n有一些 Tips:\n{tips_list[tips_value]}\n'
    s += "运势锦囊:\n"
    music = total_list[hash(qq) % len(total_list)]
    await jrwm.finish(Message([{"type": "text", "data": {"text": s}}] + song_txt(music) + [{"type": "text", "data": {"text": "图片版运势板已上线！使用命令 '今日运势' 试试吧。"}}]))


randomthings = ['推分成功！！正当你兴奋之余，突然机厅断电了。', '你心血来潮打HERA，绿了两串纵连之后转身掏出了筋膜枪。','你打花一轮的时候，后面传来了:"铸币吧打野走位，像那B三狼。" 看来你要与OTTO一起出勤了。', 'STOP Playing MAIMAI', '最心心念念的歌曲推分成功啦！']
cqmn = on_command("出勤模拟")
@cqmn.handle()
async def _(bot: Bot, event: Event, state: T_State):
    nickname = event.sender.nickname
    now = datetime.datetime.now()
    qq = int(event.get_user_id())
    randomid = random.randint(0,4)
    s = f"▾ [Sender: {nickname}]\n  Attend-Simulator | 出勤模拟器\n您今天出勤的随机事件:\n{randomthings[randomid]}\n你今天必可以推成功的歌曲:\n"
    music = total_list[hash(qq) * now.day * now.month % len(total_list)]
    await cqmn.finish(Message([{"type": "text", "data": {"text": s}}] + song_txt(music)))

jrrp = on_command('jrrp', aliases={'人品值'})

@jrrp.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qq = int(event.get_user_id())
    nickname = event.sender.nickname
    h = hash(qq)
    rp = h % 100
    luck = hash(int((h * 4) / 3)) % 100
    ap = hash(int(((luck * 100) * (rp) * (hash(qq) / 4 % 100)))) % 100
    s = f"▾ [Sender: {nickname}]\n Character | 人品签\n----------------------\n"
    s += f"人品值: {rp}%\n"
    s += f"幸运度: {luck}%"
    if rp >= 50 and rp < 70 or rp >= 70 and rp < 90 and luck < 60:
        s += "            小吉!\n"
    elif rp >= 70 and rp < 90 and luck >= 60 or rp >= 90 and luck < 80:
        s += "             吉!\n"
    elif rp >= 90 and luck >= 80:
        s += "            大吉!\n"
    elif rp >= 10 and rp < 30 and luck < 40:
        s += "             凶!\n"
    elif rp < 10 and luck < 10:
        s += "            大凶!\n"
    else:
        s += "            小凶!\n"
    s += f"收歌率: {ap}%\n----------------------\n更多请查看今日运势或今日性癖。"
    await jrrp.finish(Message([
        {"type": "text", "data": {"text": s}}
    ]))

jrgq = on_command('/kiba 早', aliases={'签到', '/kiba 晚上好', '/kiba 上午好', '/kiba 下午好', '/kiba 中午好'})

@jrgq.handle()
async def _(bot: Bot, event: Event, state: T_State):
    nickname = event.sender.nickname
    day = datetime.datetime.now().day
    hour = datetime.datetime.now().hour
    mt = event.message_type
    db = get_driver().config.db
    sign = 1
    c = await db.cursor()
    if mt == "guild":
        await c.execute(f'select * from gld_table where uid="{event.user_id}"')
        data = await c.fetchone()
        if data is None:
            await jrgq.send(f"▿ [Sender: {nickname}]\n  Sign-in Error | 签到 - 错误\n在频道内，签到前需要将您的 QQ 进行绑定。您尚未将您的 QQ 绑定到小犽，请进行绑定或输入用户名再试一次。\n")
            return
        else:
            qq = int(data[0])
    else:
        qq = int(event.get_user_id())
    await c.execute(f'select * from sign_table')
    data1 = await c.fetchone()
    if data1 is None:
        await c.execute(f'insert into sign_table values (1, {qq}, {day})')
    else:
        if day != data1[2]:
            await c.execute(f'delete from sign_table')
            await c.execute(f'insert into sign_table values (1, {qq}, {day})')
        else:
            await c.execute(f'select * from sign_table where id={qq}')
            data2 = await c.fetchone()
            if data2 is None:
                await c.execute(f'select * from sign_table')
                data3 = await c.fetchall()
                if data3 == "":
                    await c.execute(f'insert into sign_table values (1, {qq}, {day})')
                else:
                    await c.execute(f'insert into sign_table values ({len(data3) + 1}, {qq}, {day})')
                    sign = len(data3) + 1
            else:
                await jrgq.finish(f"▿ [Sender: {nickname}]\n  Signed in | 已签到\n您貌似今天已经签过到啦！排名是第 {data2[0]} 位。")
                return
    await db.commit()
    s = f"▾ [Sender: {nickname}]\n  Sign In | 签到\n"
    if hour < 6:
        s += "您起来的这么早吗？！还是熬夜啦......"
    elif hour >= 6 and hour < 9:
        s += "早上好呀！"
    elif hour >= 9 and hour < 12:
        s += "上午好呀！"
    elif hour >= 12 and hour <= 18:
        s += "下午好！！"
    else:
        s += "晚上好啊。"
    h = hash(qq)
    rp = h % 100
    s += f"今天您的签到排名是第 {sign} 位。\n您人品值是 {rp}，为您推荐：\n"
    music = total_list[(h * 4) % len(total_list)]
    await jrgq.finish(Message([
        {"type": "text", "data": {"text": s}}
    ] + song_txt(music)))

music_aliases = defaultdict(list)
f = open('src/static/aliases.csv', 'r', encoding='utf-8')
tmp = f.readlines()
f.close()
for t in tmp:
    arr = t.strip().split('\t')
    for i in range(len(arr)):
        if arr[i] != "":
            music_aliases[arr[i].lower()].append(arr[0])


find_song = on_regex(r".+是什么歌")


@find_song.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "(.+)是什么歌"
    name = re.match(regex, str(event.get_message())).groups()[0].strip().lower()
    nickname = event.sender.nickname
    if name not in music_aliases:
        await find_song.finish(f"▿ [Sender: {nickname}]\n  Search | 查歌 - 错误\n这个别称太新了，我找不到这首歌啦。\n但是您可以帮助我收集歌曲的别名！戳链接加入 Kiba 歌曲别名收集计划:\nhttps://docs.qq.com/form/page/DREJFWUtWektMSm9Y")
        return
    result_set = music_aliases[name]
    if len(result_set) == 1:
        music = total_list.by_title(result_set[0])
        await find_song.finish(Message([{"type": "text", "data": {"text": f"▾ [Sender: {nickname}]\n  Search Result | 别名查歌结果\n您说的应该是：\n"}}] + song_txt(music)))
    else:
        s = '\n'.join(result_set)
        await find_song.finish(f"▾ [Sender: {nickname}]\n  Search Results | 多个别名查歌结果\n您要找的可能是以下歌曲中的其中一首：\n{ s }")


query_score = on_command('分数线')


@query_score.handle()
async def _(bot: Bot, event: Event, state: T_State):
    r = "([绿黄红紫白])(id)?([0-9]+)"
    argv = str(event.get_message()).strip().split(" ")
    nickname = event.sender.nickname
    if len(argv) == 1 and argv[0] == '帮助':
        s = '''▾ Help for ACHV. Line 分数线 - 帮助
这个功能为你提供达到某首歌分数线的最低标准而设计的~~~
命令格式：分数线 <难度+歌曲id> <分数线>
例如：分数线 紫799 100
命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
以下为 TAP GREAT 的对应表：
GREAT/GOOD/MISS
TAP\t1/2.5/5
HOLD\t2/5/10
SLIDE\t3/7.5/15
TOUCH\t1/2.5/5
BREAK\t5/12.5/25(外加200落)'''
        await query_score.send(Message([{
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"
            }
        }]))
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0]).groups()
            level_labels = ['绿', '黄', '红', '紫', '白']
            level_labels2 = ['Basic', 'Advanced', 'Expert', 'Master', 'Re:MASTER']
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[1])
            music = total_list.by_id(chart_id)
            chart: Dict[Any] = music['charts'][level_index]
            tap = int(chart['notes'][0])
            slide = int(chart['notes'][2])
            hold = int(chart['notes'][1])
            touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
            brk = int(chart['notes'][-1])
            total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
            break_bonus = 0.01 / brk
            break_50_reduce = total_score * break_bonus / 4
            reduce = 101 - line
            if reduce <= 0 or reduce >= 101:
                raise ValueError
            await query_chart.send(f'''▾ [Sender: {nickname}]\n  ACHV. Line | 分数线
♪ {music['id']} ({music['type']})
{music['title']} | {level_labels2[level_index]}
设置的达成率为{line}%，其 Note 损失参照如下:
----------------------
此表格遵循的格式为:
类型 | ACHV.损失/个 | 最多损失数
----------------------
Great 评价:
Tap & Touch | {10000 / total_score:.4f}% | {(total_score * reduce / 10000):.2f}
Hold | {(10000 / total_score)* 2:.4f}% | {((total_score * reduce / 10000)/ 2):.2f}
Slide | {(10000 / total_score)* 3:.4f}% | {((total_score * reduce / 10000)/ 3):.2f}
Good 评价:
Tap & Touch | {(10000 / total_score)* 2.5:.4f}% | {((total_score * reduce / 10000)/ 2.5):.2f}
Hold | {(10000 / total_score)* 5:.4f}% | {((total_score * reduce / 10000)/ 5):.2f}
Slide | {(10000 / total_score)* 7.5:.4f}% | {((total_score * reduce / 10000)/ 7.5):.2f}
Miss 评价:
Tap & Touch | {(10000 / total_score)*5:.4f}% | {((total_score * reduce / 10000)/5):.2f}
Hold | {(10000 / total_score)* 10:.4f}% | {((total_score * reduce / 10000)/ 10):.2f}
Slide | {(10000 / total_score)* 15:.4f}% | {((total_score * reduce / 10000)/ 15):.2f}

Break 各评价损失:
注意: Break 的 Great 与 Perfect 评价都有细分等级，此表格的 Break Great 不做细分，仅为大约数供您参考。
本谱面每个 Break Perfect 2600 的达成率是 {((10000 / total_score) * 25 + (break_50_reduce / total_score * 100)* 4):.4f}%,谱面共 {brk} 个 Break，其占总体达成率的 {(((10000 / total_score) * 25 + (break_50_reduce / total_score * 100)* 4)* brk):.4f}%。
----------------------
此表格遵循的格式为:
类型 | ACHV.损失/个 | Tap Great 等价数
----------------------
Perfect 2550 | {break_50_reduce / total_score * 100:.4f}% | {(break_50_reduce / 100):.3f}
Perfect 2500 | {(break_50_reduce / total_score * 100)* 2:.4f}% | {(break_50_reduce / 100)* 2:.3f}
Great | ≈{((10000 / total_score) * 5 + (break_50_reduce / total_score * 100)* 4):.4f}% | ≈{5 + (break_50_reduce / 100)* 4:.3f}
Good | {((10000 / total_score) * 12.5 + (break_50_reduce / total_score * 100)* 4):.4f}% | {12.5 + (break_50_reduce / 100)* 4:.3f}
Miss | {((10000 / total_score) * 25 + (break_50_reduce / total_score * 100)* 4):.4f}% | {25 + (break_50_reduce / 100)* 4:.3f}''')
        except Exception:
            await query_chart.send("格式错误，输入 “分数线 帮助” 以查看帮助信息")

setplate = on_command('设置牌子', aliases={'setplate', '更换名牌板'})
@setplate.handle()
async def _(bot: Bot, event: Event, state: T_State):
    platenum = str(event.get_message()).strip()
    nickname = event.sender.nickname
    mt = event.message_type
    db = get_driver().config.db
    qq = str(event.get_user_id())
    c = await db.cursor()
    if mt == "guild":
        await c.execute(f'select * from gld_table where uid="{event.user_id}"')
        data = await c.fetchone()
        if data is None:
            await setplate.send(f"▿ [Sender: {nickname}]\n  Plate Changer Error | 错误\n在频道内，您需要绑定 QQ 才允许使用更换名牌版功能。您尚未将您的 QQ 绑定到小犽，请进行绑定或输入用户名再试一次。\n")
            return
        else:
            qq = str(data[0])
    if platenum == "":
        await setplate.finish(f"▿ [Sender: {nickname}]\n  Plate Changer | 更换名牌板\n除将/极/神/舞舞牌子需要您查询一次清谱后自动为您更换外，您还可以使用‘setplate 对应数字’更换普通名牌板。\nKiba 当前收录的普通名牌板如下(持续更新):\n0.默认\n1.maimai でらっくす\n2.全国制霸 でらっくす\n3.はっぴー（ゆにばーす）\n4.东方Projectちほー\n5.炎炎ノ消防队ちほー\n6.でらっくすちほー おしゃま牛乳\n另外内置了一个彩蛋牌子，是 KING of Performai 3rd ファイナリスト，提示是“21、11、9”。")
    elif int(platenum) < 0 and int(platenum) > 6 and int(platenum) != 1001:
        await setplate.finish(f"▿ [Sender: {nickname}]\n  Plate Changer | 更换名牌板\n请输入正确的名牌板号码。")
    else:
        await c.execute(f'select * from plate_table where id="{qq}"')
        data = await c.fetchone()
        if data is None:
            await c.execute(f'insert into plate_table values ({qq}, {platenum})')
        else:
            await c.execute(f'update plate_table set platenum={platenum} where id={qq}')
        await db.commit()
        await setplate.finish(f"▾ [Sender: {nickname}]\n   Plate Changer | 更换名牌板\n更换完成。")
    


best_40_pic = on_command('b40', aliases={'B40'})
@best_40_pic.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = str(event.get_message()).strip()
    nickname = event.sender.nickname
    mt = event.message_type
    db = get_driver().config.db
    c = await db.cursor()
    if username == "":
        if mt == "guild":
            await c.execute(f'select * from gld_table where uid="{event.user_id}"')
            data = await c.fetchone()
            if data is None:
                await best_40_pic.send(f"▿ [Sender: {nickname}]\n  Best 40: Error | 错误\n在频道内，免输入用户名的前提是需要将您的 QQ 进行绑定。您尚未将您的 QQ 绑定到小犽，请进行绑定或输入用户名再试一次。\n")
                return
            else:
                payload = {'qq': str(data[0])}
                await c.execute(f'select * from plate_table where id="{str(data[0])}"')
                data1 = await c.fetchone()
                if data1 is None:
                    platenum = 0
                else:
                    platenum = str(data1[1])
        else:
            payload = {'qq': str(event.get_user_id())}
            await c.execute(f'select * from plate_table where id="{str(event.get_user_id())}"')
            data1 = await c.fetchone()
            if data1 is None:
                platenum = 0
            else:
                platenum = str(data1[1])
    else:
        payload = {'username': username}
        platenum = 0
    try:
        img, success = await generate(payload, platenum)
    except Exception as e:
        await best_40_pic.send(f"▿ [Sender: {nickname}]\n  Best 40: Exception | 生成失败\n[Exception Occurred]\n{e}\n请检查查分器是否已正确导入所有乐曲成绩。\n若需要确认设置，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/")
        return
    if success == 400:
        await best_40_pic.send(f"▿ [Sender: {nickname}]\n  Best 40: Not Found | 找不到 ID\n此玩家 ID 没有找到。\n请检查一下您的用户名是否输入正确或有无注册查分器系统？如您没有输入ID，请检查您的QQ是否与查分器绑定正确。\n若需要确认设置，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/")
    elif success == 403:
        await best_40_pic.send(f'▿ [Sender: {nickname}]\n  Best 40: Banned | 被禁止\n{username} 不允许使用此方式查询 Best 40。\n如果是您的账户，请检查您的QQ是否与查分器绑定正确后直接输入“b40”。\n您需要修改查分器设置吗？请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/')
    else:
        if username == "":
            text = f'▾ [Sender: {nickname}]\n  Best 40 Details | 我的 B40\n您的 Best 40 如图所示。\n若您需要修改查分器数据，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/'
        else:
            text = f'▾ [Sender: {nickname}]\n  Best 40 Details | {username} 的 B40\n此 ID 的 Best 40 如图所示。\n'
        await best_40_pic.send(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.text(text),
            MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}")
        ]))

best_50_pic = on_command('b50', aliases={'B50'})

@best_50_pic.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = str(event.get_message()).strip()
    nickname = event.sender.nickname
    mt = event.message_type
    db = get_driver().config.db
    c = await db.cursor()
    if username == "":
        if mt == "guild":
            await c.execute(f'select * from gld_table where uid="{event.user_id}"')
            data = await c.fetchone()
            if data is None:
                await best_50_pic.send(f"▿ [Sender: {nickname}]\n  Best 50: Error | 错误\n在频道内，免输入用户名的前提是需要将您的 QQ 进行绑定。您尚未将您的 QQ 绑定到小犽，请进行绑定或输入用户名再试一次。\n")
                return
            else:
                payload = {'qq': str(data[0])}
                await c.execute(f'select * from plate_table where id="{str(data[0])}"')
                data1 = await c.fetchone()
                if data1 is None:
                    platenum = 0
                else:
                    platenum = str(data1[1])
        else:
            payload = {'qq': str(event.get_user_id())}
            await c.execute(f'select * from plate_table where id="{str(event.get_user_id())}"')
            data1 = await c.fetchone()
            if data1 is None:
                platenum = 0
            else:
                platenum = str(data1[1])
    else:
        payload = {'username': username}
        platenum = 0
    payload['b50'] = True
    try:
        img, success = await generate(payload, platenum)
    except Exception as e:
        await best_50_pic.send(f"▿ [Sender: {nickname}]\n  Best 50: Exception | 生成失败\n[Exception Occurred]\n{e}\n请检查查分器是否已正确导入所有乐曲成绩。\n若需要确认设置，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/")
        return
    if success == 400:
        await best_50_pic.send(f"▿ [Sender: {nickname}]\n  Best 50: Not Found | 找不到 ID\n您输入的玩家 ID 没有找到。\n请检查一下您的用户名是否输入正确或有无注册查分器系统？如您没有输入ID，请检查您的QQ是否与查分器绑定正确。\n若需要确认设置，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/")
    elif success == 403:
        await best_50_pic.send(f'▿ [Sender: {nickname}]\n  Best 50: Banned | 被禁止\n{username} 不允许使用此方式查询 Best 50。\n如果是您的账户，请检查您的QQ是否与查分器绑定正确后直接输入“b50”。\n您需要修改查分器设置吗？请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/')
    else:
        if username == "":
            text = f'▾ [Sender: {nickname}]\n  Best 50 Details | 我的 B50\n您的 Best 50 如图所示。\nBest 50 是 DX Splash Plus 及以后版本的定数方法，与当前版本的定数方法不相同。若您需要当前版本定数，请使用 Best 40。\n若您需要修改查分器数据，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/'
        else:
            text = f'▾ [Sender: {nickname}]\n  Best 50 Details | {username} 的 B50\n此 ID 的 Best 50 如图所示。\nBest 50 是 DX Splash Plus 及以后版本的定数方法，与当前版本的定数方法不相同。若您需要当前版本定数，请使用 Best 40。'
        await best_50_pic.send(Message([
            MessageSegment.reply(event.message_id),
            MessageSegment.text(text),
            MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}")
        ]))

disable_guess_music = on_command('猜歌设置', priority=0)


@disable_guess_music.handle()
async def _(bot: Bot, event: Event):
    if event.message_type != "group":
        await disable_guess_music.finish("▿ 猜歌 - 设置 - 注意\n您无法在私聊或频道内设置猜歌。")
        return
    arg = str(event.get_message())
    group_members = await bot.get_group_member_list(group_id=event.group_id)
    for m in group_members:
        if m['user_id'] == event.user_id:
            break
    su = Config.superuser
    if m['role'] != 'owner' and m['role'] != 'admin' and str(m['user_id']) not in su:
        await disable_guess_music.finish("▿ 猜歌 - 设置 - 无权限\n抱歉，只有群管理员/小犽管理者才有权调整猜歌设置。")
        return
    db = get_driver().config.db
    c = await db.cursor()
    if arg == '启用':
        try:
            await c.execute(f'update guess_table set enabled=1 where group_id={event.group_id}')
        except Exception:
            await disable_guess_music.finish(f"▿ 猜歌 - 设置\n您需要运行一次猜歌才可进行设置！")
    elif arg == '禁用':
        try:
            await c.execute(f'update guess_table set enabled=0 where group_id={event.group_id}')
        except Exception:
            await disable_guess_music.finish(f"▿ 猜歌 - 设置\n您需要运行一次猜歌才可进行设置！")
    else:
        await disable_guess_music.finish("▾ 猜歌 - 设置\n请输入 猜歌设置 启用/禁用")
        return
    await db.commit()
    await disable_guess_music.finish(f"▾ 猜歌 - 设置\n设置成功并已即时生效。\n当前群设置为: {arg}")
    
            
guess_dict: Dict[Tuple[str, str], GuessObject] = {}
guess_cd_dict: Dict[Tuple[str, str], float] = {}
guess_music = on_command('猜歌', priority=0)



async def guess_music_loop(bot: Bot, event: Event, state: T_State):
    await asyncio.sleep(10)
    guess: GuessObject = state["guess_object"]
    if guess.is_end:
        return
    cycle = state["cycle"]
    if cycle < 6:
        asyncio.create_task(bot.send(event, f"▾ 猜歌提示 | 第 {cycle + 1} 个 / 共 7 个\n这首歌" + guess.guess_options[cycle]))
    else:
        try:
            asyncio.create_task(bot.send(event, Message([
                MessageSegment.text("▾ 猜歌提示 | 第 7 个 / 共 7 个\n这首歌封面的一部分是："),
                MessageSegment.image("base64://" + str(guess.b64image, encoding="utf-8")),
                MessageSegment.text("快和群里的小伙伴猜一下吧！\n提示: 30 秒内可以回答这首歌的ID、歌曲标题或歌曲标题的大于5个字的连续片段，超时我将揭晓答案。")
            ])))
        except:
            asyncio.create_task(bot.send(event, Message([
                MessageSegment.text("▾ 猜歌提示 | 第 7 个 / 共 7 个\nemm....本来应该显示这个封面的一部分来着....但是出了点错误，那就用前面六个提示猜一下吧，相信你可以哒！30s内可以回答这首歌的ID、歌曲标题或歌曲标题的大于5个字的连续片段，超时我将揭晓答案。"),
            ])))
        asyncio.create_task(give_answer(bot, event, state))
        return
    state["cycle"] += 1
    asyncio.create_task(guess_music_loop(bot, event, state))


async def give_answer(bot: Bot, event: Event, state: T_State):
    await asyncio.sleep(30)
    guess: GuessObject = state["guess_object"]
    if guess.is_end:
        return
    mid = guess.music['id']
    if int(mid) >= 10001:
        mid = int(mid) - 10000
    try:
        asyncio.create_task(bot.send(event, Message([MessageSegment.text("▿ 答案\n都没有猜到吗......那现在揭晓答案！\n♪ " + f"{guess.music['id']} > {guess.music['title']}\n"), MessageSegment.image(f"https://www.diving-fish.com/covers/{mid}.png")])))
    except:
        try:
            asyncio.create_task(bot.send(event, Message([MessageSegment.text("▿ 答案\n都没有猜到吗......那现在揭晓答案！\n♪ " + f"{guess.music['id']} > {guess.music['title']}\n"), MessageSegment.image(f"https://www.diving-fish.com/covers/{mid}.jpg")])))
        except:
            asyncio.create_task(bot.send(event, Message([MessageSegment.text("▿ 答案\n都没有猜到吗......那现在揭晓答案！\n♪ " + f"{guess.music['id']} > {guess.music['title']}\n" + "使用 id 命令可以查看歌曲详情。")])))
    del guess_dict[state["k"]]


@guess_music.handle()
async def _(bot: Bot, event: Event, state: T_State):
    mt = event.message_type
    if mt == "guild":
        k = (mt, event.guild_id)
    else:
        k = (mt, event.user_id if mt == "private" else event.group_id)
    if mt == "group":
        gid = event.group_id
        db = get_driver().config.db
        c = await db.cursor()
        await c.execute(f"select * from guess_table where group_id={gid}")
        data = await c.fetchone()
        if data is None:
            await c.execute(f'insert into guess_table values ({gid}, 1)')
        elif data[1] == 0:
            await guess_music.send("▿ 猜歌 - 禁用\n抱歉啦，本群的管理员已禁用猜歌。")
            return
        if k in guess_dict:
            if k in guess_cd_dict and time.time() > guess_cd_dict[k] - 400:
                # 如果已经过了 200 秒则自动结束上一次
                del guess_dict[k]
            else:
                await guess_music.send("▿ 猜歌 - 正在进行中\n当前已有正在进行的猜歌，要不要来参与一下呀？")
                return
    if len(guess_dict) >= 5:
        await guess_music.finish("▿ 猜歌 - 同时进行的群过多\n小犽有点忙不过来了...现在正在猜的群太多啦，晚点再试试如何？")
        return
    if k in guess_cd_dict and time.time() < guess_cd_dict[k]:
        await guess_music.finish(f"▿ 猜歌 - 冷却中\n已经猜过一次啦！下次猜歌会在 {time.strftime('%H:%M', time.localtime(guess_cd_dict[k]))} 可用噢。")
        return
    guess = GuessObject()
    guess_dict[k] = guess
    state["k"] = k
    state["guess_object"] = guess
    state["cycle"] = 0
    guess_cd_dict[k] = time.time() + 600
    await guess_music.send("▾ 猜歌\n我将从热门乐曲中选择一首歌，并描述它的一些特征。大家可以猜一下！\n知道答案的话，可以告诉我谱面ID、歌曲标题或者标题中连续5个以上的片段来向我阐述答案！\n猜歌时查歌等其他命令依然可用，这个命令可能会很刷屏，管理员可以根据情况通过【猜歌设置】命令设置猜歌是否启用。")
    asyncio.create_task(guess_music_loop(bot, event, state))

guess_music_solve = on_message(priority=20)

@guess_music_solve.handle()
async def _(bot: Bot, event: Event, state: T_State):
    mt = event.message_type
    if mt == "guild":
        k = (mt, event.guild_id)
    else:
        k = (mt, event.user_id if mt == "private" else event.group_id)
    if k not in guess_dict:
        return
    ans = str(event.get_message())
    guess = guess_dict[k]
    # await guess_music_solve.send(ans + "|" + guess.music['id'])
    if ans == guess.music['id'] or (ans.lower() == guess.music['title'].lower()) or (len(ans) >= 5 and ans.lower() in guess.music['title'].lower()):
        guess.is_end = True
        del guess_dict[k]
        mid = guess.music['id']
        if int(mid) >= 10001:
            mid = int(mid) - 10000
        try:
            await guess_music_solve.finish(Message([
                MessageSegment.reply(event.message_id),
                MessageSegment.text("▾ 答案\n您猜对了！答案就是：\n" + f"♪ {guess.music['id']} > {guess.music['title']}\n"),
                MessageSegment.image(f"https://www.diving-fish.com/covers/{mid}.png")
            ]))
        except:
            await guess_music_solve.finish(Message([
                MessageSegment.reply(event.message_id),
                MessageSegment.text("▾ 答案\n您猜对了！答案就是：\n" + f"♪ {guess.music['id']} > {guess.music['title']}\n" + "使用 id 命令可以查看歌曲详情。"),
            ]))
waiting_set = on_command("设置店铺")
@waiting_set.handle()
async def _(bot: Bot, event: Event, state: T_State):
    argv = str(event.get_message()).strip().split(" ")
    db = get_driver().config.db
    now = datetime.datetime.now()
    c = await db.cursor()
    if event.message_type != "group":
        await waiting_set.finish("▿ 出勤大数据 - 设置\n抱歉，群管理员/小犽管理者才有权调整店铺设置，请在群内再试一次。")
        return
    arg = str(event.get_message())
    group_members = await bot.get_group_member_list(group_id=event.group_id)
    for m in group_members:
        if m['user_id'] == event.user_id:
            break
    su = Config.superuser
    if m['role'] != 'owner' and m['role'] != 'admin' and str(m['user_id']) not in su:
        await waiting_set.finish("▿ 出勤大数据 - 设置\n抱歉，只有群管理员/小犽管理者才有权调整店铺设置。")
        return
    if len(argv) > 2 or argv[0] == "帮助":
        await waiting_set.finish("▾ 出勤大数据 - 帮助\n命令格式是:\n设置店铺 [店铺名] [店铺位置]\n注意只有管理员才可以有权设置店铺信息哦。")
        return
    time = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.strftime('%M')}:{now.strftime('%S')}"
    await c.execute(f'select * from waiting_table where shop="{argv[0]}"')
    data = await c.fetchone()
    if data is None:
        if len(argv) == 2:
            await c.execute(f'insert into waiting_table values ("{argv[0]}","{argv[1]}",0,"{time}")')
            await db.commit()
        elif len(argv) == 1:
            await c.execute(f'insert into waiting_table values ("{argv[0]}","待设置",0,"{time}")')
            await db.commit()
        await waiting_set.finish(f"▾ 出勤大数据\n已成功设置店铺。\n店铺名: {argv[0]}\n出勤人数: 0\n修改时间: {time}")
    else:
        if len(argv) == 1:
            await waiting_set.finish("▿ 出勤大数据 - 设置\n已存在此店铺，您可以选择修改店铺位置信息。")
            return
        elif len(argv) == 2:
            await c.execute(f'update waiting_table set location={argv[1]} where shop={argv[0]}')
            await waiting_set.finish(f"▾ 出勤大数据\n已成功设置店铺。\n店铺名: {argv[0]}\n出勤人数: 0\n修改时间: {time}")
            await db.commit()

waiting = on_regex(r'(.+) ([0-9]?几?\+?\-?1?)人?', rule=to_me(), priority=18)
@waiting.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "(.+) ([0-9]?几?\+?\-?1?)人?"
    res = re.match(regex, str(event.get_message()).lower())
    db = get_driver().config.db
    now = datetime.datetime.now()
    c = await db.cursor()
    time = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.strftime('%M')}:{now.strftime('%S')}"
    if res.groups()[1] == "几":
        await c.execute(f'select * from waiting_table where shop="{res.groups()[0]}"')
        data = await c.fetchone()
        if data is None:
            await waiting.finish("▿ 出勤大数据\n此店铺不存在，请联系管理员添加此店铺。")
            return
        else:
            await waiting.finish(f"▾ 出勤大数据\n{data[0]} 有 {data[2]} 人出勤。最后更新时间:{data[3]}")
            return
    elif res.groups()[1] == "+1":
        await c.execute(f'select * from waiting_table where shop="{res.groups()[0]}"')
        data = await c.fetchone()
        if data is None:
            await waiting.finish("▿ 出勤大数据\n此店铺不存在，请联系管理员添加此店铺。")
            return
        else:
            await c.execute(f'update waiting_table set wait={data[2] + 1}, updated="{time}" where shop="{res.groups()[0]}"')
            await db.commit()
            await waiting.finish(f"▾ 出勤大数据\n更新完成！\n{data[0]} 有 {data[2] + 1} 人出勤。最后更新时间:{time}")
            return
    elif res.groups()[1] == "-1":
        await c.execute(f'select * from waiting_table where shop="{res.groups()[0]}"')
        data = await c.fetchone()
        if data is None:
            await waiting.finish("▿ 出勤大数据\n此店铺不存在，请联系管理员添加此店铺。")
            return
        else:
            if data[2] - 1 < 0:
                await waiting.finish("▿ 出勤大数据\n不能再减了，再减就变成灵异事件了！")
                return
            await c.execute(f'update waiting_table set wait={data[2] - 1}, updated="{time}" where shop="{res.groups()[0]}"')
            await db.commit()
            await waiting.finish(f"▾ 出勤大数据\n更新完成！\n{data[0]} 有 {data[2] - 1} 人出勤。最后更新时间:{time}")
            return
    else:
        await c.execute(f'select * from waiting_table where shop="{res.groups()[0]}"')
        data = await c.fetchone()
        if data is None:
            await waiting.finish("▿ 出勤大数据\n此店铺不存在，请联系管理员添加此店铺。")
            return
        else:
            await c.execute(f'update waiting_table set wait={res.groups()[1]}, updated="{time}" where shop="{res.groups()[0]}"')
            await db.commit()
            await waiting.finish(f"▾ 出勤大数据\n更新完成！\n{res.groups()[0]} 有 {res.groups()[1]} 人出勤。最后更新时间:{time}")
            return

location = on_regex(r'.+位置', rule=to_me())
@location.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "(.+)位置"
    name = re.match(regex, str(event.get_message())).groups()[0].strip().lower()
    db = get_driver().config.db
    c = await db.cursor()
    await c.execute(f'select * from waiting_table where shop="{name}"')
    data = await c.fetchone()
    if data is None:
        await waiting.finish("▿ 出勤大数据\n此店铺不存在，请联系管理员添加此店铺。")
        return
    else:
        await waiting.finish(f"▾ 出勤大数据 - 位置\n{data[0]}: {data[1]}")
        return

rand_ranking = on_command("段位模式")

@rand_ranking.handle()
async def _(bot: Bot, event: Event, state: T_State):
    nickname = event.sender.nickname
    argv = str(event.get_message()).strip().split(" ")
    try:
        if argv[0] == "帮助":
            rand_result = "▾ 段位模式 - 帮助\n命令是:\n段位模式 <Expert/Master> <初级/中级/上级/超上级*1> <计算> (<Great数量> <Good数量> <Miss数量> <剩余的血量*3>)*2\n* 注意:\n*1 超上级选项只对Master有效。\n*2 只有使用计算功能的时候才需要打出括号内要求的内容。注意如果您对应的 Great 或 Good 或 Miss 的数量是0，请打0。\n *3 您可以指定剩余的血量(Life)，如果您不指定血量，默认按满血计算。"
        else:
            rand_result = f'▾ [Sender: {nickname}]\n  Rank Mode\nRank: {argv[0]} {argv[1]}\n'
            if argv[0] == "Expert" or argv[0] == "expert" or argv[0] == "EXPERT":
                if argv[1] == "初级":
                    level = ['7', '8', '9']
                    life = 700
                    gr = -2
                    gd = -2
                    miss = -5
                    clear = 50
                    min = 7
                    max = 9
                    msg = "\n注意: 在难度选择时，请优先采用适合本段位的等级最高的难度，若红、紫谱面难度相同，优先采用红谱。"
                elif argv[1] == "中级":
                    level = ['8', '9', '10']
                    life = 600
                    gr = -2
                    gd = -2
                    miss = -5
                    clear = 50
                    min = 8
                    max = 10
                    msg = "\n注意: 在难度选择时，请优先采用适合本段位的等级最高的难度，若红、紫谱面难度相同，优先采用红谱。"
                elif argv[1] == "上级":
                    level = ['10+', '11', '11+', '12', '12+']
                    life = 500
                    gr = -2
                    gd = -2
                    miss = -5
                    clear = 50
                    min = '10+'
                    max = '12+'
                    msg = "\n注意: 在难度选择时，请优先采用适合本段位的等级最高的难度，若红、紫谱面难度相同，优先采用红谱。"
                else:
                    rand_ranking.send(f"▿ [Sender: {nickname}]\n  Rank Error\n寄，Expert 等级只有初级、中级、上级！")
                    return
            elif argv[0] == "Master" or argv[0] == "master" or argv[0] == "MASTER":
                if argv[1] == "初级":
                    level = ['10', '10+', '11', '11+', '12']
                    life = 700
                    gr = -2
                    gd = -2
                    miss = -5
                    clear = 50
                    min = 10
                    max = 12
                    msg = "\n注意: 在难度选择时，请优先采用适合本段位的等级最高的难度，若紫、白谱面难度相同，优先采用紫谱。"
                elif argv[1] == "中级":
                    level = ['12', '12+', '13']
                    life = 500
                    gr = -2
                    gd = -2
                    miss = -5
                    clear = 50
                    min = 12
                    max = 13
                    msg = "\n注意: 在难度选择时，请优先采用适合本段位的等级最高的难度，若紫、白谱面难度相同，优先采用紫谱。"
                elif argv[1] == "上级":
                    level = ['13', '13+', '14.0', '14.1', '14.2', '14.3']
                    life = 300
                    gr = -2
                    gd = -2
                    miss = -5
                    clear = 20
                    min = 13
                    max = 14.3
                    msg = "\n注意: 在难度选择时，请优先采用适合本段位的等级最高的难度，若紫、白谱面难度相同，优先采用紫谱。"
                elif argv[1] == "超上级":
                    level = ['14.4', '14.5', '14.6', '14+', '15']
                    life = 100
                    gr = -2
                    gd = -3
                    miss = -5
                    clear = 10
                    min = 14.4
                    max = 15.0
                    msg = "\n注意: 在难度选择时，请优先采用适合本段位的等级最高的难度，若紫、白谱面难度相同，优先采用紫谱。"
                else:
                    rand_ranking.send(f"▿ [Sender: {nickname}]\n  Rank Error\n寄，Master 等级只有初级、中级、上级、超上级！")
                    return
            else:
                rand_ranking.send(f"▿ [Sender: {nickname}]\n  Rank Error\n寄，大等级只有Master、Expert！")
                return
            if len(argv) > 3 and argv[2] == "计算":
                if len(argv) > 7:
                    raise ValueError
                else:
                    if len(argv) == 6:
                        mylife = life + (int(argv[3]) * gr) + (int(argv[4]) * gd) + (int(argv[5]) * miss)
                        if mylife <= 0:
                            await rand_ranking.send(f"▿ [Sender: {nickname}]\n  段位闯关失败\n寄，您的血量扣光了......{argv[0]} {argv[1]}段位不合格！")
                            return
                        else:
                            mylife += clear
                            if mylife > life:
                                mylife = life
                            await rand_ranking.send(f"▾ [Sender: {nickname}]\n  段位血量\n您还剩余 {mylife} 血！如果没闯到第四首就请继续加油吧！")
                            return
                    elif len(argv) == 7:
                        mylife = int(argv[6]) + (int(argv[3]) * gr) + (int(argv[4]) * gd) + (int(argv[5]) * miss)
                        if mylife <= 0:
                            await rand_ranking.send(f"▿ [Sender: {nickname}]\n  段位闯关失败\n寄，您的血量扣光了......{argv[0]} {argv[1]}段位不合格！")
                            return
                        else:
                            mylife += clear
                            if mylife > life:
                                mylife = life
                            await rand_ranking.send(f"▾ [Sender: {nickname}]\n  段位血量\n您还剩余 {mylife} 血！如果没闯到第四首就请继续加油吧！")
                            return
                    else:
                        raise ValueError
            else:
                rand_result += f"\n段位难度区间: {min} - {max}\n段位血量规则:\nLife: {life} -> Clear: +{clear}\nGreat: {gr} Good: {gd} Miss: {miss}\n"
                rand_result += msg
                for i in range(4):
                    music_data = total_list.filter(level=level, type=["SD", "DX"])
                    rand_result += f'\n----- Track {i + 1} / 4 -----\n' + song_txt(music_data.random())
        await rand_ranking.send(rand_result)
    except Exception as e:
        await rand_ranking.finish(f"▿ [Sender: {nickname}]\n  Rank Mode Error\n语法有错。如果您需要帮助请对我说‘段位模式 帮助’。\n[Exception Occurred]\n{e}")

plate = on_regex(r'^([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽煌舞霸])([極极将舞神者]舞?)进度\s?(.+)?')

@plate.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽煌舞霸])([極极将舞神者]舞?)进度\s?(.+)?"
    res = re.match(regex, str(event.get_message()).lower())
    diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')
    nickname = event.sender.nickname
    mt = event.message_type
    db = get_driver().config.db
    c = await db.cursor()
    if f'{res.groups()[0]}{res.groups()[1]}' == '真将':
        await plate.finish(f"▿ [Sender: {nickname}]\n  Plate Error\n请您注意: 真系 (maimai & maimaiPLUS) 没有真将成就。")
        return
    if not res.groups()[2]:
        if mt == "guild":
            await c.execute(f'select * from gld_table where uid="{event.user_id}"')
            data = await c.fetchone()
            if data is None:
                await plate.send(f"▿ [Sender: {nickname}]\n  Plate - 错误\n在频道内，免输入用户名的前提是需要将您的 QQ 进行绑定。您尚未将您的 QQ 绑定到小犽，请进行绑定或输入用户名再试一次。\n")
                return
            else:
                qq = str(data[0])
                payload = {'qq': qq}
        else:
            qq = str(event.get_user_id())
            payload = {'qq': qq}
    else:
        payload = {'username': res.groups()[2].strip()}
    if res.groups()[0] in ['舞', '霸']:
        payload['version'] = list(set(version for version in plate_to_version.values()))
    elif res.groups()[0] in ['真']:
        payload['version'] = [plate_to_version['真1'], plate_to_version['真2']]
    else:
        payload['version'] = [plate_to_version[res.groups()[0]]]
    player_data, success = await get_player_plate(payload)
    if success == 400:
        await plate.send(f"▿ [Sender: {nickname}]\n  Plate - 错误\n您输入的玩家 ID 没有找到。\n请检查一下您的用户名是否输入正确或有无注册查分器系统？如您没有输入ID，请检查您的QQ是否与查分器绑定正确。\n若需要确认设置，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/")
    elif success == 403:
        await plate.send(f'▿ [Sender: {nickname}]\n  Plate - 被禁止\n{username} 不允许使用此方式查询牌子进度。\n如果是您的账户，请检查您的QQ是否与查分器绑定正确后，不输入用户名再试一次。\n您需要修改查分器设置吗？请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/')
    else:
        song_played = []
        song_remain_expert = []
        song_remain_master = []
        song_remain_re_master = []
        song_remain_difficult = []
        if res.groups()[1] in ['将', '者']:
            for song in player_data['verlist']:
                if song['level_index'] == 2 and song['achievements'] < (100.0 if res.groups()[1] == '将' else 80.0):
                    song_remain_expert.append([song['id'], song['level_index']])
                if song['level_index'] == 3 and song['achievements'] < (100.0 if res.groups()[1] == '将' else 80.0):
                    song_remain_master.append([song['id'], song['level_index']])
                if res.groups()[0] in ['舞', '霸'] and song['level_index'] == 4 and song['achievements'] < (100.0 if res.groups()[1] == '将' else 80.0):
                    song_remain_re_master.append([song['id'], song['level_index']])
                song_played.append([song['id'], song['level_index']])
        elif res.groups()[1] in ['極', '极']:
            for song in player_data['verlist']:
                if song['level_index'] == 2 and not song['fc']:
                    song_remain_expert.append([song['id'], song['level_index']])
                if song['level_index'] == 3 and not song['fc']:
                    song_remain_master.append([song['id'], song['level_index']])
                if res.groups()[0] == '舞' and song['level_index'] == 4 and not song['fc']:
                    song_remain_re_master.append([song['id'], song['level_index']])
                song_played.append([song['id'], song['level_index']])
        elif res.groups()[1] == '舞舞':
            for song in player_data['verlist']:
                if song['level_index'] == 2 and song['fs'] not in ['fsd', 'fsdp']:
                    song_remain_expert.append([song['id'], song['level_index']])
                if song['level_index'] == 3 and song['fs'] not in ['fsd', 'fsdp']:
                    song_remain_master.append([song['id'], song['level_index']])
                if res.groups()[0] == '舞' and song['level_index'] == 4 and song['fs'] not in ['fsd', 'fsdp']:
                    song_remain_re_master.append([song['id'], song['level_index']])
                song_played.append([song['id'], song['level_index']])
        elif res.groups()[1] == "神":
            for song in player_data['verlist']:
                if song['level_index'] == 2 and song['fc'] not in ['ap', 'app']:
                    song_remain_expert.append([song['id'], song['level_index']])
                if song['level_index'] == 3 and song['fc'] not in ['ap', 'app']:
                    song_remain_master.append([song['id'], song['level_index']])
                if res.groups()[0] == '舞' and song['level_index'] == 4 and song['fc'] not in ['ap', 'app']:
                    song_remain_re_master.append([song['id'], song['level_index']])
                song_played.append([song['id'], song['level_index']])
        total_music_num = 0
        for music in total_list:
            if music.version in payload['version']:
                total_music_num += 1
                if [int(music.id), 2] not in song_played:
                    song_remain_expert.append([int(music.id), 2])
                if [int(music.id), 3] not in song_played:
                    song_remain_master.append([int(music.id), 3])
                if res.groups()[0] in ['舞', '霸'] and len(music.level) == 5 and [int(music.id), 4] not in song_played:
                    song_remain_re_master.append([int(music.id), 4])
        song_remain_expert = sorted(song_remain_expert, key=lambda i: int(i[0]))
        song_remain_master = sorted(song_remain_master, key=lambda i: int(i[0]))
        song_remain_re_master = sorted(song_remain_re_master, key=lambda i: int(i[0]))
        for song in song_remain_expert + song_remain_master + song_remain_re_master:
            music = total_list.by_id(str(song[0]))
            if music.ds[song[1]] > 13.6:
                try:
                    song_remain_difficult.append([music.id, music.title, diffs[song[1]], music.ds[song[1]], music.stats[song[1]].difficulty, song[1]])
                except:
                    song_remain_difficult.append([music.id, music.title, "--", music.ds[song[1]], music.stats[song[1]].difficulty, song[1]])
        expcomplete = 100 - (len(song_remain_expert) / total_music_num * 100)
        mascomplete = 100 - (len(song_remain_master) / total_music_num * 100)
        msg = f'''▾ [Sender: {nickname}]\n  {res.groups()[0]}{res.groups()[1]}当前进度\n{"您" if not res.groups()[2] else res.groups()[2]}的剩余歌曲数量如下：
Expert | 已完成 {expcomplete:.2f}%, 待完成 {len(song_remain_expert)} 首 / 共 {total_music_num} 首
Master | 已完成 {mascomplete:.2f}%, 待完成 {len(song_remain_master)} 首 / 共 {total_music_num} 首
'''
        song_remain = song_remain_expert + song_remain_master + song_remain_re_master
        song_record = [[s['id'], s['level_index']] for s in player_data['verlist']]
        if res.groups()[0] in ['舞', '霸']:
            remascomplete = 100 - (len(song_remain_re_master) / 79 * 100)
            msg += f'Re:Master | 已完成 {remascomplete:.2f}%, 待完成 {len(song_remain_re_master)} 首 / 共 79 首\n'
        if len(song_remain_difficult) > 0:
            if len(song_remain_difficult) < 11:
                if res.groups()[0] in ['真']:
                    msg += "\n注意: 真系不需要游玩ジングルベル(以下简称\"圣诞歌\")。受技术限制，真系查询仍包括圣诞歌，您可以忽略此歌曲。如您的真系进度只剩下圣诞歌，则您已达成条件。但您若需要在B40/B50查询时显示此牌子，您仍需完成圣诞歌。\n"
                elif res.groups()[0] in ['熊'] or res.groups()[0] in ['华', '華']:
                    msg += "\n此功能对应牌子遵循的版本为日版，国行版本中，完成版本 舞萌DX 分类内的歌曲可同时获得熊、华两牌。"
                elif res.groups()[0] in ['爽'] or res.groups()[0] in ['煌']:
                    msg += "\n此功能对应牌子遵循的版本为日版，国行版本中，完成版本 舞萌DX2021 分类内的歌曲可同时获得熊、华两牌。"
                msg += '\n剩余重点歌曲（>= 13.7）：\n'
                for s in sorted(song_remain_difficult, key=lambda i: i[3]):
                    self_record = ''
                    if [int(s[0]), s[-1]] in song_record:
                        record_index = song_record.index([int(s[0]), s[-1]])
                        if res.groups()[1] in ['将', '者']:
                            self_record = str(player_data['verlist'][record_index]['achievements']) + '%'
                        elif res.groups()[1] in ['極', '极', '神']:
                            if player_data['verlist'][record_index]['fc']:
                                self_record = comboRank[combo_rank.index(player_data['verlist'][record_index]['fc'])].upper()
                        elif res.groups()[1] == '舞舞':
                            if player_data['verlist'][record_index]['fs']:
                                self_record = syncRank[sync_rank.index(player_data['verlist'][record_index]['fs'])].upper()
                    if res.groups()[0] in ['真'] and s[0] == 70:
                        continue
                    msg += f'Track {s[0]} > {s[1]} | {s[2]}\n定数: {s[3]} 相对难度: {s[4]} {"当前达成率: " if self_record else ""}{self_record}'.strip() + '\n\n'
            else: msg += f'还有 {len(song_remain_difficult)} 个等级是 13+ 及以上的谱面，加油推分吧！\n'
        elif len(song_remain) > 0:
            if len(song_remain) < 11:
                msg += '\n还有以下剩余重点曲目（>=13.7）：\n'
                for s in sorted(song_remain, key=lambda i: i[3]):
                    m = total_list.by_id(str(s[0]))
                    self_record = ''
                    if [int(s[0]), s[-1]] in song_record:
                        record_index = song_record.index([int(s[0]), s[-1]])
                        if res.groups()[1] in ['将', '者']:
                            self_record = str(player_data['verlist'][record_index]['achievements']) + '%'
                        elif res.groups()[1] in ['極', '极', '神']:
                            if player_data['verlist'][record_index]['fc']:
                                self_record = comboRank[combo_rank.index(player_data['verlist'][record_index]['fc'])].upper()
                        elif res.groups()[1] == '舞舞':
                            if player_data['verlist'][record_index]['fs']:
                                self_record = syncRank[sync_rank.index(player_data['verlist'][record_index]['fs'])].upper()
                    if res.groups()[0] in ['真'] and s[0] == 70:
                        continue
                    msg += f'Track {m.id} > {m.title} | {diffs[s[1]]}\n定数: {m.ds[s[1]]} 相对难度: {m.stats[s[1]].difficulty} {"当前达成率: " if self_record else ""}{self_record}'.strip() + '\n\n'
            else:
                msg += f'{res.groups()[0]}{res.groups()[1]} 已确定！当前已经没有大于 13+ 及其以上的谱面了,加油清谱吧！\n'
        else:
            msg += f'{res.groups()[0]}{res.groups()[1]} 所需的所有歌曲均已达到要求，恭喜 {"您" if not res.groups()[2] else res.groups()[2]} 达成了 {res.groups()[0]}{res.groups()[1]}！'
            if not res.groups()[2]:
                if res.groups()[0] == "真":
                    platever = 0
                elif res.groups()[0] == "超":
                    platever = 1
                elif res.groups()[0] == "檄":
                    platever = 2
                elif res.groups()[0] == "橙":
                    platever = 3
                elif res.groups()[0] == "晓" or res.groups()[0] == "暁":
                    platever = 4
                elif res.groups()[0] == "桃":
                    platever = 5
                elif res.groups()[0] == "樱":
                    platever = 6
                elif res.groups()[0] == "紫":
                    platever = 7
                elif res.groups()[0] == "菫":
                    platever = 8
                elif res.groups()[0] == "白":
                    platever = 9
                elif res.groups()[0] == "雪":
                    platever = 10
                elif res.groups()[0] == "辉":
                    platever = 11
                elif res.groups()[0] == "舞" or res.groups()[0] == "霸":
                    platever = 'X'
                elif res.groups()[0] == "熊":
                    platever = 12
                elif res.groups()[0] == "华":
                    platever = 13
                elif res.groups()[0] == "爽":
                    platever = 14
                elif res.groups()[0] == "煌":
                    platever = 15
                if res.groups()[1] == "极":
                    platetype = 1
                elif res.groups()[1] == "将":
                    platetype = 2
                elif res.groups()[1] == "神":
                    platetype = 3
                elif res.groups()[1] == "舞舞":
                    platetype = 4
                elif res.groups()[1] == "者":
                    platetype = 5
                platenum = f'9{platever}{platetype}'
                await c.execute(f'select * from plate_table where id="{qq}"')
                data = await c.fetchone()
                if data is None:
                    await c.execute(f'insert into plate_table values ({qq}, {platenum})')
                else:
                    await c.execute(f'update plate_table set platenum={platenum} where id={qq}')
                await db.commit()
                msg += '\n您在自主查询 B40 或 B50 时，这个牌子将展现在您的姓名框处。'
        await plate.send(msg.strip())

levelprogress = on_regex(r'^([0-9]+\+?)\s?(.+)进度\s?(.+)?')

@levelprogress.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "([0-9]+\+?)\s?(.+)进度\s?(.+)?"
    res = re.match(regex, str(event.get_message()).lower())
    scoreRank = 'd c b bb bbb a aa aaa s s+ ss ss+ sss sss+'.lower().split(' ')
    levelList = '1 2 3 4 5 6 7 7+ 8 8+ 9 9+ 10 10+ 11 11+ 12 12+ 13 13+ 14 14+ 15'.split(' ')
    comboRank = 'fc fc+ ap ap+'.split(' ')
    combo_rank = 'fc fcp ap app'.split(' ')
    syncRank = 'fs fs+ fdx fdx+'.split(' ')
    sync_rank = 'fs fsp fdx fdxp'.split(' ')
    achievementList = [50.0, 60.0, 70.0, 75.0, 80.0, 90.0, 94.0, 97.0, 98.0, 99.0, 99.5, 100.0, 100.5]
    nickname = event.sender.nickname
    db = get_driver().config.db
    c = await db.cursor()
    mt = event.message_type
    if res.groups()[0] not in levelList:
        await levelprogress.finish(f"▿ [Sender: {nickname}]\n  参数错误\n最低是1，最高是15，您这整了个{res.groups()[0]}......故意找茬的吧？")
        return
    if res.groups()[1] not in scoreRank + comboRank + syncRank:
        await levelprogress.finish(f"▿ [Sender: {nickname}]\n  参数错误\n输入有误。\n1.请不要随便带空格。\n2.等级目前只有D/C/B/BB/BBB/A/AA/AAA/S/S+/SS/SS+/SSS/SSS+\n3.同步相关只有FS/FC/FDX/FDX+/FC/FC+/AP/AP+。")
        return
    if not res.groups()[2]:
        if mt == "guild":
            await c.execute(f'select * from gld_table where uid="{event.user_id}"')
            data = await c.fetchone()
            if data is None:
                await levelprogress.send(f"▿ [Sender: {nickname}]\n  等级清谱查询 - 错误\n在频道内，免输入用户名的前提是需要将您的 QQ 进行绑定。您尚未将您的 QQ 绑定到小犽，请进行绑定或输入用户名再试一次。\n")
                return
            else:
                payload = {'qq': str(data[0])}
        else:
            payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': res.groups()[2].strip()}
    payload['version'] = list(set(version for version in plate_to_version.values()))
    player_data, success = await get_player_plate(payload)
    if success == 400:
        await levelprogress.send(f"▿ [Sender: {nickname}]\n  等级清谱查询 - 错误\n您输入的玩家 ID 没有找到。\n请检查一下您的用户名是否输入正确或有无注册查分器系统？如您没有输入ID，请检查您的QQ是否与查分器绑定正确。\n若需要确认设置，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/")
        return
    elif success == 403:
        await levelprogress.send(f'▿ [Sender: {nickname}]\n  等级清谱查询 - 被禁止\n{username} 不允许使用此方式查询牌子进度。\n如果是您的账户，请检查您的QQ是否与查分器绑定正确后，不输入用户名再试一次。\n您需要修改查分器设置吗？请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/')
        return
    else:
        song_played = []
        song_remain = []
        if res.groups()[1].lower() in scoreRank:
            achievement = achievementList[scoreRank.index(res.groups()[1].lower()) - 1]
            for song in player_data['verlist']:
                if song['level'] == res.groups()[0] and song['achievements'] < achievement:
                    song_remain.append([song['id'], song['level_index']])
                song_played.append([song['id'], song['level_index']])
        elif res.groups()[1].lower() in comboRank:
            combo_index = comboRank.index(res.groups()[1].lower())
            for song in player_data['verlist']:
                if song['level'] == res.groups()[0] and ((song['fc'] and combo_rank.index(song['fc']) < combo_index) or not song['fc']):
                    song_remain.append([song['id'], song['level_index']])
                song_played.append([song['id'], song['level_index']])
        elif res.groups()[1].lower() in syncRank:
            sync_index = syncRank.index(res.groups()[1].lower())
            for song in player_data['verlist']:
                if song['level'] == res.groups()[0] and ((song['fs'] and sync_rank.index(song['fs']) < sync_index) or not song['fs']):
                    song_remain.append([song['id'], song['level_index']])
                song_played.append([song['id'], song['level_index']])
        for music in total_list:
            for i, lv in enumerate(music.level[2:]):
                if lv == res.groups()[0] and [int(music.id), i + 2] not in song_played:
                    song_remain.append([int(music.id), i + 2])
        song_remain = sorted(song_remain, key=lambda i: int(i[1]))
        song_remain = sorted(song_remain, key=lambda i: int(i[0]))
        songs = []
        for song in song_remain:
            music = total_list.by_id(str(song[0]))
            try:
                songs.append([music.id, music.title, diffs[song[1]], music.ds[song[1]], music.stats[song[1]].difficulty, song[1]])
            except:
                songs.append([music.id, music.title, "--", music.ds[song[1]], music.stats[song[1]].difficulty, song[1]])
        msg = ''
        if len(song_remain) > 0:
            if len(song_remain) < 50:
                song_record = [[s['id'], s['level_index']] for s in player_data['verlist']]
                msg += f'▼ [Sender: {nickname}]\n  清谱进度\n以下是 {"您" if not res.groups()[2] else res.groups()[2]} 的 Lv.{res.groups()[0]} 全谱面 {res.groups()[1].upper()} 的剩余曲目：\n'
                for s in sorted(songs, key=lambda i: i[3]):
                    self_record = ''
                    if [int(s[0]), s[-1]] in song_record:
                        record_index = song_record.index([int(s[0]), s[-1]])
                        if res.groups()[1].lower() in scoreRank:
                            self_record = str(player_data['verlist'][record_index]['achievements']) + '%'
                        elif res.groups()[1].lower() in comboRank:
                            if player_data['verlist'][record_index]['fc']:
                                self_record = comboRank[combo_rank.index(player_data['verlist'][record_index]['fc'])].upper()
                        elif res.groups()[1].lower() in syncRank:
                            if player_data['verlist'][record_index]['fs']:
                                self_record = syncRank[sync_rank.index(player_data['verlist'][record_index]['fs'])].upper()
                    if self_record == "":
                        self_record = "暂无"
                    msg += f'Track {s[0]} > {s[1]} | {s[2]}\nBase: {s[3]} 相对难度: {s[4]} 当前达成率: {self_record}'.strip() + '\n\n'
            else:
                await levelprogress.finish(f'▾ [Sender: {nickname}]\n  清谱进度\n{"您" if not res.groups()[2] else res.groups()[2]} 还有 {len(song_remain)} 首 Lv.{res.groups()[0]} 的曲目还没有达成 {res.groups()[1].upper()},加油推分吧！')
        else:
            await levelprogress.finish(f'▾ [Sender: {nickname}]\n  清谱完成\n恭喜 {"您" if not res.groups()[2] else res.groups()[2]} 达成 Lv.{res.groups()[0]} 全谱面 {res.groups()[1].upper()}！')
        await levelprogress.send(MessageSegment.image(f"base64://{image_to_base64(text_to_image(msg.strip())).decode()}"))

rankph = on_command('查看排行', aliases={'查看排名'})

@rankph.handle()
async def _(bot: Bot, event: Event, state: T_State):
    async with aiohttp.request("GET", "https://www.diving-fish.com/api/maimaidxprober/rating_ranking") as resp:
        rank_data = await resp.json()
        msg = f'▾ Rating TOP50 排行榜\n截止 {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}，Diving-Fish 查分器网站已注册用户 Rating 排行：\n'
        for i, ranker in enumerate(sorted(rank_data, key=lambda r: r['ra'], reverse=True)[:50]):
            msg += f'TOP {i + 1}> {ranker["username"]}  DX Rating:{ranker["ra"]}\n'
        await rankph.send(MessageSegment.image(f"base64://{image_to_base64(text_to_image(msg.strip())).decode()}"))


rise_score = on_regex(r'^我要在?([0-9]+\+?)?上([0-9]+)分\s?(.+)?')

@rise_score.handle()
async def _(bot: Bot, event: Event, state: T_State):
    mt = event.message_type
    regex = "我要在?([0-9]+\+?)?上([0-9]+)分\s?(.+)?"
    res = re.match(regex, str(event.get_message()).lower())
    scoreRank = 'd c b bb bbb a aa aaa s s+ ss ss+ sss sss+'.lower().split(' ')
    levelList = '1 2 3 4 5 6 7 7+ 8 8+ 9 9+ 10 10+ 11 11+ 12 12+ 13 13+ 14 14+ 15'.split(' ')
    comboRank = 'fc fc+ ap ap+'.split(' ')
    combo_rank = 'fc fcp ap app'.split(' ')
    syncRank = 'fs fs+ fdx fdx+'.split(' ')
    sync_rank = 'fs fsp fdx fdxp'.split(' ')
    achievementList = [50.0, 60.0, 70.0, 75.0, 80.0, 90.0, 94.0, 97.0, 98.0, 99.0, 99.5, 100.0, 100.5]
    nickname = event.sender.nickname
    db = get_driver().config.db
    c = await db.cursor()
    if res.groups()[0] and res.groups()[0] not in levelList:
        await rise_score.finish(f"▿ [Sender: {nickname}]\n  参数错误\n最低是1，最高是15，您这整了个{res.groups()[0]}......故意找茬的吧？")
        return
    if not res.groups()[2]:
        if mt == "guild":
            await c.execute(f'select * from gld_table where uid="{event.user_id}"')
            data = await c.fetchone()
            if data is None:
                await rise_score.send(f"▿ [Sender: {nickname}]\n  犽的锦囊 - 错误\n在频道内，免输入用户名的前提是需要将您的 QQ 进行绑定。您尚未将您的 QQ 绑定到小犽，请进行绑定或输入用户名再试一次。\n")
                return
            else:
                payload = {'qq': str(data[0])}
        else:
            payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': res.groups()[2].strip()}
    player_data, success = await get_player_data(payload)
    if success == 400:
        await rise_score.send(f"▿ [Sender: {nickname}]\n  犽的锦囊 - 错误\n您输入的玩家 ID 没有找到。\n请检查一下您的用户名是否输入正确或有无注册查分器系统？如您没有输入ID，请检查您的QQ是否与查分器绑定正确。\n若需要确认设置，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/")
        return
    elif success == 403:
        await rise_score.send(f'▿ [Sender: {nickname}]\n  犽的锦囊 - 被禁止\n{username} 不允许使用此方式查询。\n如果是您的账户，请检查您的QQ是否与查分器绑定正确后，不输入用户名再试一次。\n您需要修改查分器设置吗？请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/')
        return
    else:
        dx_ra_lowest = 999
        sd_ra_lowest = 999
        player_dx_list = []
        player_sd_list = []
        music_dx_list = []
        music_sd_list = []
        for dx in player_data['charts']['dx']:
            dx_ra_lowest = min(dx_ra_lowest, dx['ra'])
            player_dx_list.append([int(dx['song_id']), int(dx["level_index"]), int(dx['ra'])])
        for sd in player_data['charts']['sd']:
            sd_ra_lowest = min(sd_ra_lowest, sd['ra'])
            player_sd_list.append([int(sd['song_id']), int(sd["level_index"]), int(sd['ra'])])
        player_dx_id_list = [[d[0], d[1]] for d in player_dx_list]
        player_sd_id_list = [[s[0], s[1]] for s in player_sd_list]
        for music in total_list:
            for i, achievement in enumerate(achievementList):
                for j, ds in enumerate(music.ds):
                    if res.groups()[0] and music['level'][j] != res.groups()[0]: continue
                    if music.is_new:
                        music_ra = computeRa(ds, achievement)
                        if music_ra < dx_ra_lowest: continue
                        if [int(music.id), j] in player_dx_id_list:
                            player_ra = player_dx_list[player_dx_id_list.index([int(music.id), j])][2]
                            if music_ra - player_ra == int(res.groups()[1]) and [int(music.id), j, music_ra] not in player_dx_list:
                                music_dx_list.append([music, diffs[j], ds, achievement, scoreRank[i + 1].upper(), music_ra, music.stats[j].difficulty])
                        else:
                            if music_ra - dx_ra_lowest == int(res.groups()[1]) and [int(music.id), j, music_ra] not in player_dx_list:
                                music_dx_list.append([music, diffs[j], ds, achievement, scoreRank[i + 1].upper(), music_ra, music.stats[j].difficulty])
                    else:
                        music_ra = computeRa(ds, achievement)
                        if music_ra < sd_ra_lowest: continue
                        if [int(music.id), j] in player_sd_id_list:
                            player_ra = player_sd_list[player_sd_id_list.index([int(music.id), j])][2]
                            if music_ra - player_ra == int(res.groups()[1]) and [int(music.id), j, music_ra] not in player_sd_list:
                                music_sd_list.append([music, diffs[j], ds, achievement, scoreRank[i + 1].upper(), music_ra, music.stats[j].difficulty])
                        else:
                            if music_ra - sd_ra_lowest == int(res.groups()[1]) and [int(music.id), j, music_ra] not in player_sd_list:
                                music_sd_list.append([music, diffs[j], ds, achievement, scoreRank[i + 1].upper(), music_ra, music.stats[j].difficulty])
        if len(music_dx_list) == 0 and len(music_sd_list) == 0:
            await rise_score.send(f"▿ [Sender: {nickname}]\n  犽的锦囊 - 无匹配乐曲\n没有找到这样的乐曲。")
            return
        elif len(music_dx_list) + len(music_sd_list) > 60:
            await rise_score.send(f"▿ [Sender: {nickname}]\n  犽的锦囊 - 结果过多\n结果太多啦...一共我查到{len(res)} 条符合条件的歌!\n缩小一下查询范围吧。")
            return
        msg = f'▼ [Sender: {nickname}]\n  犽的锦囊 - 升 {res.groups()[1]} 分攻略\n'
        if len(music_sd_list) != 0:
            msg += f'----- B25 区域升分推荐 (旧版本乐曲) -----\n'
            for music, diff, ds, achievement, rank, ra, difficulty in sorted(music_sd_list, key=lambda i: int(i[0]['id'])):
                msg += f'Track {music["id"]}> {music["title"]} | {diff}\n定数: {ds} 要求的达成率: {achievement} 分数线: {rank} Rating: {ra} 相对难度: {difficulty}\n\n'
        if len(music_dx_list) != 0:
            msg += f'----- B15 区域升分推荐 (当前版本乐曲) -----\n'
            for music, diff, ds, achievement, rank, ra, difficulty in sorted(music_dx_list, key=lambda i: int(i[0]['id'])):
                msg += f'Track {music["id"]}> {music["title"]} | {diff}\n定数: {ds} 要求的达成率: {achievement} 分数线: {rank} Rating: {ra} 相对难度: {difficulty}\n\n'
        await rise_score.send(MessageSegment.image(f"base64://{image_to_base64(text_to_image(msg.strip())).decode()}"))

base = on_command("底分分析", aliases={"rating分析"})

@base.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = str(event.get_message()).strip()
    nickname = event.sender.nickname
    db = get_driver().config.db
    c = await db.cursor()
    mt = event.message_type
    if username == "":
        if mt == "guild":
            await c.execute(f'select * from gld_table where uid="{event.user_id}"')
            data = await c.fetchone()
            if data is None:
                await base.send(f"▿ [Sender: {nickname}]\n  底分分析 - 错误\n在频道内，免输入用户名的前提是需要将您的 QQ 进行绑定。您尚未将您的 QQ 绑定到小犽，请进行绑定或输入用户名再试一次。\n")
                return
            else:
                payload = {'qq': str(data[0])}
                name = "您"
        else:
            payload = {'qq': str(event.get_user_id())}
            name = "您"
    else:
        payload = {'username': username}
        name = username
    obj, success = await get_player_data(payload)
    if success == 400:
        await base.send(f"▿ [Sender: {nickname}]\n  底分分析 - 错误\n您输入的玩家 ID 没有找到。\n请检查一下您的用户名是否输入正确或有无注册查分器系统？如您没有输入ID，请检查您的QQ是否与查分器绑定正确。\n若需要确认设置，请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/")
        return
    elif success == 403:
        await base.send(f'▿ [Sender: {nickname}]\n  底分分析 - 被禁止\n{username} 不允许使用此方式查询。\n如果是您的账户，请检查您的QQ是否与查分器绑定正确后，不输入用户名再试一次。\n您需要修改查分器设置吗？请参阅:\nhttps://www.diving-fish.com/maimaidx/prober/')
        return
    else:
        try:
            sd_best = BestList(25)
            dx_best = BestList(15)
            dx: List[Dict] = obj["charts"]["dx"]
            sd: List[Dict] = obj["charts"]["sd"]
            for c in sd:
                sd_best.push(ChartInfo.from_json(c))
            for c in dx:
                dx_best.push(ChartInfo.from_json(c))
            sd_best_max_sc = sd_best[0].ra
            ds_sd_best_max = sd_best[0].ds
            ds_sd_best_min = sd_best[len(sd_best) - 1].ds
            sd_best_min_sc = sd_best[len(sd_best) - 1].ra
            dx_best_max_sc = dx_best[0].ra
            ds_dx_best_max = dx_best[0].ds
            ds_dx_best_min = dx_best[len(dx_best) - 1].ds
            dx_best_min_sc = dx_best[len(dx_best) - 1].ra
            maxuse = 0
            minuse = 0
            maxuse_dx = 0
            minuse_dx = 0
            if sd_best[0].achievement >= 100.5:
                max_sssp = ds_sd_best_max
            elif sd_best[0].achievement < 100.5 and sd_best[0].achievement >= 100:
                max_sss = ds_sd_best_max
                maxuse = 1
            elif sd_best[0].achievement < 100 and sd_best[0].achievement >= 99.5:
                max_ssp = ds_sd_best_max
                maxuse = 2
            elif sd_best[0].achievement < 99.5 and sd_best[0].achievement >= 99:
                max_ss = ds_sd_best_max
                maxuse = 3
            elif sd_best[0].achievement < 99 and sd_best[0].achievement >= 98:
                max_sp = ds_sd_best_max
                maxuse = 4
            elif sd_best[0].achievement < 98 and sd_best[0].achievement >= 97:
                max_s = ds_sd_best_max
                maxuse = 5
            else:
                raise ValueError("请您注意: 此账号 Best 40 B25 中最高达成率小于 Rank S的要求。请继续加油！")
            if sd_best[len(sd_best) - 1].achievement >= 100.5:
                min_sssp = ds_sd_best_min
            elif sd_best[len(sd_best) - 1].achievement < 100.5 and sd_best[len(sd_best) - 1].achievement >= 100:
                min_sss = ds_sd_best_min
                minuse = 1
            elif sd_best[len(sd_best) - 1].achievement < 100 and sd_best[len(sd_best) - 1].achievement >= 99.5:
                min_ssp = ds_sd_best_min
                minuse = 2
            elif sd_best[len(sd_best) - 1].achievement < 99.5 and sd_best[len(sd_best) - 1].achievement >= 99:
                min_ss = ds_sd_best_min
                minuse = 3
            elif sd_best[len(sd_best) - 1].achievement < 99 and sd_best[len(sd_best) - 1].achievement >= 98:
                min_sp = ds_sd_best_min
                minuse = 4
            elif sd_best[len(sd_best) - 1].achievement < 98 and sd_best[len(sd_best) - 1].achievement >= 97:
                min_s = ds_sd_best_min
                minuse = 5
            else:
                raise ValueError("请您注意: 此账号 Best 40 B25 中最低达成率小于 Rank S的要求。请继续加油！")
            if maxuse == 0:
                max_sss = max_sssp + 0.6
                max_ssp = max_sssp + 1
                max_ss = max_sssp + 1.2
                max_sp = max_sssp + 1.7
                max_s = max_sssp + 1.9
            elif maxuse == 1:
                max_sssp = max_sss - 0.6
                max_ssp = max_sss + 0.4
                max_ss = max_sss + 0.6
                max_sp = max_sss + 1.1
                max_s = max_sss + 1.3
            elif maxuse == 2:
                max_sssp = max_ssp - 1
                max_sss = max_ssp - 0.4
                max_ss = max_ssp + 0.2
                max_sp = max_ssp + 0.7
                max_s = max_ssp + 0.9
            elif maxuse == 3:
                max_sssp = max_ss - 1.2
                max_sss = max_ss - 0.6
                max_ssp = max_ss - 0.2
                max_sp = max_ss + 0.5
                max_s = max_ss + 0.7
            elif maxuse == 4:
                max_sssp = max_sp - 1.7
                max_sss = max_sp - 1.1
                max_ssp = max_sp - 0.7
                max_ss = max_sp - 0.5
                max_s = max_sp + 0.2
            else:
                max_sssp = max_s - 1.9
                max_sss = max_s - 1.3
                max_ssp = max_s - 0.9
                max_ss = max_s - 0.7
                max_sp = max_s - 0.2
            if minuse == 0:
                min_sss = min_sssp + 0.6
                min_ssp = min_sssp + 1
                min_ss = min_sssp + 1.2
                min_sp = min_sssp + 1.7
                min_s = min_sssp + 1.9
            elif minuse == 1:
                min_sssp = min_sss - 0.6
                min_ssp = min_sss + 0.4
                min_ss = min_sss + 0.6
                min_sp = min_sss + 1.1
                min_s = min_sss + 1.3
            elif minuse == 2:
                min_sssp = min_ssp - 1
                min_sss = min_ssp - 0.4
                min_ss = min_ssp + 0.2
                min_sp = min_ssp + 0.7
                min_s = min_ssp + 0.9
            elif minuse == 3:
                min_sssp = min_ss - 1.2
                min_sss = min_ss - 0.6
                min_ssp = min_ss - 0.2
                min_sp = min_ss + 0.5
                min_s = min_ss + 0.7
            elif minuse == 4:
                min_sssp = min_sp - 1.7
                min_sss = min_sp - 1.1
                min_ssp = min_sp - 0.7
                min_ss = min_sp - 0.5
                min_s = min_sp + 0.2
            else:
                min_sssp = min_s - 1.9
                min_sss = min_s - 1.3
                min_ssp = min_s - 0.9
                min_ss = min_s - 0.7
                min_sp = min_s - 0.2
            if dx_best[0].achievement >= 100.5:
                max_sssp_dx = ds_dx_best_max
            elif dx_best[0].achievement < 100.5 and dx_best[0].achievement >= 100:
                max_sss_dx = ds_dx_best_max
                maxuse_dx = 1
            elif dx_best[0].achievement < 100 and dx_best[0].achievement >= 99.5:
                max_ssp_dx = ds_dx_best_max
                maxuse_dx = 2
            elif dx_best[0].achievement < 99.5 and dx_best[0].achievement >= 99:
                max_ss_dx = ds_dx_best_max
                maxuse_dx = 3
            elif dx_best[0].achievement < 99 and dx_best[0].achievement >= 98:
                max_sp_dx = ds_dx_best_max
                maxuse_dx = 4
            elif dx_best[0].achievement < 98 and dx_best[0].achievement >= 97:
                max_s_dx = ds_dx_best_max
                maxuse_dx = 5
            else:
                raise ValueError("请您注意: 此账号 Best 40 B15 中最高达成率小于 Rank S的要求。请继续加油！")
            if dx_best[len(dx_best) - 1].achievement >= 100.5:
                min_sssp_dx = ds_dx_best_min
            elif dx_best[len(dx_best) - 1].achievement < 100.5 and dx_best[len(dx_best) - 1].achievement >= 100:
                min_sss_dx = ds_dx_best_min
                minuse_dx = 1
            elif dx_best[len(dx_best) - 1].achievement < 100 and dx_best[len(dx_best) - 1].achievement >= 99.5:
                min_ssp_dx = ds_dx_best_min
                minuse_dx = 2
            elif dx_best[len(dx_best) - 1].achievement < 99.5 and dx_best[len(dx_best) - 1].achievement >= 99:
                min_ss_dx = ds_dx_best_min
                minuse_dx = 3
            elif dx_best[len(dx_best) - 1].achievement < 99 and dx_best[len(dx_best) - 1].achievement >= 98:
                min_sp_dx = ds_dx_best_min
                minuse_dx = 4
            elif dx_best[len(dx_best) - 1].achievement < 98 and dx_best[len(dx_best) - 1].achievement >= 97:
                min_s_dx = ds_dx_best_min
                minuse_dx = 5
            else:
                raise ValueError("请您注意: 此账号 Best 40 B15 中最低达成率小于 Rank S 的要求。请继续加油！")
            if maxuse_dx == 0:
                max_sss_dx = max_sssp_dx + 0.6
                max_ssp_dx = max_sssp_dx + 1
                max_ss_dx = max_sssp_dx + 1.2
                max_sp_dx = max_sssp_dx + 1.7
                max_s_dx = max_sssp_dx + 1.9
            elif maxuse_dx == 1:
                max_sssp_dx = max_sss_dx - 0.6
                max_ssp_dx = max_sss_dx + 0.4
                max_ss_dx = max_sss_dx + 0.6
                max_sp_dx = max_sss_dx + 1.1
                max_s_dx = max_sss_dx + 1.3
            elif maxuse_dx == 2:
                max_sssp_dx = max_ssp_dx - 1
                max_sss_dx = max_ssp_dx - 0.4
                max_ss_dx = max_ssp_dx + 0.2
                max_sp_dx = max_ssp_dx + 0.7
                max_s_dx = max_ssp_dx + 0.9
            elif maxuse_dx == 3:
                max_sssp_dx = max_ss_dx - 1.2
                max_sss_dx = max_ss_dx - 0.6
                max_ssp_dx = max_ss_dx - 0.2
                max_sp_dx = max_ss_dx + 0.5
                max_s_dx = max_ss_dx + 0.7
            elif maxuse_dx == 4:
                max_sssp_dx = max_sp_dx - 1.7
                max_sss_dx = max_sp_dx - 1.1
                max_ssp_dx = max_sp_dx - 0.7
                max_ss_dx = max_sp_dx - 0.5
                max_s_dx = max_sp_dx + 0.2
            else:
                max_sssp_dx = max_s_dx - 1.9
                max_sss_dx = max_s_dx - 1.3
                max_ssp_dx = max_s_dx - 0.9
                max_ss_dx = max_s_dx - 0.7
                max_sp_dx = max_s_dx - 0.2
            if minuse_dx == 0:
                min_sss_dx = min_sssp_dx + 0.6
                min_ssp_dx = min_sssp_dx + 1
                min_ss_dx = min_sssp_dx + 1.2
                min_sp_dx = min_sssp_dx + 1.7
                min_s_dx = min_sssp_dx + 1.9
            elif minuse_dx == 1:
                min_sssp_dx = min_sss_dx - 0.6
                min_ssp_dx = min_sss_dx + 0.4
                min_ss_dx = min_sss_dx + 0.6
                min_sp_dx = min_sss_dx + 1.1
                min_s_dx = min_sss_dx + 1.3
            elif minuse_dx == 2:
                min_sssp_dx = min_ssp_dx - 1
                min_sss_dx = min_ssp_dx - 0.4
                min_ss_dx = min_ssp_dx + 0.2
                min_sp_dx = min_ssp_dx + 0.7
                min_s_dx = min_ssp_dx + 0.9
            elif minuse_dx == 3:
                min_sssp_dx = min_ss_dx - 1.2
                min_sss_dx = min_ss_dx - 0.6
                min_ssp_dx = min_ss_dx - 0.2
                min_sp_dx = min_ss_dx + 0.5
                min_s_dx = min_ss_dx + 0.7
            elif minuse_dx == 4:
                min_sssp_dx = min_sp_dx - 1.7
                min_sss_dx = min_sp_dx - 1.1
                min_ssp_dx = min_sp_dx - 0.7
                min_ss_dx = min_sp_dx - 0.5
                min_s_dx = min_sp_dx + 0.2
            else:
                min_sssp_dx = min_s_dx - 1.9
                min_sss_dx = min_s_dx - 1.3
                min_ssp_dx = min_s_dx - 0.9
                min_ss_dx = min_s_dx - 0.7
                min_sp_dx = min_s_dx - 0.2
            max_sssp = round(max_sssp, 1)
            max_sss = round(max_sss, 1)
            max_ssp = round(max_ssp, 1)
            max_ss = round(max_ss, 1)
            max_sp = round(max_sp, 1)
            max_s = round(max_s, 1)
            min_sssp = round(min_sssp, 1)
            min_sss = round(min_sss, 1)
            min_ssp = round(min_ssp, 1)
            min_ss = round(min_ss, 1)
            min_sp = round(min_sp, 1)
            min_s = round(min_s, 1)
            max_sssp_dx = round(max_sssp_dx, 1)
            max_sss_dx = round(max_sss_dx, 1)
            max_ssp_dx = round(max_ssp_dx, 1)
            max_ss_dx = round(max_ss_dx, 1)
            max_sp_dx = round(max_sp_dx, 1)
            max_s_dx = round(max_s_dx, 1)
            min_sssp_dx = round(min_sssp_dx, 1)
            min_sss_dx = round(min_sss_dx, 1)
            min_ssp_dx = round(min_ssp_dx, 1)
            min_ss_dx = round(min_ss_dx, 1)
            min_sp_dx = round(min_sp_dx, 1)
            min_s_dx = round(min_s_dx, 1)
            if max_sssp > 15.0 or max_sssp < 1.0:
                max_sssp = ""
            if max_ssp > 15.0 or max_ssp < 1.0:
                max_ssp = ""
            if max_sp > 15.0 or max_sp < 1.0:
                max_sp = ""
            if max_sss > 15.0 or max_sss < 1.0:
                max_sss = ""
            if max_ss > 15.0 or max_ss < 1.0:
                max_ss = ""
            if max_s > 15.0 or max_s < 1.0:
                max_s = ""
            if min_sssp > 15.0 or min_sssp < 1.0:
                min_sssp = ""
            if min_ssp > 15.0 or min_ssp < 1.0:
                min_ssp = ""
            if min_sp > 15.0 or min_sp < 1.0:
                min_sp = ""
            if min_sss > 15.0 or min_sss < 1.0:
                min_sss = ""
            if min_ss > 15.0 or min_ss < 1.0:
                min_ss = ""
            if min_s > 15.0 or min_s < 1.0:
                min_s = ""
            if max_sssp_dx > 15.0 or max_sssp_dx < 1.0:
                max_sssp_dx = ""
            if max_ssp_dx > 15.0 or max_ssp_dx < 1.0:
                max_ssp_dx = ""
            if max_sp_dx > 15.0 or max_sp_dx < 1.0:
                max_sp_dx = ""
            if max_sss_dx > 15.0 or max_sss_dx < 1.0:
                max_sss_dx = ""
            if max_ss_dx > 15.0 or max_ss_dx < 1.0:
                max_ss_dx = ""
            if max_s_dx > 15.0 or max_s_dx < 1.0:
                max_s_dx = ""
            if min_sssp_dx > 15.0 or min_sssp_dx < 1.0:
                min_sssp_dx = ""
            if min_ssp_dx > 15.0 or min_ssp_dx < 1.0:
                min_ssp_dx = ""
            if min_sp_dx > 15.0 or min_sp_dx < 1.0:
                min_sp_dx = ""
            if min_sss_dx > 15.0 or min_sss_dx < 1.0:
                min_sss_dx = ""
            if min_ss_dx > 15.0 or min_ss_dx < 1.0:
                min_ss_dx = ""
            if min_s_dx > 15.0 or min_s_dx < 1.0:
                min_s_dx = ""
            if name == "您":
                msg = f"▾ [Sender: {nickname}]\n  Rating | 您的底分分析\n"
            else:
                msg = f"▾ [Sender: {nickname}]\n  Rating | {name}的底分分析\n"
            msg += f"----------------------\nB25> #1: {sd_best_max_sc}  #25: {sd_best_min_sc} \nB15> #1: {dx_best_max_sc}  #15: {dx_best_min_sc} \n----------------------"
            msg += f"\nType | SSS+ | SSS | SS+ | SS\n[B25]\n#1 | {max_sssp}   {max_sss}   {max_ssp}   {max_ss}\n"
            msg += f"#25 | {min_sssp}   {min_sss}   {min_ssp}   {min_ss}\n[B15]\n#1 | {max_sssp_dx}   {max_sss_dx}   {max_ssp_dx}   {max_ss_dx}\n#15 | {min_sssp_dx}   {min_sss_dx}   {min_ssp_dx}   {min_ss_dx}\n"
            msg += f"----------------------\n{name}的历史歌曲中：\n#1 的 Rating 相当于达成"
            if max_sssp != "":
                msg += f" {max_sssp} 的 SSS+"
            if max_sss != "":
                msg += f"、{max_sss} 的 SSS"
            if max_ssp != "":
                msg += f"、{max_ssp} 的 SS+"
            if max_ss != "":
                msg += f"、{max_ss} 的 SS"
            if max_sp != "":
                msg += f"、{max_sp} 的 S+"
            if max_s != "":
                msg += f"、{max_s} 的 S"
            msg += "可获得的 Rating；\n#25 的 Rating 相当于达成"
            if min_sssp != "":
                msg += f" {min_sssp} 的 SSS+"
            if min_sss != "":
                msg += f"、{min_sss} 的 SSS"
            if min_ssp != "":
                msg += f"、{min_ssp} 的 SS+"
            if min_ss != "":
                msg += f"、{min_ss} 的 SS"
            if min_sp != "":
                msg += f"、{min_sp} 的 S+"
            if min_s != "":
                msg += f"、{min_s} 的 S"
            msg += f"可获得的 Rating。\n{name}的当前大版本歌曲中：\n#1 的 Rating 相当于达成"
            if max_sssp_dx != "":
                msg += f" {max_sssp_dx} 的 SSS+"
            if max_sss_dx != "":
                msg += f"、{max_sss_dx} 的 SSS"
            if max_ssp_dx != "":
                msg += f"、{max_ssp_dx} 的 SS+"
            if max_ss_dx != "":
                msg += f"、{max_ss_dx} 的 SS"
            if max_sp_dx != "":
                msg += f"、{max_sp_dx} 的 S+"
            if max_s_dx != "":
                msg += f"、{max_s_dx} 的 S"
            msg += "可获得的 Rating；\n#15 的 Rating 相当于达成"
            if min_sssp_dx != "":
                msg += f" {min_sssp_dx} 的 SSS+"
            if min_sss_dx != "":
                msg += f"、{min_sss_dx} 的 SSS"
            if min_ssp_dx != "":
                msg += f"、{min_ssp_dx} 的 SS+"
            if min_ss_dx != "":
                msg += f"、{min_ss_dx} 的 SS"
            if min_sp_dx != "":
                msg += f"、{min_sp_dx} 的 S+"
            if min_s_dx != "":
                msg += f"、{min_s_dx} 的 S"
            msg += "可获得的 Rating。\n请注意：B15 按照当前大版本的最高等级 (即 15.0) 来表示；如需升分推荐，请移步犽的锦囊。"
            await base.send(msg)
        except Exception as e:
            await base.send(f"▿ [Sender: {nickname}]\n  底分分析 - 错误\n出现意外错误啦。\n[Exception Occurred]\n{e}")
            return
