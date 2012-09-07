#!/usr/bin/python

import sys, re
from socket import *

serve_addr = ('localhost', 47701)

if __name__ == '__main__':
  IRC_BOLD = '\x02'
  IRC_ULINE = '\x1f'
  IRC_NORMAL = '\x0f'
  IRC_RED = '\x034'
  IRC_LIME = '\x039'
  IRC_BLUE = '\x0312'

  repo, author, rev, description = sys.argv[1:5]

  match = re.search(r'^\s*(.*?)\s*<.*>\s*$', author)
  if match:
    author = match.group(1)

  data = (
      "%(IRC_RED)s%(repo)s "
      "%(IRC_NORMAL)s%(IRC_BOLD)s%(author)s "
      "%(IRC_NORMAL)s%(IRC_ULINE)s%(rev)s%(IRC_NORMAL)s "
      "%(description)s" % locals()
      )
  if len(data) > 400:
    data = data[:400] + "..."
  sock = socket(AF_INET, SOCK_DGRAM)
  sock.sendto(data, serve_addr)
  sock.close()
