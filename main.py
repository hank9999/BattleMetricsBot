# -*- encoding : utf-8 -*-

from khl import Bot, Message, Cert
from khl.card import CardMessage, Card, Module, Element, Types
import aiohttp
import datetime
import json

# webhook
# bot = Bot(cert=Cert(token='token', verify_token='verify_token'), port=3000,
#           route='/khl-wh')

# websocket
bot = Bot(token='token')


@bot.command(regex=r'(?:\.|\/|。)(?:搜|查|找)(.+)')
async def look(msg: Message, d: str = ''):
    if d.startswith(' '):
        await check(msg, d[1:], '')
    elif d.find(' ') < 0:
        await check(msg, '', d)
    else:
        game = d[:d.find(' ')].strip()
        name = d[d.find(' '):].strip()
        await check(msg, name, game)


async def reflect(game: str) -> str:
    with open('reflect.json', 'r') as f:
        rt = json.loads(f.read())
    if game in rt:
        return rt[game]
    else:
        return game


async def check(msg: Message, name: str = '', game: str = ''):
    game = await reflect(game.lower())
    name = name.strip()
    log_msg = f"[{datetime.datetime.now().strftime('%m-%d %H:%M:%S')}] {msg.author.username}#{msg.author.identify_num} 查询 {game}:{name}"
    print(log_msg)
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://api.battlemetrics.com/servers?filter[search]={name}&filter[game]={game}') as resp:
            rj = await resp.json()
            if len(rj['data']) == 0:
                await reply(msg, '搜索结果为空')
            elif len(rj['data']) == 1:
                name = rj['data'][0]['attributes']['name']
                players = rj['data'][0]['attributes']['players']
                max_players = rj['data'][0]['attributes']['maxPlayers']
                if 'map' in rj['data'][0]['attributes']['details']:
                    map_name = rj['data'][0]['attributes']['details']['map']
                if rj['data'][0]['attributes']['address'] is not None:
                    address = rj['data'][0]['attributes']['address']
                else:
                    ip = rj['data'][0]['attributes']['ip']
                    port = rj['data'][0]['attributes']['port']
                c = Card()
                c.theme = Types.Theme.WARNING
                c.append(Module.Header(f'{name}'))
                text = ''
                text += f'人数: {players}/{max_players}\n'
                if 'map' in rj['data'][0]['attributes']['details']:
                    text += f'地图: {map_name}\n'
                if rj['data'][0]['attributes']['address'] is not None:
                    text += f'IP: {address}'
                else:
                    text += f'IP: {ip}:{port}'
                c.append(Module.Section(Element.Text(content=text, type=Types.Text.KMD)))
                await reply(msg, CardMessage(c))
            else:
                count = 1
                c = Card()
                c.theme = Types.Theme.INFO
                c.append(Module.Header('查询到多个服务器, 显示前10个'))
                c.append(Module.Divider())
                for i in rj['data']:
                    name = i['attributes']['name']
                    players = i['attributes']['players']
                    max_players = i['attributes']['maxPlayers']
                    if 'map' in i['attributes']['details']:
                        map_name = i['attributes']['details']['map']
                    if i['attributes']['address'] is not None:
                        address = i['attributes']['address']
                    else:
                        ip = i['attributes']['ip']
                        port = i['attributes']['port']
                    c.append(Module.Header(f'{count}:  {name}'))
                    text = ''
                    text += f'人数: {players}/{max_players}\n'
                    if 'map' in i['attributes']['details']:
                        text += f'地图: {map_name}\n'
                    if i['attributes']['address'] is not None:
                        text += f'IP: {address}'
                    else:
                        text += f'IP: {ip}:{port}'
                    c.append(Module.Section(Element.Text(content=text, type=Types.Text.KMD)))
                    c.append(Module.Divider())
                    count += 1
                await reply(msg, CardMessage(c))


async def reply(msg, text):
    await msg.reply(text)


if __name__ == '__main__':
    bot.run()
