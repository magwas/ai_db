#!/usr/bin/python

################################################################################
# Quick-hacked filter script to prevent confusing the terminal when displaying
# some binary stuff. Also highlights some special log entry substrings with
# colors.
#
# - reads lines from STDIN,
# - converts nonprintable characters to hexa or menmonics with inverted display
# - highlights some log entry substrings with different colors
# - writes the result to STDOUT
# Runs in an infinite loop, uses no buffering.
# Can be stopped with Ctrl-C :-)
#
# Note: far much slower than the same in Perl :-(
#
# TRACK:
# date------ who--------------- what--------------------------------------------
# 2002.05.15 Laszlo Gerencser   Initial version
#
################################################################################

import sys
import re
import string
import binascii


######## VARS ########

# DEC VT220 terminal escape sequences
normal     = "\x1B[0m"  #normal video mode
hi_on      = "\x1B[1m"  #hilite (bold) video mode
ul_on      = "\x1B[4m"  #underline video mode
rev_on     = "\x1B[7m"  #reverse video mode
red_fg     = "\x1B[31m" #foreground colors
green_fg   = "\x1B[32m"
yellow_fg  = "\x1B[33m"
blue_fg    = "\x1B[34m"
magenta_fg = "\x1B[35m"
cyan_fg    = "\x1B[36m"
white_fg   = "\x1B[37m"
default_fg = "\x1B[39m"

# Nonprintable regexp filters
nonpr1 = re.compile("([\\x00-\\x08\\x0B-\\x0C\\x0E-\\x1F\\x80-\\x9F])") #control charsof ISO-8859-1
nonpr2 = re.compile("([\\x7F])") #delete char
nonpr3 = re.compile("([\\x0D])") #CR char (can do dirty things with some terminal emulators)

# Log substring matching regexp filters specialized to the current log format of WATCHTOWER
# They depend on the re.sub execution order of colorize()
firstfrom     = re.compile("(\w{1,4}\s+\d{1,2}\s+\d\d:\d\d:\d\d)(\s+[\w\d\.\/\@]+)") #first string after the timestamp, identifying the system
lastfrom      = re.compile("(r\:\s\w+)$") #last string identifying the system (r: anything)
firststamp    = re.compile("^(\w{1,4}\s+\d{1,2}\s+\d\d:\d\d:\d\d)") #first timestamp of the line
httperror     = re.compile("(\"\w+ .*?HTTP/[\d\.]+\"\s)(\d+)(\s\d+\s\".*?\")") #http error message


######## DEFS ########

# Function to filter out nonprintable characters
def filter_nonprintable(s):
     """Gets a string parameter, filters out nonprintable chars and returns it.

     Nonprintable stuff will be converted to hexa values or menmonics with
     inverse terminal display.
     Inverse display is done by ANSI terminal escape sequences (DEC VT220)."""

     #oh god, how ugly is this lambda thing...
     s = re.sub( nonpr1, lambda matchobj: rev_on + string.upper( binascii.b2a_hex( matchobj.group() ) ) + normal , s )
     s = re.sub( nonpr2, rev_on + "<DEL>" + normal, s )
     s = re.sub( nonpr3, rev_on + "<CR>" + normal, s )
     return s


# Function to colorize log entries
def colorize(s):
     """Gets a string parameter (preferably a log entry), higlights some special
substrings with colors and returns it.

     Highlighting is done by ANSI terminal escape sequences (DEC VT220)."""

     #the exec order is important here due to the quick-and-dirty type of this code...
     s = re.sub( firstfrom,  "\g<1>" + cyan_fg + hi_on + "\g<2>" + normal + default_fg,   s )
     s = re.sub( lastfrom,   yellow_fg + hi_on + "\g<1>" + normal + default_fg, s )
     s = re.sub( firststamp, green_fg + "\g<1>" + default_fg,  s )
     s = re.sub( httperror, "\g<1>" + hi_on + "\g<2>" + normal + "\g<3>",  s )

     return s


######## MAIN ########

#while 1:
#    sys.stdout.write( colorize( filter_nonprintable( sys.stdin.readline() ) ) )
#    sys.stdout.flush()


