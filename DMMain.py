import json
import random
import time
import asyncio
from discord.ext import commands

DB = {}
Match_Data = dict()


Weapon = {'dds': {'Hit': 28, 'useSpec': 25, 'numSpec': 2, 'effect': 'POISON', 'type': 'melee'},
          'whip': {'Hit': 42, 'useSpec': 0, 'numSpec': 1, 'effect': '', 'type': 'melee'},
          'gmaul': {'Hit': 34, 'useSpec': 100, 'numSpec': 3, 'effect': '', 'type': 'melee'},
          'acb': {'Hit': 41, 'useSpec': 0, 'numSpec': 1, 'effect': '', 'type': 'ranged'},
          'barrage': {'Hit': 33, 'useSpec': 0, 'numSpec': 1, 'effect': 'FREEZE', 'type': 'magic'},
          'dbow': {'Hit': 45, 'useSpec': 50, 'numSpec': 2, 'effect': '', 'type': 'ranged'},
          'dclaws': {'Hit': 22, 'useSpec': 50, 'numSpec': 4, 'effect': '', 'type': 'melee'},
          'ags': {'Hit': 76, 'useSpec': 75, 'numSpec': 1, 'effect': '', 'type': 'melee'}}


class Match:
    def __init__(self, serverid, channelid):
        self.server = serverid
        self.channelid = channelid
        self.Turn = 1
        self.Player_1 = Fighter(currentChan(self.server, self.channelid)['Player_1_Name'], currentChan(self.server, self.channelid)['Player_1'], self.server, self.channelid)
        self.Player_2 = Fighter(currentChan(self.server, self.channelid)['Player_2_Name'], currentChan(self.server, self.channelid)['Player_2'], self.server, self.channelid)

        print(self.Player_1.name)
        print(Match_Data)

    def NextTurn(self, attacker, opponent):
        self.Turn = ((self.Turn % 2) + 1)
        #TODO:


class Fighter:
    def __init__(self, name, id, serverid, channelid):
        self.name = name
        self.id = id
        self.HP = 100
        self.Special_Attack_Bar = 100
        self.Food = 2
        self.Runes = 2


        self.poison = ''
        self.frozen = ''
        #TODO: self.Buffs - open a db and find out if they have any items buffing their damage.

        self.server = serverid
        self.channelid = channelid


