# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 22:40:23 2020

@author: Anders
"""
import random

        
def viterbi(vals, states, valid, transition):
    n=len(vals)
    k=len(states)
    dists = [[0 for guy in states] for guy in vals]
    prevs = [[0 for guy in states] for guy in vals]
    inf = float('inf')
    dists[0] = [0 if valid(vals[0], guy) else inf for guy in states]
    for i in range(1, n):
        for j in range(k):
            if not valid(vals[i], states[j]):
                dists[i][j] = inf
                continue
            sml = inf
            prev = []
            for l in range(k):
                dist = dists[i-1][l] + transition(states[l], states[j])
                if dist < sml:
                    sml = dist
                    prev =[l]
                elif dist == sml:
                    prev.append(l)
            dists[i][j] = sml
            prevs[i][j] = random.choice(prev)
    path = [dists[-1].index(min(dists[-1]))]
    for i in range(n-1, 0, -1):
        path.append(prevs[i][path[-1]])
    return [states[guy] for guy in path[::-1]]

# twinkle = [0,0,7,7,9,9,7,5,5,4,4,2,2,0]
# row = [0,0,0,2,4,4,2,4,5,7,0,0,0,7,7,7,4,4,4,0,0,0,7,5,4,2,0]
# ode = [4,4,5,7,7,5,4,2,0,0,2,4,4,2,2,4,4,5,7,7,5,4,2,0,0,2,4,2,0,0]
# # states = ["I", "IV", "vi", "V7"]
# # print(viterbi(row, states, valid, transition))


def dot(x,y):
    return sum(x[i]*y[i] for i in range(len(x)))
def find_key(vals):
    major = [10,-14,5,-12,8,5,-6,8,-6,4,-8,6]
    minor = [9,-9,3,7,-8,3,-8,7,3,-9,0,2]
    vals = [(guy - 60) % 12 for guy in vals]
    counts = [0,0,0,0,0,0,0,0,0,0,0,0]
    for guy in vals:
        counts[guy]+=1
    big = 0
    do = None
    tonality = None
    for i in range(12):
        # print(dot(counts, major))
        # print(dot(counts, minor))
        if dot(counts, major) > big:
            big = dot(counts, major)
            do = i
            tonality = 'major'
        if dot(counts, minor) > big:
            big = dot(counts, minor)
            do = i
            tonality = 'minor'
        counts.append(counts.pop(0))
    return (do, tonality)


def valid(i, chord):
    chords = {"I":[0,4,7],"IV":[0,5,9],"vi":[0,4,9],"V7":[2,5,7,11]}
    return i in chords[chord]
def transition(i,j):
    order = ["I", "IV", "vi", "V7"]
    vals = [[0,2,3,5],[2,0,4,4],[5,3,0,2],[1,6,3,0]]
    #vals = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    return vals[order.index(i)][order.index(j)]


def harmony(pitches):
    chords = {"I":[0,4,7],"IV":[5,9,0],"vi":[9,0,4],"V7":[7,11,2,5]}
    states = ["I", "IV", "vi", "V7"]
    do, tonality = find_key(pitches)
    assert(tonality == 'major')
    scaled = [(guy-do)%12 for guy in pitches]
    harm = viterbi(scaled, states, valid, transition)
    return [[(do + boi)%12 for boi in chords[guy]] for guy in harm]


def harmonize(notes):
    pitches = []
    for guy in notes:
        if guy[1] != 0:
            pitches.append(guy[1])
    stuff = harmony(pitches)
    bass = [pitches[0]-12-(pitches[0]%12)+stuff[0][0] if stuff[0][0]<=pitches[0]%12 else pitches[0]-24-(pitches[0]%12)+stuff[0][0]]
    for i in range(1, len(pitches)):
        change = (stuff[i][0]-stuff[i-1][0])%12
        if bass[-1]+change <= pitches[i]-12:
            bass.append(bass[-1]+change)
        else:
            bass.append(bass[-1]+change-12)
    x = pitches[0] % 12
    used = []
    for guy in stuff[0][:3]:
        if guy != x:
            use = pitches[0]-x+guy
            if use > pitches[0]:
                use -= 12
            used.append(use)
    used.sort()
    tenor = [used[0]]
    alto = [used[1]]
    for i in range(1, len(pitches)):
        tenchange = [guy - tenor[-1]%12 for guy in stuff[i]]
        altchange = [guy - alto[-1]%12 for guy in stuff[i]]
        tenchange = sorted([(guy+6)%12-6 for guy in tenchange], key=abs)
        altchange = sorted([(guy+6)%12-6 for guy in altchange], key=abs)
        propten = tenor[-1]+tenchange[0]
        propalt = alto[-1]+altchange[0]
        if propten != propalt:
            tenor.append(propten)
            alto.append(propalt)
        else:
            if tenchange[1] <= altchange[1]:
                tenor.append(tenor[-1]+tenchange[1])
                alto.append(propalt)
            else:
                tenor.append(propten)
                alto.append(alto[-1]+altchange[1])
    bass_notes = []
    alt_notes = []
    ten_notes = []
    ind = 0
    for i in range(len(notes)):
        if notes[i][1] != 0:
            bass_notes.append((notes[i][0], bass[ind]))
            alt_notes.append((notes[i][0], alto[ind]))
            ten_notes.append((notes[i][0], tenor[ind]))
            ind+=1
        else:
            bass_notes.append((notes[i][0],0))
            alt_notes.append((notes[i][0], 0))
            ten_notes.append((notes[i][0], 0))
    return [notes,bass_notes,alt_notes,ten_notes]
    
    

# twinkle = [0,0,7,7,9,9,7,5,5,4,4,2,2,0]
# row = [0,0,0,2,4,4,2,4,5,7,0,0,0,7,7,7,4,4,4,0,0,0,7,5,4,2,0]
# ode = [4,4,5,7,7,5,4,2,0,0,2,4,4,2,2,4,4,5,7,7,5,4,2,0,0,2,4,2,0,0]

# mayday = [(240,0),(120,66),(120,66),(240,66),(120,64),(120,64),(240,64),(120,61),(120,61),
#                   (120,61),(120,59),(240,61),(180,58),(60,56),(1200,58),(480,0),
#                   (240,0),(120,66),(120,66),(240,66),(120,64),(120,64),(240,64),(120,61),(120,61),
#                   (240,61),(240,64),(180,66),(60,64),(1200,66),(360,0),(120,66),
#                   (120,66),(120,68),(120,68),(120,66),(120,66),(120,68),(960,68),(120,0),(120,66),
#                   (120,66),(120,68),(120,68),(120,66),(120,66),(120,71),(240,70),(240,68),(240,0),(480,66),
#                   (240,0),(120,66),(120,66),(240,66),(120,64),(120,64),(240,64),(120,61),(120,61),
#                   (120,61),(120,59),(240,61),(180,58),(60,56),(1200,58),(480,0)]
# mayday = [guy[1] for guy in mayday if guy[1] > 0]
# # print(find_key(mayday))
# # print(find_key(twinkle))
# # print(find_key(row))
# # print(find_key(ode))
# stars = [65,62,58,62,65,70,74,72,70,62,64,65,65,65,74,72,70,69,67,69,70,70,65,62,58,
#          65,62,58,62,65,70,74,72,70,62,64,65,65,65,74,72,70,69,67,69,70,70,65,62,58,
#          74,74,74,75,77,77,75,74,72,74,75,75,75,74,72,70,69,67,69,70,62,64,65,
#          65,70,70,70,69,67,67,67,72,74,75,74,72,70,70,69,
#          65,65,70,72,74,75,77,70,72,74,75,72,70]
# #print(find_key(stars))
# sphere = [67,65,70,68,67,65,63,60,62,60,59]
# #print(find_key(sphere))
# arpeg = [79,75,72,67,63,60,59,62,67,71,74,79,79,76,72,67,64,61,60,65,68,72,77,80,
#          80,77,72,68,65,62,60,63,67,72,75,79,81,78,72,69,66,60,59,62,67,71,79]
# #print(find_key(arpeg))
# birth = [60,60,62,60,65,64,60,60,62,60,67,65,60,60,72,69,65,64,62,70,70,69,65,67,65]
# birth_notes = [(20000,guy) for guy in birth]
# #print(find_key(birth))
# anim = [67,68,67,66,67,60,63,62,63,62,60,62,59,55,60,61,60,59,60,64,67,60,70,68,67,65,
#         65,67,65,64,65,68,67,62,65,63,62,60,59,60,63,67,72,74,75,74,72,72,70,70,68,68,66,67,67,68,67]
# #print(find_key(anim))

#print(harmony(birth))
# print(harmonize(birth_notes)[3])
# #print(viterbi(row, states, valid, transition))