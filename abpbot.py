#!/usr/bin/env python
#
# Simple IRC Bot to announce messages
#
# Code originally based on example bot and irc-bot class from
# Joel Rosdahl <joel@rosdahl.net>, author of included python-irclib.
#


"""
An IRC bot stub, it will join a particular channel on a server. All
further functionality is implemented by additional handler classes.
"""

import sys
from ircbot import SingleServerIRCBot
import irclib
from botcommon import OutputManager
import logbot, beanbot

# The message returned when someone messages the bot
HELP_MESSAGE = "I am the Adblock Plus logging bot."

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


class Bot(SingleServerIRCBot):
  def __init__(self, config):
    ircaddr = parse_host_port(config.get('main', 'host'), 6667)
    self.channel = config.get('main', 'channel')
    self.nickname = config.get('main', 'nickname')
    try:
      self.nickpass = config.get('main', 'nickpass')
    except ConfigParser.NoOptionError:
      self.nickpass = None
    try:
      self.needinvite = (config.get('main', 'needinvite') == 'yes')
    except ConfigParser.NoOptionError:
      self.needinvite = False

    SingleServerIRCBot.__init__(self, [ircaddr], self.nickname, self.nickname, 5)
    self.queue = OutputManager(self.connection, .9)
    self.queue.start()

    self.handlers = {}

    def handler_for_key(self, key):
      return lambda c, e: self.execute_handlers(key, c, e)

    for handler in logbot.Logbot(config, self.queue), beanbot.Beanbot(config, self.queue):
      for props in handler.__dict__, handler.__class__.__dict__:
        for key in props.iterkeys():
          if not key.startswith('on_'):
            continue
          value = getattr(handler, key)
          if not hasattr(value, '__call__'):
            continue

          if not key in self.handlers:
            # Set up handling for this message
            self.handlers[key] = []
            if hasattr(self, key):
              self.handlers[key].append(getattr(self, key))
            setattr(self, key, handler_for_key(self, key))

          # Add new handler for this message
          self.handlers[key].append(value)

    try:
      self.start()
    except KeyboardInterrupt:
      self.connection.quit("Ctrl-C at console")
    except Exception, e:
      self.connection.quit("%s: %s" % (e.__class__.__name__, e.args))
      raise

  def execute_handlers(self, key, c, e):
    for handler in self.handlers[key]:
      handler(c, e)

  def do_join(self, c):
    if self.needinvite:
      c.privmsg("chanserv", "invite %s" % self.channel)
    c.join(self.channel)

  def on_nicknameinuse(self, c, e):
    c.nick(c.get_nickname() + "_")

  def on_quit(self, c, e):
    source = irclib.nm_to_n(e.source())
    if source == self.nickname:
      # Our desired nick just quit - take the nick back
      c.nick(self.nickname)
      self.do_join(c)

  def on_welcome(self, c, e):
    if self.nickpass and c.get_nickname() != self.nickname:
      # Reclaim our desired nickname
      c.privmsg('nickserv', 'ghost %s %s' % (self.nickname, self.nickpass))
    else:
      # Identify ourselves before joining the channel
      c.privmsg("nickserv", "identify %s" % self.nickpass)
      self.do_join(c)

  def on_privmsg(self, c, e):
    c.privmsg(irclib.nm_to_n(e.source()), HELP_MESSAGE)


def usage(exitcode=1):
  print "Usage: %s <config-file>" % sys.argv[0]
  sys.exit(exitcode)

def main():
  if len(sys.argv) < 2:
    usage()

  configfile = sys.argv[1]

  import ConfigParser
  config = ConfigParser.ConfigParser()
  config.read(configfile)
  Bot(config)

if __name__ == "__main__":
  main()
