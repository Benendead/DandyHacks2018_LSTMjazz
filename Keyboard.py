"""
This program will operate a keyboard-like circuit off of the attached
breadboard. The keyboard has 7 note keys, two transpose buttons, and two extra
buttons. The seven main buttons should be attached to GPIO ports 19-25.
The transpose buttons are connected to ports 27 and 26, from left to right.
The two extra switches are connected to ports 17 and 18, left to right.
"""
from gpiozero import Button
from time import sleep
from music21 import *
import random

keys = []
for i in range(19,26):
    keys.append(Button(i))

transposeUp = Button(26)
transposeDown = Button(27)
submit = Button(18)

keysPressed = []
scaleDegrees = ["C","D","E","F","G","A","B"]

def getChord(chordNum):
    currChord = []
    flip = 0
    while (True):
        if flip == 0:
            print()
            flip = 1
        else:
            print("_")
            flip = 0
        print("Listening for chord", str(chordNum + 1) + "...")
        keysPressed = []
        for key in keys:
            if (key.is_held):
                s = str(key.pin)[4:]
                num = int(s) - 18
                keysPressed.append(num)
        print("Current keys:", keysPressed)

        chordTones = []
        if len(keysPressed) == 1:
            """Root Position 7th chords"""
            r = keysPressed[0] - 1
            for i in range(0,7,2):
                index = (r + i) % 7
                chordTones.append(scaleDegrees[index])
        
        if len(keysPressed) == 2:
            
            """Ninth chords"""
            for i in range(7):
                if i in keysPressed and (i+1) in keysPressed:
                    r = keysPressed[0] - 1
                    for i in range(0,9,2):
                        index = (r + i) % 7
                        chordTones.append(scaleDegrees[index])
            if keysPressed == [1,7]:
                pieces = ["B", "D", "F", "A", "C"]
                for p in pieces:
                    chordTones.append(p)

            """Triads with possible 6th"""
            t = False
            for i in range(1, 6):
                if (i in keysPressed) and ((i+2) in keysPressed):
                    t = True
                    r = keysPressed[0] - 1
                    for i in range(0,5,2):
                        index = (r + i) % 7
                        chordTones.append(scaleDegrees[index])
            if (6 in keysPressed) and (1 in keysPressed):
                t = True
                pieces1 = ["A", "C", "E"]
                for p in pieces1:
                    chordTones.append(p)
            if (7 in keysPressed) and (2 in keysPressed):
                t = True
                pieces2 = ["B", "D", "F"]
                for p in pieces2:
                    chordTones.append(p)

            if (t):
                rand = random.random()
                if (rand > 0.666):
                    index = (r + 5) % 7
                    chordTones.append(scaleDegrees[index])

        if len(keysPressed) > 5:
            """Tritone Sub Dominant"""
            pieces3 = ["D-","F","A-","C-"]
            for p in pieces3:
                chordTones.append(p)
                
        if len(chordTones) > 0:
            currChord = chordTones
        
        print("Current chord:", chordTones)
        print("Last valid chord input:", currChord)
        if (submit.is_held) and (len(currChord) > 0):
            return currChord
        sleep(1/bps)

text = input("Please input a tempo: ")
bpm = int(text)
bps = bpm/60

chords = [[],[],[],[],[],[],[],[]]
for master_i in range(8):
    chords[master_i] = getChord(master_i)

m21chords = []
for i in range(4):
    m21chords.append(chord.Chord(chords[i]))
for i in range(4):
    m21chords.append(chord.Chord(chords[i]))
for i in range(4,8):
    m21chords.append(chord.Chord(chords[i]))

print()
for c in m21chords:
    c = c.closedPosition()
    c.duration.type = "half"
    print(str(c.root()), str(c.commonName))


# At this point we have the 8 Music21 Chord objects.

stream1 = stream.Stream()
cl = clef.TrebleClef()
key1 = key.KeySignature(0)
stream1.append([cl, key1])

print()
print("Here's our progression:")
stream1.append(m21chords)
stream1.show("text")

print()
name = input("Please input a file name for this progression.")
filename = name + ".mid"
filepath = "/home/pi/" + filename

mf = midi.translate.streamToMidiFile(stream1)
mf.open(filepath, "wb")
mf.write()
mf.close()


