info = {
	'8ball':['!8ball', 'Gives a Magic 8-Ball response to a question', ''],
	'about':['!about', 'Aquobot gives a basic description of itself', ''],
	'alive':['!alive', 'Simply asks the bot to respond if active', ''],
	'apod':['!apod [YYYY-MM-DD]', "Gets an image from NASA's 'Astronomy Picture of the Day' site", ''],
	'birthday':['!birthday [set] MONTH DAY', 'Look up or add birthdays to the database', 'List birthdays with "!birthday list"'],
	'blackjack':['!blackjack', 'Play blackjack with the computer!', 'See how many points you have with "!points"'],
    'brainfuck':['!brainfuck', 'Convert messages into/out of the Brainfuck programming language', 'Also works with !bf'],
    'bf':['!bf', 'Convert messages into/out of the Brainfuck programming language', 'Also works with !brainfuck'],
	'cal':['!cal [MONTH]', 'Prints out the calendar for the month', ''],
	'choose':['!choose OPTION1, OPTION2, OPTION3, ...', 'Picks between a list of options, separated by commas', ''],
	'deletethis':['!deltethis', 'Posts the .gif of Eggman holding the "delete this" sign', 'Also works with "!dt"'],
	'define':['!define PHRASE COMMAND', 'Users can make their own commands that can then be called with !PHRASE!', ''],
	'dt':['!dt', 'Posts the .gif of Eggman holding the "delete this" sign', 'Also works with "!deletethis"'],
	'ecco':['!ecco PHRASE', 'Takes text and adds it to an image in the style of Ecco the Dolphin', ''],
	'echo':['!echo PHRASE', 'Repeats back what is said to it', ''],
	'fact':['!fact', 'Gives a great and interesting fact', ''],
	'feedback':['!feedback MESSAGE', 'Sends feedback to the developers', ''],
	'forecast':['!forecast [set] LOCATION', 'Gives a 7 day forecast of a given location', 'Can also be used with "!f"'],
	'f':['!f [set] LOCATION', 'Gives a 7 day forecast of a given location', 'Can also be used with "!forecast"'],
	'getavatar':['!getavatar [USERNAME]', 'Gives the avatar of the specified user', ''],
	'google':['!google PHRASE', 'Returns the first Google search result', 'Also works with "!g"'],
	'g':['!g PHRASE', 'Returns the first Google search result', 'Also works with "!google"'],
	'img':['!img PHRASE', 'Returns the first Google image search result', ''],
	'iss':['!iss', 'Returns the current location of the International Space Station (ISS)', ''],
	'joke':['!joke', 'Tells a joke', ''],
	'help':['!help [COMMAND]', 'Posts information on how to use a command. But you already know that.', ''],
	'lovecalc':['!lovecalc NAME1 NAME2', 'Gives the compatibility of two people. Toally not bogus.', 'Can also be used with "!lc"'],
	'lc':['!lc NAME1 NAME2', 'Gives the compatibility of two people. Toally not bogus.', 'Can also be used with "!lovecalc"'],
	'mathfact':['!mathfact INTEGER', 'Gives mathematical facts about a number', ''],
	'mayan':['!mayan MM-DD-YYYY', 'Converts the date into the Mayan Long Count', ''],
	'morse':['!morse MESSAGE', 'Converts message into or out of morse code', ''],
	'myanimelist':['!myanimelist [set] USERNAME', 'Shows the MyAnimeList profile of the given user', 'Also works with "!mal"'],
	'mal':['!mal [set] USERNAME', 'Shows the MyAnimeList profile of the given user', 'Also works with "!myanimelist"'],
	'nick':['!nick NEW_USERNAME', 'Gives your account the new nickname specified. (Basically the same as /nick but works on mobile)', "Aquobot's role needs to be higher than the user being edited. Due to this, this function can't work for server owners."],
	'pin':['!pin USERNAME', 'Pins the most recent post by the given user', 'You can also pin a message by reacting with :pushpin:'],
	'points':['!points', 'See how many points you have from the casino games', ''],
	'poll':['!poll TITLE, OPTION1, OPTION2, OPTION3, ...', 'Presents a poll for users, based on input separated by commas. Users can vote via Discord reactions.', ''],
	'quote':['!quote [remove #]', 'Returns a quote from the quote database', 'Quotes are added by reacting to a message with :speech_balloon:'],
	'qf':['!qf [set] LOCATION', 'The same as !forecast, but gives the forecast in emojis', ''],
	'qw':['!qw [set] LOCATION', 'The same as !weather, but gives the forecast in emojis', ''],
	'rockpaperscissors':['!rockpaperscissors HAND', 'Play Rock, Paper, Scissors against the computer!', 'Also works with !rps'],
	'rps':['!rps HAND', 'Play Rock, Paper, Scissors against the computer!', 'Also works with !rockpaperscissors'],
	'roman':['!roman NUMBER/NUMERAL', 'Converts numbers to/from roman numerals', ''],
	'scrabble':['!scrabble WORD', 'Calculates how many Scrabble points a word is worth', ''],
	'servers':['!servers', 'Lists the number of servers Aquobot is currently serving', ''],
	'serverinfo':['!serverinfo', 'Gives information on the current server', ''],
	'speedrun':['!speedrun GAME or !speedrun USER username', 'Gives information about a game or user on speedrun.com', ''],
	'spellcheck':['!spellcheck', 'Attempts to find any misspelled words in a sentence', ''],
	'slots':['!slots', 'Try your hand at a the slot machine!', 'You can see how many points you have with "!points"'],
	'steam':['!steam STEAM-USERNAME', 'Gives stats of a given Steam account', ''],
	'stop':['!stop', 'Posts one of several images featuring a stop sign', ''],
	'time':['!time [set] LOCATION', 'Posts the current time of a specified location', ''],
	'todo':['!todo [add/remove #]', 'Allows users to add, remove, or view items on their personal todo list', ''],
	'translate':['!translate TARGET-LANGUAGE PHRASE', 'Translates a phrase into a specified language', 'Can also use "!tr"\n^ can be used to translate previous message, i.e. !tr en ^'],
	'tr':['!tr TARGET-LANGUAGE PHRASE', 'Translates a phrase into a specified language', 'Can also use "!translate"\n^ can be used to translate previous message, i.e. !tr en ^'],
	'trapcard':['!trapcard', 'Posts the image of the "Bitch Hold On" trap card', ''],
	'twitch':['!twitch USERNAME', 'Posts info about the Twitch profile of the given username', ''],
	'upside':['!upside PHRASE', 'Returns the given text, but upside down', ''],
	'unshrug':['/unshrug', "Don't you wish there was an /unshrug to go with /shrug?", ''],
	'until':['!until MM-DD-YYYY', 'Gives the number of days until a specified date', ''],
	'userinfo':['!userinfo [USERNAME]', 'Gives info on the specified user', 'Can either type in the exact username or their "ping" name'],
	'weather':['!weather [set] LOCATION', 'Gives the current weather of a specified location', 'Also works with "!w"'],
	'w':['!w [set] LOCATION', 'Gives the current weather of a specified location', 'Also works with "!weather"'],
	'whatpulse':['!whatpulse [set] USERNAME', "Gives the statistics of a user's WhatPulse account", 'Also works with "!wp"'],
	'wp':['!wp [set] USERNAME', "Gives the statistics of a user's WhatPulse account", 'Also works with "!whatpulse"'],
	'wiki':['!wiki QUERY', 'Returns the Wikipedia page of the searched term', ''],
	'wolfram':['!wolfram QUERY', 'Provides an answer to a WolframAlpha query', ''],
	'xkcd':['!xkcd [random/#]', 'Posts a comic from xkcd', 'Either !xkcd random or !xkcd rand with produce a random comic.\n!xkcd will post the most recent comic.'],
	'youtube':['!youtube QUERY', 'Provides the YouTube link to the first result of the search phrase', 'Also works with "!yt"'],
	'yt':['!yt QUERY', 'Provides the YouTube link to the first result of the search phrase', 'Also works with "!youtube"']
}

def main(m):
	if m in list(info.keys()):
		output = "Syntax: `{}`\n{}".format(info[m][0], info[m][1])
		if info[m][2] != '':
			output += '\nNote: {}'.format(info[m][2])
	else:
		output = "There is no command by that name."

	return output

def functions():
	return list(info.keys())