class MatchManager:
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def test(self, ctx):
        return print(currentChan(ctx.message.server.id, ctx.message.channel.id)['Player_1'])



    @commands.command(pass_context=True, aliases=Weapon.keys())
    async def attack(self, ctx):
        start_time = time.time()

        server = ctx.message.server.id
        channelid = ctx.message.channel.id
        attackerid = ctx.message.author.id
        opponent = ''
        attacker = ''
        check_server(ctx.message.server.id, ctx.message.server.name, ctx.message.channel.id, ctx.message.channel.name, server, channelid)

        if currentChan(server, channelid)['Player_1'] == attackerid and currentChan(server, channelid)['Instance'].Turn == 1:
            opponent = currentChan(server, channelid)['Instance'].Player_2
            attacker = currentChan(server, channelid)['Instance'].Player_1
        elif currentChan(server, channelid)['Player_2'] == attackerid and currentChan(server, channelid)['Instance'].Turn == 2:
            opponent = currentChan(server, channelid)['Instance'].Player_1
            attacker = currentChan(server, channelid)['Instance'].Player_2
        if opponent != '':
            weapon = Weapon[ctx.invoked_with]

            if attacker.frozen == 'FROZEN' and weapon['type'] == 'melee':
                await self.bot.say('You are Frozen and must use a ranged or magic attack!')
                return

            if attacker.Special_Attack_Bar < weapon['useSpec']:
                await self.bot.say('You are out of special attack!')
                return

            await self.WeaponDamage(opponent, attacker, weapon, server, channelid)


            print( time.time() - start_time)
            try:
                currentChan(server, channelid)['Instance'].NextTurn(attacker, opponent)
            except AttributeError as e:
                print('game ended')

    @commands.command(pass_context=True)
    async def dm(self, ctx):
        server_id = ctx.message.server.id
        server_name = ctx.message.server.name
        player_id = ctx.message.author.id
        player_name = ctx.message.author.name
        channel_id = ctx.message.channel.id
        channel_name = ctx.message.channel.name
        check_server(server_id, server_name, channel_id, channel_name, player_id, player_name)

        await self.match_status(server_id, channel_id, player_id, player_name)

    async def match_status(self, server, channelid, player, playername):
        if currentChan(server, channelid)['Player_1'] == '':
            currentChan(server, channelid)['Player_1'] = player
            currentChan(server, channelid)['Player_1_Name'] = playername

            await self.bot.say(
                '{} is waiting for a challenger. Type .dm within 30 seconds to accept'.format(playername))
            await self.accept_timer(server, channelid, playername)

        elif currentChan(server, channelid)['Player_2'] == '':
            currentChan(server, channelid)['Player_2'] = player
            currentChan(server, channelid)['Player_2_Name'] = playername
            currentChan(server, channelid)['Instance'] = Match(server, channelid)
            currentChan(server, channelid)['Instance'].Turn = random.randint(1, 2)

            if currentChan(server, channelid)['Player_1'] == player and currentChan(server, channelid)[
                'Instance'].Turn == 1:
                playersturn = currentChan(server, channelid)['Player_1_Name']

            elif currentChan(server, channelid)['Player_2'] == player and currentChan(server, channelid)['Instance'].Turn == 2:
                playersturn = playername

            await self.bot.say('{} has accepted {}\'s challenge. \n{} makes the first move.'.format(playername, currentChan(server, channelid)['Player_1_Name'], playersturn))

        else:
            return await self.bot.say('There is already a match in progress')

    async def accept_timer(self, server, channelid, challenger_name):

        counter = 0
        while currentChan(server, channelid)['Player_2'] == '':
            counter += 1
            print(counter)
            await asyncio.sleep(1)
            if counter == 30:
                currentChan(server, channelid)['Player_1'] = ''

                await self.bot.say('{}\'s challenge has expired'.format(challenger_name))
                return

    async def WeaponDamage(self, opponent, attacker, weapon, serverid, channelid):
        effect = weapon['effect']
        hit = weapon['Hit']
        amount = weapon['numSpec']
        spec_drain = weapon['useSpec']
        dmg = []
        poisoned = 'no'
        poison_dmg = 0
        #   attacker.Buffs =

        opponent.frozen = ''

        if effect == 'FREEZE':
            if attacker.Runes >=1:
                attacker.Runes -= 1
                freeze = random.randint(0, 2)
                if freeze == 0:
                    opponent.frozen = 'FROZEN'

            else:
                return await self.bot.say('You are out of runes!')
        if opponent.poison == 'POISONED':
            if random.randint(0, 1) == 1:

                poison_dmg = random.randint(3, 6)
                opponent.HP -= poison_dmg

        print(effect, opponent.poison)
        if effect == 'POISON'and opponent.poison == '':
                if random.randint(0, 1) in [0,1]:
                    print('here')
                    opponent.poison = 'POISONED'
                    poisoned = 'yes'


        for i in range(amount):
            dmgx = random.randint(0, hit)
            if dmgx > 0:
                dmg.append(dmgx)

        attacker.Special_Attack_Bar -= spec_drain

        opponent.HP -= sum(dmg)
        if opponent.HP <= 0:
            opponent.HP = 0

        await self.Formatter(opponent, attacker, dmg, poison_dmg, poisoned, serverid, channelid)

        if opponent.HP <= 0:
            await self.MatchEnd(opponent, attacker, serverid, channelid)
        return

    async def MatchEnd(self, opponent, attacker, serverid, channelid):

        # DB = {123456: {'name': 'TestName',
        #                                         'Wins': {}, 'Loses': {},
        #                                         'items': {'Coins': 50000},
        #                                         'equip': {'head': '', 'chest': '', 'cape': '', 'gloves': '',
        #                                                   'legs': '', 'boots': '',
        #                                                   'mainhand': '', 'offhand': ''}}}

        with open('DB.json') as f:
            DB = json.load(f)

        for x in DB.keys():
            if x == opponent.id:
                opponentdb = DB[x]
            if x == attacker.id:
                attackerdb = DB[x]

        if opponent.name in attackerdb['Wins']:
            attackerdb['Wins'][opponent.name] += 1
        if opponent.name not in attackerdb['Wins']:
            attackerdb['Wins'] = {opponent.name: 1}
        if attacker.name in opponentdb['Loses']:
            opponentdb['Loses'][attacker.name] += 1
        if attacker.name not in opponentdb['Loses']:
            opponentdb['Loses'] = {attacker.name: 1}
        [currentChan(serverid, channelid)['Player_1'],
         currentChan(serverid, channelid)['Player_1_Name'],
         currentChan(serverid, channelid)['Player_2'],
         currentChan(serverid, channelid)['Player_2_Name'],
         currentChan(serverid, channelid)['Instance']
         ] = ['', '', '', '', '']

        with open('DB.json', 'w') as f:
            json.dump(DB, f, indent=2)

        return await self.bot.say('\n{} Wins!--- Stat Tracking will be added soon ---- Please message Digbigpig for any feedback'.format(attacker.name))

    async def Formatter(self, opponent, attacker, damage, poison_dmg, poisoned, serverid, channelid):
        global returnmsg
        # TODO: Make emojis for the hpbar

        msg = ''

        print(poisoned)
        if poisoned == 'yes':
            msg += '`{} has been Poisoned!`\n'.format(opponent.name)

        if poison_dmg != 0:
            msg += '`{} has taken {} damage from poison!`\n'.format(opponent.name, poison_dmg)

        if opponent.frozen == 'FROZEN':
            msg += '`{} is Frozen and can only use ranged attacked for 1 turn!!`\n'.format(opponent.name)

        if damage:
            damagelist = ''
            for i in range(len(damage)):
                if damage[i] > 0:
                    damagelist += str(damage[i])
                    if (i + 1) < len(damage):
                        damagelist += ' and '

            msg += '**{} hit {} for {} damage!**\n'.format(attacker.name, opponent.name, damagelist)

        if sum(damage) == 0:
            msg += ('`{} missed their attack!`\n'.format(attacker.name))

        if currentChan(serverid, channelid)['Message']:
            await self.bot.delete_message(currentChan(serverid, channelid)['Message'])

        currentChan(serverid, channelid)['Message'] = await self.bot.say('{}\n{}:\n\n                HP:  {}  **|{}|**'
                                       '\n            SPEC:  **{}**\n          FOOD:  {}\tRunes:  {}                                  '
                                        '\n\n\n{}:\n\n                HP:  {}  **|{}|**\n            SPEC:  **{}**\n'
                                       '          FOOD:  {}\tRunes:  {}\n\n'.format(
            msg, ('**' + opponent.name + '**'), opponent.HP, ('░' * (opponent.HP // 5)),
            ('▮' * (opponent.Special_Attack_Bar // 25)),
            opponent.Food, opponent.Runes,
            ( '**' + attacker.name + '**'), attacker.HP, ('░' * (attacker.HP // 5)),
            ('▮' * (attacker.Special_Attack_Bar // 25)),
            attacker.Food, attacker.Runes))
        return


def currentChan(server, channelid):
    try:
        for serv in Match_Data['server']:
            if serv['ID'] == server:
                for chan in serv['channels']:
                    if chan['ID'] == channelid:
                        return chan
    except Exception as e:
        return print(e)


def check_server(serverid, servername, channelid, channelname, playerid, playername):
    global Match_Data
    if Match_Data == {}:
        Match_Data = {'server': []}

    for server in Match_Data['server']:
        if server['ID'] == serverid:
            for channel in server['channels']:
                if channel['ID'] == channelid:
                    return

            server['channels'].append({
                'name': channelname,
                'ID': channelid,
                'Player_1': '',
                'Player_1_Name': '',
                'Player_2': '',
                'Player_2_Name': '',
                'Instance': '',
                'Message': ''})
            return

    Match_Data['server'].append(
        {'ID': serverid,
         'Name': servername,
         'channels': [{
                'name': channelname,
                'ID': channelid,
                'Player_1': '',
                'Player_1_Name': '',
                'Player_2': '',
                'Player_2_Name': '',
                'Instance': '',
                'Message': ''}
                    ]})

    with open('DB.json') as f:
        DB = json.load(f)
    print('loaded DB', DB)

    if playerid not in DB.keys():
        DB[playerid] = {'name': playername,
                                                'Wins': {}, 'Loses': {},
                                                'items': {'Coins': 420},
                                                'equip': {'head': '', 'chest': '', 'cape': '', 'gloves': '',
                                                          'legs': '', 'boots': '',
                                                          'mainhand': '', 'offhand': ''}}

    with open('DB.json', 'w') as f:
        json.dump(DB, f, indent=2)

    return


def setup(bot):
    bot.add_cog(MatchManager(bot))
