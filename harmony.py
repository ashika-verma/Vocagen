import random
import numpy as np

        
def viterbi(vals, states, valid, transition):
    """
    vals: list of values, such as the notes in a melody
    states: list of possible states at each timestep
    valid(value, state) is the cost associated with that value-state pair
    transition(state1, state2) is the distance traveled to get from state1 to state2 at consecutive timesteps
    weight is the importance given to the transition distance apposed to the cost from valid()
    
    returns: list of states for best path for vals
    """
    n=len(vals)
    k=len(states)
    # make tables for viterbi
    dists = [[0 for guy in states] for guy in vals]
    prevs = [[0 for guy in states] for guy in vals]
    inf = float('inf')
    dists[0] = [valid(vals[0],guy, False) for guy in states]
    for i in range(1, n):
        for j in range(k):
            sml = inf
            prev = []
            for l in range(k): # check all possible previous states
                dist = dists[i-1][l] + transition(states[l], states[j])
                if dist < sml:
                    sml = dist
                    prev =[l]
                elif dist == sml:
                    prev.append(l)
            dists[i][j] = sml + valid(vals[i], states[j], i==n-1)
            prevs[i][j] = prev[0] #random.choice(prev)
    path = [dists[-1].index(min(dists[-1]))]
    for i in range(n-1, 0, -1): #reconstruct path of states
        path.append(prevs[i][path[-1]])
    return [states[guy] for guy in path[::-1]]

def dot(x,y): # dot product
    return sum(x[i]*y[i] for i in range(len(x)))
def find_key(vals):
    # these are weights assigned to each of the 12 possible notes
    major = [10,-14,5,-12,8,5,-6,9,-6,4,-7,4]
    minor = [10,-9,3,8,-8,3,-8,9,3,-9,0,2]
    vals = [guy % 12 for guy in vals]
    counts = [0,0,0,0,0,0,0,0,0,0,0,0] #frequency of each note
    for guy in vals:
        counts[guy]+=1
    big = 0
    do = None
    tonality = None
    for i in range(12):
        #print(dot(counts, major), dot(counts, minor))
        # check value for each possible key
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


# def major_valid(i, notes): # weight of a chord in major
#     if i not in notes:
#         return float('inf')
#     weights = [10,-14,5,-12,8,5,-6,8,-6,4,-8,6]
#     return -sum(weights[i] for i in notes)
# def minor_valid(i, notes): #weight of a chord in minor
#     if i not in notes:
#         return float('inf')
#     weights = [9,-9,3,7,-8,3,-8,7,3,-9,0,2]
#     return -sum(weights[i] for i in notes)
def pop_maj_valid(i, notes, need_do):
    if i not in notes:
        return float('inf')
    if need_do and notes[:2]==(0,4):
        return -1000
    weights = [100,-20,50,35,65,85,-20,100,55,55,50,-20,
               55,-20,70,-20,65,65,-20,-20,-20,90,-20,-20]
    if (notes[1]-notes[0])%12 == 4:
        return -weights[notes[0]] + np.random.normal(0.0, 30.)
    else:
        return -weights[12+notes[0]] + np.random.normal(0.0, 30.)
def pop_min_valid(i, notes, need_do):
    if i not in notes:
        return float('inf')
    if need_do and notes[:2]==(0,3):
        return -1000
    weights = [60,55,45,100,-20,60,-20,67,88,-20,90,-20,
               100,-20,-20,-20,-20,74,-20,74,-20,-20,-20,-20]
    if (notes[1]-notes[0])%12 == 4:
        return -weights[notes[0]] + np.random.normal(0.0, 30.)
    else:
        return -weights[12+notes[0]] + np.random.normal(0.0, 30.)
def class_maj_valid(i, notes, need_do):
    if i not in notes:
        return float('inf')
    if need_do and notes[:2]==(0,4):
        return -1000
    weights = [100,-20,68,-20,64,85,-20,100,53,55,-20,-20,
               -20,-20,92,-20,54,-20,-20,-20,-20,83,-20,-20]
    if (notes[1]-notes[0])%12 == 4:
        return -weights[notes[0]] + np.random.normal(0.0, 30.)
    else:
        return -weights[12+notes[0]] + np.random.normal(0.0, 30.)
