"""
    ANS2FANS
"""


import argparse
import types


parser = argparse.ArgumentParser(
    description='Converts ANSI art files (*.ans) to FANSI/MUSHcode format')
parser.add_argument('file', help='specify input file')
group = parser.add_mutually_exclusive_group()
group.add_argument('-o', '--output',
    help='specify the output file (default is stdout)')
args = parser.parse_args()

with open(args.file, 'r') as content_file:
    content = content_file.read()
content_file.close()    # close file because we don't need it anymore

string = list(content)
leng = len(string)


fore = 7
back = 0
highlight = False
underline = False
blinking = False
inverted = False
hidden = False

out = ['%R']
i = 0


while i < leng:
    o = (string[i][0])
    if o == chr(0) or o == chr(7) or o == chr(13):
        # print o
        pass
    elif o == '\n':
        out.append('%R')
    elif o == '\x1b': # ESC - 0x1B - 21
        type = 'm'
        code = ''
        j = i + 1
        stop = False
        while (j+1) < leng and stop == False:
            piece = string[j+1]
            if piece == '[':
                pass
            elif piece == '?':
                type = '?'
            elif piece == 'h':
                type = 'h'
                stop = True
            elif piece == 'm':
                type = 'm'
                stop = True
            elif piece == 'C':
                type = 'C'
                stop = True
            else:
                code += piece
            j += 1 # unsure of where to put this...
        i = j #- 1
        parts = code.split(';')
        for part in parts:
            part = int(part)
        if type == 'm':
            pieces = len(parts)
            for k in xrange(pieces):
                value = int(parts[k])
                if value == 1:
                    highlight=True
                    fore += 8
                elif value == 0:
                    fore = 7
                    back = 0
                    highlight = False
                    underline = False
                    blinking = False
                    inverted = False
                    hidden = False
                elif value == 4:
                    underline = not underline
                elif value == 5:
                    blinking = not blinking
                elif value == 7:
                    inverted = not inverted
                elif value == 8:
                    hidden = not hidden
                elif value >= 30 and value < 40:
                    fore = value - 30
                    if highlight == True:
                        fore += 8
                    else:
                        pass
                elif value >= 40 and value < 50:
                    back = value - 40
        elif type == 'C':
            number = int(parts[0])
            if back == 0 and int(parts[0]) < 6:
                out.append('%B' * int(parts[0]))
            else:
                out.append('[c(32,' + parts[0] + ')]')
                #out.append([fore, back, [[32, int(parts[0])]]])
        elif type == 'h':  # ignores code 7h
            pass
        elif type == '?':  # ignores 'screen mode' code ?#
            pass
    elif o == '\x1a':   # This starts a SAUCE record...
        break;  # ...we don't want any of that now do we?
    else:
        last = out[len(out) - 1]
        if last[0] == fore and last[1] == back:
            lastchar = last[2][len(last[2]) - 1]
            if lastchar[0] == ord(o):    # same char was just put in!
                # add the number of the last character to the new number
                out[len(out)-1][2][len(last[2])-1][1] += 1
            else:
                out[len(out)-1][2].append([ord(o), 1])
        else:
            out.append([fore, back, [[ord(o), 1]]]) 
    i += 1

print out


final = ""
total = len(out)
for i in xrange(total):
    if isinstance(out[i], str):
        final += out[i]
    elif not isinstance(out[i], basestring):
        fore = out[i][0]
        back = out[i][1]
        chars = out[i][2]
        """
        if i == total-1:
            if out[i][3] == 1:
                final += "[color("+str(fore)+","+str(back)+",c("+str(out[i][2])+"))]"
            else:
                final += "[color("+str(fore)+","+str(back)+",c("+str(out[i][2])+","+str(out[i][3])+"))]"
        if isinstance(out[i+1], basestring): # not array
            if out[i][3] == 1:
                final += "[color("+str(fore)+","+str(back)+",c("+str(out[i][2])+"))]"
            else:
                final += "[color("+str(fore)+","+str(back)+",c("+str(out[i][2])+","+str(out[i][3])+"))]"
        elif not isinstance(out[i+1], basestring): # is array
            if out[i][2] != out[i+1][2] or out[i][1] != out[i+1][1] or out[i][0] != out[i+1][0]:
                if out[i][3] == 1:
                    final += "[color("+str(fore)+","+str(back)+",c("+str(out[i][2])+"))]"
                else:
                    final += "[color("+str(fore)+","+str(back)+",c("+str(out[i][2])+","+str(out[i][3])+"))]"
            else:
                out[i+1][3] += out[i][3]
        """

        final += '[color(' + str(fore) + ',' + str(back) + ','
        if isinstance(chars, types.IntType):   # a number
            final += 'c(' + str(chars) + ')'
        elif isinstance(chars, basestring):
            final += chars
        elif len(chars) == 1:       # one c()
            if chars[0][0] == 32 and chars[0][1] == 1:   # space is smaller as %b
                final += '%b'
            elif chars[0][1] == 1:  # c(##)
                final += 'c(' + str(chars[0][0]) + ')'
            elif chars[0][1] > 1:   # c(##,##)
                final += 'c(' + str(chars[0][0]) + ',' + str(chars[0][1]) + ')'
        else: # more than one c()
            for char in chars:
                if char[1] == 1:
                    if char[0] == 32 and char[1] == 1:  # space is smaller as %b
                        final += '%b'
                    else:
                        final += '[c(' + str(char[0]) + ')]'
                elif char[1] > 1:
                    final += '[c(' + str(char[0]) + ',' + str(char[1]) + ')]'
        final += ')]'

if not args.output:     # print to stdio
    print final
else:                   # print to file
    outputfile = open(args.output, 'w+')
    outputfile.write(final)
