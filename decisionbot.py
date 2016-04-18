"""
   Decisionbot - A simple IRC bot to help make "coin flip" decisions.

   botname: x or y?
   => x

   botname: a or b or c?
   => b
"""

import random
import re

from irclib import nm_to_n


class Decisionbot():
    def __init__(self, config, queue):
        self.queue = queue

        nickname = config.get("main", "nickname")
        self.question_regexp = re.compile(r"^%s:?(.+\s+or\s+.+)\?+\s*$" %
                                          re.escape(nickname), re.IGNORECASE)
        self.question_delim_regexp = re.compile(r"\s+or\s+", re.IGNORECASE)

    def on_pubmsg(self, connection, event):
        channel = event.target()
        message = event.arguments()[0]
        sender = nm_to_n(event.source())

        match = self.question_regexp.search(message)
        if (match):
            choices = self.question_delim_regexp.split(match.group(1).strip("? \t"))
            if len(choices) > 1:
                self.say_public(channel, "%s: %s" % (sender, random.choice(choices)))

    def say_public(self, channel, text):
        self.queue.send(text, channel)
