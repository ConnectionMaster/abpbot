#!/usr/bin/env python
#
# Simple IRC Bot to announce messages
#
# Code originally based on example bot and irc-bot class from
# Joel Rosdahl <joel@rosdahl.net>, author of included python-irclib.
#


"""An IRC bot to announce messages on a channel.

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  The bot enters a channel and relays messages fed to it
via some means (currently UDP).

"""

import sys, os
from threading import Thread

class Beanbot():
  def __init__(self, config, queue):
    self.queue = queue
    self.channel = config.get('main', 'channel')

    udpaddr = parse_host_port(config.get('beanbot', 'udp-addr'))
    self.inputthread = UDPInput(self, udpaddr)
    self.inputthread.start()

  def say_public(self, text):
    "Print TEXT into public channel, for all to see."
    self.queue.send(text, self.channel)


def parse_host_port(hostport, default_port=None):
  lis = hostport.split(":", 1)
  host = lis[0]
  if len(lis) == 2:
    try:
      port = int(lis[1])
    except ValueError:
      print "Error: Erroneous port."
      sys.exit(1)
  else:
    if default_port is None:
      print "Error: Port required in %s." % hostport
      sys.exit(1)
    port = default_port
  return host, port


class UDPInput(Thread):
  def __init__(self, bot, addr):
    Thread.__init__(self)
    self.setDaemon(1)
    self.bot = bot
    from socket import socket, AF_INET, SOCK_DGRAM
    self.socket = socket(AF_INET, SOCK_DGRAM)
    self.socket.bind(addr)

  def run(self):
    while 1:
      data, addr = self.socket.recvfrom(1024)
      self.bot.say_public(data)