def class_min_valid(i, notes, need_do):
    if i not in notes:
        return float('inf')
    if need_do and notes[:2]==(0,3):
        return -1000
    weights = [64,55,63,86,-20,57,-20,97,83,-20,73,-20,
               100,-20,-20,-20,-20,86,-20,56,-20,-20,-20,-20]
    if (notes[1]-notes[0])%12 == 4:
        return -weights[notes[0]] + np.random.normal(0.0, 30.)
    else:
        return -weights[12+notes[0]] + np.random.normal(0.0, 30.)
def pop_maj_transition(i,j): # "distance" between two consecutive chords (smaller is more favorable)
    if i == j:
        return -200
    if (i[1] - i[0])%12 == 4 and (i[0] - j[0])%12 == 7:
        return -40
    if i[0] == 5 and j[0] == 0:
        return -20
    return 0
def class_maj_transition(i,j):
    if i == j:
        return -70
    if (i[1] - i[0])%12 == 4 and (i[0] - j[0])%12 == 7 and i != 0:
        return -50
    if i[0] == 7 and j[0] == 9 and j[1] == 0:
        return -15
    if i[0] == 2 and j[0] == 7:
        return -30
    if i[0] == 8 and j[0] != 7:
        return 100
    if i[0] == 8:
        return -15
    return 0
def pop_min_transition(i,j):
    if i==j:
        return -200
    if i[0] == 7 and i[1] == 11:
        if j[0] == 0:
            return -10
        if j[0] != 8:
            return 100
    return 0
def class_min_transition(i,j):
    if i == j:
        return -70
    if (i[1] - i[0])%12 == 4 and (i[0] - j[0])%12 == 7:
        return -60
    if i[0] == 1 and j[0] != 7:
        return 100
    if i[0] == 7 and i[1] == 11 and j[0] == 8:
        return -10
    return 0
def shift(nums, ind):
    return tuple((i+ind)%12 for i in nums)

def harmony(pitches, genre): #dominant tonic is how much we favor dominant-tonic motion
    states = [shift([0,4,7], i) for i in range(12)] + [shift([0,3,7], i) for i in range(12)] #all major and minor chords
    do, tonality = find_key(pitches)
    
    if genre == 'pop':
        valid = pop_min_valid if tonality == 'minor' else pop_maj_valid
        transition = pop_min_transition if tonality == 'minor' else pop_maj_transition
    if genre == 'classical':
        valid = class_min_valid if tonality == 'minor' else class_maj_valid
        transition = class_min_transition if tonality == 'minor' else class_maj_transition
    scaled = [(guy-do)%12 for guy in pitches]
    harm = viterbi(scaled, states, valid, transition)
    return [[(do + boi)%12 for boi in guy] for guy in harm] #shift back to correct key


def harmonize(notes, genre = "pop", brange=(36,54), trange=(52,64), arange=(56,68)):
    pitches = []
    for guy in notes:
        if guy[1] != 0:
            pitches.append(guy[1])
    stuff = harmony(pitches, genre)
    voices = [((brange[0]+brange[1])/2, (trange[0]+trange[1])/2, (arange[0]+arange[1])/2)]
    ind=-1
    for chord in stuff:
        ind+=1
        allowed = []
        for i in range(brange[0], brange[1]+1):
            if i%12 == chord[0]:
                for j in range(trange[0], trange[1]+1):
                    if j%12 in chord:
                        for k in range(arange[0], arange[1]+1):
                            if k%12 in chord:
                                if i != j and j != k and i != k and chord[1] in [j%12, k%12, pitches[ind]%12]:
                                    dist = abs(i-voices[-1][0])**2 + abs(j-voices[-1][1])**2 + abs(k-voices[-1][2])**2
                                    allowed.append((dist, i, j, k))
        allowed.sort()
        voices.append(allowed[0][1:])
    bass_notes = []
    alt_notes = []
    ten_notes = []
    ind = 1
    for i in range(len(notes)):
        if notes[i][1] != 0:
            bass_notes.append((notes[i][0], voices[ind][0]))
            alt_notes.append((notes[i][0], voices[ind][2]))
            ten_notes.append((notes[i][0], voices[ind][1]))
            ind+=1
        else:
            bass_notes.append((notes[i][0],0))
            alt_notes.append((notes[i][0], 0))
            ten_notes.append((notes[i][0], 0))
    return [notes,bass_notes,ten_notes,alt_notes]
    
    

