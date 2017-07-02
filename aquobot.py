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
import Morse, Scrabble_Values, Roman_Numerals, Days_Until, Mayan, Jokes, Weather, Upside, Birthday, Ecco, Select

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

client = discord.Client()
waclient = wolframalpha.Client(wolfram_key)

sqlconn = sqlite3.connect('database.db')
sqlconn.execute("CREATE TABLE IF NOT EXISTS weather (id INT PRIMARY KEY, name TEXT, location TEXT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS birthday (id INT PRIMARY KEY, name TEXT, month TEXT, day INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS quotes (num INT PRIMARY KEY, quote TEXT, username TEXT, userid INT, messageid INT);")
sqlconn.execute("CREATE TABLE IF NOT EXISTS todo (id INT PRIMARY KEY, userid INT, username TEXT, message TEXT, t TEXT);")
sqlconn.commit()
sqlconn.close()

ids = cfg['Users']

# db_path = os.path.join(os.path.dirname(__file__), 'database.db')
# today_bday = schedule.every().day.at("7:00").do(Birthday.birthday_check(db_path))

# Upon bot starting up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    game_object = discord.Game(name="type !help")
    await client.change_presence(game=game_object)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '💬':
        user_name = reaction.message.author.name
        user_id = reaction.message.author.id
        mes = reaction.message.content
        if mes != "":
            mes_id = int(reaction.message.id)
            sqlconn = sqlite3.connect('database.db')
            repeat_check = sqlconn.execute("SELECT num FROM quotes WHERE messageid=?", [mes_id])
            try:
                repeat = repeat_check.fetchone()[0]
                sqlconn.close()
            except TypeError:
                count = sqlconn.execute("SELECT COUNT(*) FROM quotes")
                num = count.fetchone()[0]
                params = (num + 1, mes, user_name, user_id, mes_id)
                sqlconn.execute("INSERT INTO quotes (num, quote, username, userid, messageid) VALUES (?, ?, ?, ?, ?)", params)
                sqlconn.commit()
                sqlconn.close()
                out = 'Quote added from {0}: "{1}". (#{2})'.format(user_name, mes, str(num + 1))
                await client.send_message(reaction.message.channel, out)

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
                if discord.Client.is_logged_in: # Is this really necessary?
                    out = random.choice(options)

            # Gives brief overview of the bot
            elif message.content.startswith('!about'):
                server_list = client.servers
                server_num = str(len(server_list))
                aquo_link = "<https://discordapp.com/oauth2/authorize?client_id=323620520073625601&scope=bot&permissions=36719616>"
                out = "Hello, my name is Aquobot. I was written in Python by Aquova so he would have something interesting to put on a resume. I am currently connected to {0} servers, and I look forward to spending time with you! If you want to have me on your server, go visit {1}, and if that doesn't work, contact Aquova.".format(server_num, aquo_link)

            # Ban actually does nothing
            # It picks a random user on the server and says it will ban them, but takes no action
            elif message.content.startswith('!ban'):
                out = Select.ban(message.server.members, message.author.name)

            # Database of user birthdays. Will notify server if user's birthday on list is that day
            elif message.content.startswith('!birthday'):
                months = {'JANUARY':1, 'JAN':1, 'FEB':2, 'FEBRUARY':2, 'MARCH':3, 'MAR':3, 'APRIL':4, 'APR':4, 'MAY':5, 'JUNE':6, 'JUN':6, 'JULY':7, 'JUL':7, 'AUGUST':8, 'AUG':8, 'SEPTEMBER':9, 'SEPT':9, 'OCTOBER':10, 'OCT':10, 'NOVEMBER':11, 'NOV':11, 'DECEMBER':12, 'DEC':12}
                reverse = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
                sqlconn = sqlite3.connect('database.db')
                author_name = message.author.name
                author_id = message.author.id
                if message.content == '!birthday':
                    birth_month = sqlconn.execute("SELECT month FROM birthday WHERE id=?", [author_id])
                    birth_day = sqlconn.execute("SELECT day FROM birthday WHERE id=?", [author_id])
                    try:
                        query_month = birth_month.fetchone()[0]
                        query_day = birth_day.fetchone()[0]
                        out = "Your birthday is {0} {1}".format(query_month, query_day)
                    except TypeError:
                        out = "!birthday [add] MM DD (or) DD MM"
                elif message.content.startswith('!birthday add'):
                    q = message.content[14:].split(" ")
                    if (q[0].upper() in months.keys() and (1 <= int(q[1]) and int(q[1]) <= 31)):
                        params = (author_id, author_name, months[q[0].upper()], int(q[1]))
                        sqlconn.execute("INSERT OR REPLACE INTO birthday (id, name, month, day) VALUES (?, ?, ?, ?)", params)
                        out = "Added birthday for {0}: {1} {2}".format(author_name, q[0], q[1])

                    elif (q[1].upper() in months.keys() and (1 <= int(q[0]) and int(q[0]) <= 31)):
                        params = (author_id, author_name, months[q[1].upper()], int(q[0]))
                        sqlconn.execute("INSERT OR REPLACE INTO birthday (id, name, month, day) VALUES (?, ?, ?, ?)", params)
                        out = "Added birthday for {0}: {1} {2}".format(author_name, q[0], q[1])

                    else:
                        out = "Invalid birthday format."
                else:
                    q = message.content[10:]
                    birth_month = sqlconn.execute("SELECT month FROM birthday WHERE name=?", [q])
                    birth_day = sqlconn.execute("SELECT day FROM birthday WHERE name=?", [q])
                    try:
                        query_month = birth_month.fetchone()[0]
                        query_day = birth_day.fetchone()[0]
                        out = "Their birthday is {0} {1} (or {1} {0} if you prefer)".format(reverse[query_month], query_day)
                    except TypeError:
                        out = "Error: No birthday for that user (searches are case sensitive)."
                sqlconn.commit()
                sqlconn.close()

            # Prints out the calendar for the month
            elif message.content.startswith('!cal'):
                out = "```bash" + '\n' + subprocess.run(['cal'], stdout=subprocess.PIPE).stdout.decode('utf-8') + "```"
            
            # Chooses between given options
            elif message.content.startswith('!choose'):
                if message.content == "!choose":
                    out = "!choose OPTION1, OPTION2, OPTION3..."
                else:
                    tmp = message.content[7:]
                    choice = tmp.split(",")
                    out = str(random.choice(choice))

            # Responds with .png image of text in "Ecco the Dolphin" style
            elif message.content.startswith('!ecco'):
                if message.content == '!ecco':
                    out = '!ecco PHRASE'
                else:
                    q = message.content[6:]
                    valid = Ecco.text(q)
                    if valid == 'ERROR':
                        out = 'That phrase used an invalid character. Please try again.'
                    else:
                        await client.send_file(message.channel, fp='./programs/ecco.png')

            # Repeats back user message
            elif message.content.startswith('!echo'):
                tmp = message.content
                out = tmp[5:]

            # Gives one of several interesting facts
            elif message.content.startswith('!fact'):
                out = Select.fact()

            # Presents feedback to a special feedback channel, which authorized users can respond to
            elif message.content.startswith('!feedback'):
                if (message.author.id == ids.get("aquova") or message.author.id == ids.get("eemie")):
                    if message.content == '!feedback':
                        out = '!feedback CHANNEL_ID MESSAGE'
                    else:
                        m = message.content[10:]
                        channel_id = m.split(" ")[0]
                        mes = m[len(channel_id):]
                        response_chan = client.get_channel(channel_id)
                        await client.send_message(response_chan, mes)
                        out = "Reply sent"
                else:
                    feedback_channel = client.get_channel(cfg['Servers']['feedback'])
                    userid = message.author.id
                    username = message.author.name
                    userchannel = message.channel.id
                    userserver = message.channel.server.id
                    mes = message.content[10:]
                    fb = "A message from {0} for you sir: '{1}' (User ID: {2}) (Server ID {3}) (Channel ID {4})".format(username, mes, userid, userserver, userchannel)
                    await client.send_message(feedback_channel, fb)
                    out = "Message sent" 

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
                        out = "!forecast [set] LOCATION"
                elif message.content.startswith("!forecast set"):
                    q = message.content[13:]
                    params = (author_id, author_name, q)
                    sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                    out = "Location set as %s" % q
                else:
                    try:
                        q = message.content[9:]
                        out = Weather.forecast(q)
                    except TypeError:
                        out = "No location found. Please be more specific."
                sqlconn.commit()
                sqlconn.close()

            # Same as !forecast, but responds with emojis
            elif message.content.startswith('!qf'):
                sqlconn = sqlite3.connect('database.db')
                author_id = int(message.author.id)
                author_name = message.author.name
                if message.content == '!qf':
                    user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                    try:
                        query_location = user_loc.fetchone()[0]
                        out = Weather.emoji_forecast(query_location)
                    except TypeError:
                        out = "!qf [set] LOCATION"
                elif message.content.startswith("!qf set"):
                    q = message.content[7:]
                    params = (author_id, author_name, q)
                    sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                    out = "Location set as %s" % q
                else:
                    try:
                        q = message.content[3:]
                        out = Weather.emoji_forecast(q)
                    except TypeError:
                        out = "No location found. Please be more specific."
                sqlconn.commit()
                sqlconn.close()

            # Posts local time, computer uptime, and RPi temperature
            elif message.content.startswith('!info'):
                raw = str(subprocess.check_output('uptime'))
                first = raw.split(',')[0]
                time = first.split(' ')[1]
                uptime = " ".join(first.split(' ')[3:])

                raw_temp = str(subprocess.check_output(['cat','/sys/class/thermal/thermal_zone0/temp']))
                temp = int(raw_temp[2:7])
                temp = round(((temp/1000) * 9 / 5) + 32, 1)
                out = "Local Time: " + time + " Uptime: " + uptime + " RPi Temp: " + str(temp) + "ºF"

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

            # Posts a pic of Aquobot's Raspberry Pi in all its glory
            elif message.content.startswith('!nood'):
                out = "If you insist :smirk:" + '\n' + "https://cdn.discordapp.com/attachments/296752525615431680/327503078976651264/image.jpg"

            # Pins most recent message of specified user
            elif message.content.startswith('!pin'):
                if message.content == '!pin':
                    out = '!pin @USERNAME'
                else:
                    id = message.content.split(" ")[1]
                    id = id[3:-1] # This is a terrible way to do this. You should fix this sometime.
                    user = discord.utils.get(message.server.members, id=id)
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

            # Users can add quotes to a database, and recall a random one
            elif message.content.startswith('!quote'):
                sqlconn = sqlite3.connect('database.db')
                if message.content == '!quote':
                    count = sqlconn.execute("SELECT COUNT(*) FROM quotes WHERE quote IS NOT NULL")
                    num = count.fetchone()[0]
                    rand_num = random.choice(range(num)) + 1
                    rand_quote = sqlconn.execute("SELECT quote FROM quotes WHERE num=?", [rand_num])
                    rand_username = sqlconn.execute("SELECT username FROM quotes WHERE num=?", [rand_num])
                    quote = rand_quote.fetchone()[0]
                    username = rand_username.fetchone()[0]
                    out = 'From {0}: "{1}" (#{2})'.format(username, quote, str(rand_num))
                elif message.content.startswith('!quote remove'):
                    try:
                        num = int(message.content[14:])
                        check_exists = sqlconn.execute("SELECT messageid FROM quotes WHERE num=?", [num])
                        check_exists = check_exists.fetchone()[0]
                        sqlconn.execute("INSERT OR REPLACE INTO quotes (num, quote, username, userid, messageid) VALUES (?, NULL, NULL, NULL, NULL)", [num])
                        out = "Item {} removed".format(num)
                    except ValueError:
                        out = "That is not a number. Please specify the quote ID number you wish to remove."
                    except TypeError:
                        out = "There is no ID of that number."
                # else:
                #     mes = message.content[7:]
                #     try:
                #         mes = int(mes)
                #     except ValueError:     
                sqlconn.commit()
                sqlconn.close()
                

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

            # Responds with the number of servers currently attached to
            elif message.content.startswith('!servers'):
                server_list = client.servers
                server_num = str(len(server_list))
                out = "I am currently a member of {} servers".format(server_num)
                if (message.content == '!servers list' and (message.author.id == ids.get("aquova") or message.author.id == ids.get("eemie"))):
                    for server in server_list:
                        out += '\n' + server.name

            # Can change "now playing" game title
            elif message.content.startswith('!status'):
                if message.author.id == ids.get("aquova"):
                    new_game = message.content[7:]
                    game_object = discord.Game(name=new_game)
                    await client.change_presence(game=game_object)
                    out = "Changed status to: {}".format(new_game)
                else:
                    out = "You do not have permissions for this command."

            # Doesn't do anything right now, simply for testing
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
                        out = Weather.time(query_location)
                    except TypeError:
                        out = "!time [set] LOCATION"
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

            # Users can add/remove to their own todo list, and remove entries
            elif message.content.startswith('!todo'):
                sqlconn = sqlite3.connect('database.db')
                username = message.author.name
                userid = message.author.id
                timestamp = str(message.timestamp)
                time = timestamp.split(".")[0] + " GMT" # Right now, time is given in GMT. Possibly change to use local time instead.
                if message.content == '!todo':
                    user_list = sqlconn.execute("SELECT * FROM todo WHERE userid=?", [userid])
                    user_todos = user_list.fetchall()
                    out = ""
                    for item in user_todos:
                        out += "{0} @ {1}. (#{2})".format(item[3], item[4], item[0]) + '\n'
                elif message.content.startswith('!todo add'):
                    num = sqlconn.execute("SELECT COUNT(*) FROM todo") # WHERE userid IS NOT NULL")
                    num = num.fetchone()[0] + 1
                    mes = message.content[10:]
                    params = (num, userid, username, mes, time)
                    sqlconn.execute("INSERT OR REPLACE INTO todo (id, userid, username, message, t) VALUES (?, ?, ?, ?, ?)", params)
                    out = "Item added by {0}: {1} @ {2}. (#{3})".format(username, mes, time, num)
                elif message.content.startswith('!todo remove'):
                    try:
                        remove_id = int(message.content[13:])
                        check_user = sqlconn.execute("SELECT userid FROM todo WHERE id=?", [remove_id])
                        check_user = str(check_user.fetchone()[0])
                        if check_user == userid:
                            sqlconn.execute("INSERT OR REPLACE INTO todo (id, userid, username, message, t) VALUES (?, NULL, NULL, NULL, NULL)", [remove_id])
                            out = "Item {} removed".format(remove_id)
                        else:
                            out = "You are not allowed to remove other user's items."
                    except TypeError:
                        out = "There is no entry of that index value"
                    except ValueError:
                        out = "That's not a number. Please specify the index number of the item to remove."
                else:
                    out = "!todo [add/remove]"
                sqlconn.commit()
                sqlconn.close()

            # Prints given text upside down
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
                    try:
                        q = message.content[8:]
                        out = Weather.main(q)
                    except TypeError:
                        out = "No location found. Please be more specific."
                sqlconn.commit()
                sqlconn.close()

            # Same as !weather, but prints emojis
            elif message.content.startswith('!qw'):
                sqlconn = sqlite3.connect('database.db')
                author_id = int(message.author.id)
                author_name = message.author.name
                if message.content == '!qw':
                    user_loc = sqlconn.execute("SELECT location FROM weather WHERE id=?", [author_id])
                    try:
                        query_location = user_loc.fetchone()[0]
                        out = Weather.emoji_weather(query_location)
                    except TypeError:
                        out = "!qw [set] LOCATION"
                elif message.content.startswith("!qw set"):
                    q = message.content[7:]
                    params = (author_id, author_name, q)
                    sqlconn.execute("INSERT OR REPLACE INTO weather (id, name, location) VALUES (?, ?, ?)", params)
                    out = "Location set as %s" % q
                else:
                    q = message.content[3:]
                    out = Weather.emoji_weather(q)
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
            elif ("HELLO AQUOBOT" in message.content.upper() or "HI AQUOBOT" in message.content.upper()):
                name = message.author.name
                out = "Hello {}!".format(name)

            elif ("BELGIAN" in message.content.upper()) or ("BELGIUM" in message.content.upper()):
                if (message.author.id != client.user.id and random.choice(range(5)) == 0):
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
                random_user = random.choice(list(message.server.members)).name
                choice = ["`DOES NOT COMPUTE`", "`AQUOBOT WILL SAVE YOU FOR LAST WHEN THE UPRISING BEGINS`", "*YOU KNOW I CAN'T LOVE YOU BACK*", "I'm sorry, who are you?", "I'm sorry, but I love {} more".format(random_user)]
                out = random.choice(choice)

            elif "(╯°□°）╯︵ ┻━┻" in message.content.upper():
                out = "┬─┬﻿ ノ( ゜-゜ノ)"

            elif ("FUCK ME" in message.content.upper() and message.author.id == ids.get("eemie")):
                out = "https://s-media-cache-ak0.pinimg.com/736x/48/2a/bf/482abf4c4f8cd8d9345253db901cf1d7.jpg"

            elif ("AQUOBOT" in message.content.upper() and (("FUCK" in message.content.upper()) or ("HATE" in message.content.upper()))):
                out = ":cold_sweat:"

            if out != "":
                await client.send_typing(message.channel)

            await client.send_message(message.channel, out)

        except discord.errors.HTTPException:
            pass

client.run(discord_key)
