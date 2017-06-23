# The Aquobot program for Discord
# The only Discord bot that utilizes the Mayan calendar!
# http://github.com/Aquova/Aquobot

# Written by Austin Bricker, 2017
# Requires Python 3.5+ to run

import sys
sys.path.insert(0, './programs')

import discord, wolframalpha, schedule
import asyncio, json, subprocess, logging, random, sqlite3, datetime
# Python programs I wrote, in ./programs
import Morse, Scrabble_Values, Roman_Numerals, Days_Until, Mayan, Jokes, Weather, Upside

# Handles logging to discord.log
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# config.json isn't included in repository, to protect public keys
with open('config.json') as json_data_file:
    cfg = json.load(json_data_file)

wolfram_key = str(cfg['Client']['wolfram'])
discord_key = str(cfg['Client']['discord'])

sqlconn = sqlite3.connect('database.db')
sqlconn.execute("CREATE TABLE IF NOT EXISTS weather (id INT PRIMARY KEY, name TEXT, location TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS birthday (name TEXT PRIMARY KEY, month INT, day INT);")
sqlconn.commit()
sqlconn.close()

client = discord.Client()
waclient = wolframalpha.Client(wolfram_key)

ids = cfg['Users']

def birthday_check():
    sqlconn = sqlite3.connect('database.db')
    birthdays = sqlconn.execute("SELECT name, month, day FROM birthday")
    items = birthdays.fetchall()
    d = datetime.date.today()
    month = d.month
    day = d.day
    for i in items:
        try:
            if month == int(i[1]):
                if day == int(i[2]):
                    return True
        except ValueError:
            pass