# twinkle = [0,0,7,7,9,9,7,5,5,4,4,2,2,0]
# row = [0,0,0,2,4,4,2,4,5,7,0,0,0,7,7,7,4,4,4,0,0,0,7,5,4,2,0]
# ode = [4,4,5,7,7,5,4,2,0,0,2,4,4,2,2,4,4,5,7,7,5,4,2,0,0,2,4,2,0,0]
# ode = [guy+60 for guy in ode]
# ode_notes = [(1,guy) for guy in ode]
# mayday = [(240,0),(120,66),(120,66),(240,66),(120,64),(120,64),(240,64),(120,61),(120,61),
#                   (120,61),(120,59),(240,61),(180,58),(60,56),(1200,58),(480,0),
#                   (240,0),(120,66),(120,66),(240,66),(120,64),(120,64),(240,64),(120,61),(120,61),
#                   (240,61),(240,64),(180,66),(60,64),(1200,66),(360,0),(120,66),
#                   (120,66),(120,68),(120,68),(120,66),(120,66),(120,68),(960,68),(120,0),(120,66),
#                   (120,66),(120,68),(120,68),(120,66),(120,66),(120,71),(240,70),(240,68),(240,0),(480,66),
#                   (240,0),(120,66),(120,66),(240,66),(120,64),(120,64),(240,64),(120,61),(120,61),
#                   (120,61),(120,59),(240,61),(180,58),(60,56),(1200,58),(480,0)]
# mayday = [guy[1] for guy in mayday if guy[1] > 0]
# print(find_key(mayday))
# print(find_key(twinkle))
# print(find_key(row))
# print(find_key(ode))
#stars = [65,62,58,62,65,70,74,72,70,62,64,65,65,65,74,72,70,69,67,69,70,70,65,62,58]#,
           # 65,62,58,62,65,70,74,72,70,62,64,65,65,65,74,72,70,69,67,69,70,70,65,62,58,
           # 74,74,74,75,77,77,75,74,72,74,75,75,75,74,72,70,69,67,69,70,62,64,65,
           # 65,70,70,70,69,67,67,67,72,74,75,74,72,70,70,69,
           # 65,65,70,72,74,75,77,70,72,74,75,72,70]
#print(find_key(stars))
# sphere = [67,65,70,68,67,65,63,60,62,60,59]
# print(find_key(sphere))
# arpeg = [79,75,72,67,63,60,59,62,67,71,74,79,79,76,72,67,64,61,60,65,68,72,77,80,
#          80,77,72,68,65,62,60,63,67,72,75,79,81,78,72,69,66,60,59,62,67,71,79]
#print(find_key(arpeg))
#birth = [60,60,62,60,65,64,60,60,62,60,67,65,60,60,72,69,65,64,62,70,70,69,65,67,65]
#borth = [60,60,61,60,65,64,60,60,61,60,67,65,60,60,72,68,65,63,61,70,70,68,65,67,65]
#birth_notes = [(1,guy) for guy in birth]
#print(find_key(birth))
# anim = [67,68,67,66,67,60,63,62,63,62,60,62,59,55,60,61,60,59,60,64,67,60,70,68,67,65,
#          65,67,65,64,65,68,67,62,65,63,62,60,59,60,63,67,72,74,75,74,72,72,70,70,68,68,66,67,67,68,67]
# print(find_key(anim))
# # print(harmony(anim, 50))
# bad = [55,62,58,61,62,61,58,60,67,63,66,67,66,63,62,69,62,66,62,60,62,55]
# print(find_key(bad))
# print(harmony(bad, 'hi'))
# legends = [59,57,56,59,60,52,64,62,60,59,57,60,59]
# print(find_key(legends))
#print(harmony(stars, 1000))
#print(harmony(birth, 'classical'))
#print(find_key(borth))
#print(harmony(borth, 'classical'))
#print(harmony(arpeg, 50))
# x=harmonize(ode_notes, 1000)
# print(x[0])
# print(x[1])
# print(x[2])
# print(x[3])
# #print(viterbi(row, states, valid, transition))