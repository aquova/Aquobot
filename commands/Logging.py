# Better logging functionality for Aquobot

import os, discord, datetime

def setup(servers):
    if not os.path.isdir("logs"):
        os.makedirs("logs")
        for server in servers:
            folder = "logs/" + server.name
            os.makedirs(folder)
    else:
        for server in servers:
            folder = "logs/" + server.name
            if not os.path.isdir(folder):
                os.makedirs(folder)

def renameServer(old, new):
    oldFolder = "logs/" + old.name
    newFolder = "logs/" + new.name
    os.rename(oldFolder, newFolder)
    for channel in new.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(new.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("The server {} has been renamed to {}\n".format(old.name, new.name))

def write(message):
    if message.channel.type == discord.ChannelType.text:
        f = "logs/{}/#{}.log".format(message.server.name, message.channel.name)
        ts = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        try:
            if message.author.nick == None:
                name = message.author.name
            else:
                name = message.author.nick
        except AttributeError:
            name = message.author.name
        with open(f, 'a', encoding='utf-8') as openFile:
            openFile.write("{} <{}> {}\n".format(ts, name, message.content))

def changeNick(old, new, server):
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{}#{} is now known as {}\n".format(old.name, old.discriminator, new))

def changedRole(role, name, server, gained):
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(server.name, channel.name)
            with open(f, 'a') as openFile:
                if gained:
                    openFile.write("{} has gained the role {}\n".format(name, role))
                else:
                    openFile.write("{} has lost the role {}\n".format(name, role))

def memberJoined(member, server):
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{}#{} has joined the server\n".format(member.name, member.discriminator))

def memberLeave(member, server):
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{}#{} has left the server\n".format(member.name, member.discriminator))

def ban(member):
    for channel in member.server.channels:
        if channel.type == discord.ChannelType.text:
            f = "logs/{}/#{}.log".format(member.server.name, channel.name)
            with open(f, 'a') as openFile:
                openFile.write("{}#{} has been banned.\n".format(member.name, member.discriminator))