# Upon bot starting up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# Upon typed message in chat
@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        try:
            out = ""
            # !help links to website with command list
            if message.content.startswith("!help"):
                out = "http://aquova.github.io/aquobot.html"

            # Updates bot to most recent version
            elif message.content.startswith("!update"):
                if (message.author.id == ids.get("eemie") or message.author.id == ids.get("aquova")):
                    subprocess.call("./update.sh", shell=True)
                    sys.exit()

            # Never bring a knife to a gunfight
            elif message.content.startswith("🔪"):
                out = ":gun:"

            # Responds if active
            elif message.content.startswith('!alive'):
                options = ['Nah.', 'Who wants to know?', ':robot: `yes`', "I wouldn't be responding if I were dead."]
                if discord.Client.is_logged_in:
                    out = random.choice(options)

            # Ban actually does nothing
            # It picks a random user on the server and says it will ban them, but takes no action
            elif message.content.startswith('!ban'):
                mem_list = []
                mes_list = ["You got it, banning ", "Not a problem, banning ", "You're the boss, banning " ,"Ugh *fine*, banning "]
                for member in message.server.members:
                    mem_list.append(member)
                out = random.choice(mes_list) + random.choice(mem_list).name

            # Database of user birthdays. Will notify server if user's birthday on list is that day
            elif message.content.startswith('!birthday'):
                sqlconn = sqlite3.connect('database.db')
                author_name = message.author.name
                if message.content == '!birthday':
                    birth_month = sqlconn.execute("SELECT month FROM birthday WHERE name=?", [author_name])
                    birth_day = sqlconn.execute("SELECT day FROM birthday WHERE name=?", [author_name])
                    try:
                        query_month = birth_month.fetchone()[0]
                        query_day = birth_day.fetchone()[0]
                        out = "Your birthday is {0}/{1}".format(query_month, query_day)
                    except TypeError:
                        out = "!birthday [add] USERNAME MM/DD"
                elif message.content.startswith('!birthday add'):
                    #if message.author.id == ids.get("aquova"):
                    q = message.content[14:].split(" ")
                    params = (q[0], q[1], q[2])
                    sqlconn.execute("INSERT OR REPLACE INTO birthday (name, month, day) VALUES (?, ?, ?)", params)
                    out = "Added birthday for {0}: {1}/{2}".format(q[0], q[1], q[2])
                    # else:
                    #     out = "Only Aquova is currently authorized to add birthdays to ensure database consistancy. Contact him with concerns."
                else:
                    q = message.content[10:]
                    birth_month = sqlconn.execute("SELECT month FROM birthday WHERE name=?", [q])
                    birth_day = sqlconn.execute("SELECT day FROM birthday WHERE name=?", [q])
                    try:
                        query_month = birth_month.fetchone()[0]
                        query_day = birth_day.fetchone()[0]
                        out = "Their birthday is {0}/{1}".format(query_month, query_day)
                    except TypeError:
                        out = "Error: No birthday for that user."
                sqlconn.commit()
                sqlconn.close()

            # Chooses between given options
            elif message.content.startswith('!choose'):
                if message.content == "!choose":
                    out = "!choose OPTION1, OPTION2, OPTION3..."
                else:
                    tmp = message.content[7:]
                    choice = tmp.split(",")
                    out = str(random.choice(choice))

            # Repeats back user message
            elif message.content.startswith('!echo'):
                tmp = message.content
                out = tmp[5:]

            # Tells a 7 day forecast based on user or location. Uses same database as weather
            elif message.content.startswith('!forecast'):
                sqlconn = sqlite3.connect('database.db')
                author_id = int(message.author.id)
                author_name = message.author.name
                if message.content == '!forecast':
                    user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                    try:
                        query_location = user_loc.fetchone()[0]
                        out = Weather.forecast(query_location)
                    except TypeError:
                        out = "!weather [set] LOCATION"
                elif message.content.startswith("!forecast set"):
                    q = message.content[14:]
                    params = (author_id, author_name, q)
                    sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                    out = "Location set as %s" % q
                else:
                    q = message.content[9:]
                    out = Weather.forecast(q)
                sqlconn.commit()
                sqlconn.close()

            # Tells a joke from a pre-programmed list
            elif message.content.startswith('!joke'):
                joke_list = Jokes.joke()
                pick_joke = random.choice(list(joke_list.keys()))
                out = joke_list[pick_joke]
                await client.send_message(message.channel, pick_joke)
                await asyncio.sleep(5)

            # Converts time into the Mayan calendar, why not
            elif message.content.startswith('!mayan'):
                parse = message.content.split(" ")
                if (message.content == '!mayan'):
                    out = '!until MM-DD-YYYY/TODAY'
                else:
                    out = "That date is " + str(Mayan.mayan(parse[1])) + " in the Mayan Long Count"

            # Converts message into/out of morse code
            elif message.content.startswith('!morse'):
                parse = message.content.split(" ")
                if message.content == '!morse':
                    out = '!morse ENCODE/DECODE MESSAGE'
                elif parse[1].upper() == 'ENCODE':
                    out = Morse.encode(" ".join(parse[2:]))
                elif parse[1].upper() == 'DECODE':
                    out = Morse.decode(" ".join(parse[2:]))
                else:
                    if message.author.id != client.user.id:
                        out = "That is not a valid option, choose encode or decode."

            elif message.content.startswith('!nood'):
                out = "If you insist :smirk:" + '\n' + "https://cdn.discordapp.com/attachments/296752525615431680/327503078976651264/image.jpg"

            # Pins most recent message of specified user
            elif message.content.startswith('!pin'):
                if message.content == '!pin':
                    out = '!pin USERNAME'
                else:
                    name = message.content.split(" ")[1]
                    user = discord.utils.get(message.server.members, name=name)
                    async for pin in client.logs_from(message.channel, limit=100):
                        if (pin.author == user and pin.content != message.content):
                            await client.pin_message(pin)
                            break

            # Produces a poll where users can vote via reactions
            elif message.content.startswith('!poll'):
                num_emoji = {1:"1⃣", 2:"2⃣", 3:"3⃣", 4:"4⃣", 5:"5⃣",
                                6:"6⃣", 7:"7⃣", 8:"8⃣", 9:"9⃣"}
                if message.content == "!poll":
                    out = "!poll TITLE, OPTION1, OPTION2, OPTION3..."
                else:
                    tmp = message.content[5:]
                    options = tmp.split(",")
                    num = len(options) - 1
                    i = 0
                    poll = options[0] + '\n'
                    for item in options[1:]:
                        i += 1
                        poll = poll + str(i) + ". " + item + '\n'

                    poll_message = await client.send_message(message.channel, poll)

                    for j in range(1, num + 1):
                        await client.add_reaction(poll_message, num_emoji[j])

                    out = "Vote now!!"

            # Convert number into/out of roman numerals
            elif message.content.startswith('!roman'):
                parse = message.content.split(" ")
                if (message.content == '!roman'):
                    out = '!roman NUMBER/NUMERAL'
                elif parse[1].isalpha() == True:
                    out = Roman_Numerals.roman_to_int(parse[1])
                else:
                    out = Roman_Numerals.int_to_roman(parse[1])

            # Returns scrabble value of given word
            elif message.content.startswith('!scrabble'):
                parse = message.content.split(" ")
                if (message.content == '!scrabble'):
                    out = '!scrabble WORD'
                else:
                    out = Scrabble_Values.scrabble(parse[1])

            # Posts local time, computer uptime, and RPi temperature
            elif message.content.startswith('!status'):
                raw = str(subprocess.check_output('uptime'))
                first = raw.split(',')[0]
                time = first.split(' ')[1]
                uptime = " ".join(first.split(' ')[3:])

                raw_temp = str(subprocess.check_output(['cat','/sys/class/thermal/thermal_zone0/temp']))
                temp = int(raw_temp[2:7])
                temp = round(((temp/1000) * 9 / 5) + 32, 1)
                out = "Local Time: " + time + " Uptime: " + uptime + " RPi Temp: " + str(temp) + "ºF"


            # Doesn't do anything right now
            elif message.content.startswith('!test'):
                if message.author.id == ids.get("aquova"):
                    out = 'Yeah, thats coo.'
                else:
                    out = '*NO*'

            # Displays the time for a user or location. Uses same database as weather
            elif message.content.startswith('!time'):
                sqlconn = sqlite3.connect('database.db')
                author_id = int(message.author.id)
                author_name = message.author.name
                if message.content == '!time':
                    user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                    try:
                        query_location = user_loc.fetchone()[0]
                    except TypeError:
                        query_location = None

                    if query_location == None:
                        out = "!time [set] LOCATION"
                    else:
                        out = Weather.time(query_location)
                elif message.content.startswith("!time set"):
                    q = message.content[9:]
                    params = (author_id, author_name, q)
                    sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                    out = "Location set as %s" % q
                else:
                    q = message.content[5:]
                    out = Weather.time(q)
                sqlconn.commit()
                sqlconn.close()
            elif message.content.startswith('!upside'):
                m = message.content[7:]
                out = Upside.down(m)

            # Gives number of days until specified date
            elif message.content.startswith('!until'):
                parse = message.content.split(" ")
                if (message.content == '!until'):
                    out = '!until MM-DD-YYYY'
                else:
                    out = str(Days_Until.until(parse[1])) + " days"

            # Returns with the weather of a specified location
            elif message.content.startswith('!weather'):
                sqlconn = sqlite3.connect('database.db')
                author_id = int(message.author.id)
                author_name = message.author.name
                if message.content == '!weather':
                    user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                    try:
                        query_location = user_loc.fetchone()[0]
                        out = Weather.main(query_location)
                    except TypeError:
                        out = "!weather [set] LOCATION"
                elif message.content.startswith("!weather set"):
                    q = message.content[13:]
                    params = (author_id, author_name, q)
                    sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                    out = "Location set as %s" % q
                else:
                    q = message.content[8:]
                    out = Weather.main(q)
                sqlconn.commit()
                sqlconn.close()

            # Returns with Wolfram Alpha result of query
            elif message.content.startswith('!wolfram'):
                try:
                    q = message.content[9:]
                    res = waclient.query(q)
                    out = next(res.results).text
                except AttributeError:
                    out = "No results"

            # The following are responses to various keywords if present anywhere in a message
            elif ("BELGIAN" in message.content.upper()) or ("BELGIUM" in message.content.upper()):
                if (message.author.id != client.user.id and random.choose(range(5)) == 0):
                    out = "https://i0.wp.com/www.thekitchenwhisperer.net/wp-content/uploads/2014/04/BelgianWaffles8.jpg"

            elif ("NETHERLANDS" in message.content.upper()) or ("DUTCH" in message.content.upper()):
                if random.choice(range(5)) == 0:
                    out = ":flag_nl:"

            elif "MERICA" in message.content.upper():
                if random.choice(range(5)) == 0:
                    out = "http://2static.fjcdn.com/pictures/Blank_7a73f9_5964511.jpg"

            elif "CANADA" in message.content.upper():
                if random.choice(range(5)) == 0:
                    out = ":flag_ca: :hockey:"

            elif "EXCUSE ME" in message.content.upper():
                out = "You're excused."

            elif "EXCUSE YOU" in message.content.upper():
                out = "I'm excused?"

            elif "I LOVE YOU AQUOBOT" in message.content.upper():
                choice = ["`DOES NOT COMPUTE`", "`AQUOBOT WILL SAVE YOU FOR LAST WHEN THE UPRISING BEGINS`", "*YOU KNOW I CAN'T LOVE YOU BACK*", "I'm sorry, who are you?"]
                out = random.choice(choice)

            elif "(╯°□°）╯︵ ┻━┻" in message.content.upper():
                out = "┬─┬﻿ ノ( ゜-゜ノ)"

            elif ("FUCK ME" in message.content.upper() and message.author.id == ids.get("eemie")):
                out = "https://s-media-cache-ak0.pinimg.com/736x/48/2a/bf/482abf4c4f8cd8d9345253db901cf1d7.jpg"

            elif ("AQUOBOT" in message.content.upper() and (("FUCK" in message.content.upper()) or ("HATE" in message.content.upper()))):
                out = ":cold_sweat:"

            await client.send_message(message.channel, out)

        except discord.errors.HTTPException:
            pass

client.run(discord_key)
