import random

        
def viterbi(vals, states, valid, transition, weight):
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
    dists[0] = [valid(vals[0],guy) for guy in states]
    for i in range(1, n):
        for j in range(k):
            sml = inf
            prev = []
            for l in range(k): # check all possible previous states
                dist = dists[i-1][l] + weight * transition(states[l], states[j])
                if dist < sml:
                    sml = dist
                    prev =[l]
                elif dist == sml:
                    prev.append(l)
            dists[i][j] = sml + valid(vals[i], states[j])
            prevs[i][j] = prev[0] #random.choice(prev)
    path = [dists[-1].index(min(dists[-1]))]
    for i in range(n-1, 0, -1): #reconstruct path of states
        path.append(prevs[i][path[-1]])
    return [states[guy] for guy in path[::-1]]

def dot(x,y): # dot product
    return sum(x[i]*y[i] for i in range(len(x)))
def find_key(vals):
    # these are weights assigned to each of the 12 possible notes
    major = [10,-14,5,-12,8,5,-6,8,-6,4,-8,6]
    minor = [9,-9,3,7,-8,3,-8,7,3,-9,0,2]
    vals = [guy % 12 for guy in vals]
    counts = [0,0,0,0,0,0,0,0,0,0,0,0] #frequency of each note
    for guy in vals:
        counts[guy]+=1
    big = 0
    do = None
    tonality = None
    for i in range(12):
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


def major_valid(i, notes): # weight of a chord in major
    if i not in notes:
        return float('inf')
    weights = [10,-14,5,-12,8,5,-6,8,-6,4,-8,6]
    return -sum(weights[i] for i in notes)
def minor_valid(i, notes): #weight of a chord in minor
    if i not in notes:
        return float('inf')
    weights = [9,-9,3,7,-8,3,-8,7,3,-9,0,2]
    return -sum(weights[i] for i in notes)
def transition(i,j): # "distance" between two consecutive chords (smaller is more favorable)
    if i == j:
        return -1
    if (i[1] - i[0])%12 == 4 and (i[0] - j[0])%12 == 7:
        return -1
    else:
        return 0

def shift(nums, ind):
    return tuple((i+ind)%12 for i in nums)
def harmony(pitches, dominant_tonic): #dominant tonic is how much we favor dominant-tonic motion
    states = [shift([0,4,7], i) for i in range(12)] + [shift([0,3,7], i) for i in range(12)] #all major and minor chords
    do, tonality = find_key(pitches)
    valid = minor_valid if tonality == 'minor' else major_valid
    scaled = [(guy-do)%12 for guy in pitches]
    harm = viterbi(scaled, states, valid, transition, dominant_tonic)
    return [[(do + boi)%12 for boi in guy] for guy in harm] #shift back to correct key


def harmonize(notes, dominant_tonic=1000, brange=(36,54), trange=(52,64), arange=(56,68)):
    pitches = []
    for guy in notes:
        if guy[1] != 0:
            pitches.append(guy[1])
    stuff = harmony(pitches, dominant_tonic)
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
# # print(find_key(mayday))
# # print(find_key(twinkle))
# # print(find_key(row))
#print(find_key(ode))
#stars = [65,62,58,62,65,70,74,72,70,62,64,65,65,65,74,72,70,69,67,69,70,70,65,62,58]#,
          # 65,62,58,62,65,70,74,72,70,62,64,65,65,65,74,72,70,69,67,69,70,70,65,62,58,
          # 74,74,74,75,77,77,75,74,72,74,75,75,75,74,72,70,69,67,69,70,62,64,65,
          # 65,70,70,70,69,67,67,67,72,74,75,74,72,70,70,69,
          # 65,65,70,72,74,75,77,70,72,74,75,72,70]
# #print(find_key(stars))
# sphere = [67,65,70,68,67,65,63,60,62,60,59]
# #print(find_key(sphere))
# arpeg = [79,75,72,67,63,60,59,62,67,71,74,79,79,76,72,67,64,61,60,65,68,72,77,80,
#          80,77,72,68,65,62,60,63,67,72,75,79,81,78,72,69,66,60,59,62,67,71,79]
# print(find_key(arpeg))
#birth = [60,60,62,60,65,64,60,60,62,60,67,65,60,60,72,69,65,64,62,70,70,69,65,67,65]
#birth_notes = [(1,guy) for guy in birth]
# #print(find_key(birth))
# anim = [67,68,67,66,67,60,63,62,63,62,60,62,59,55,60,61,60,59,60,64,67,60,70,68,67,65,
#         65,67,65,64,65,68,67,62,65,63,62,60,59,60,63,67,72,74,75,74,72,72,70,70,68,68,66,67,67,68,67]
# #print(find_key(anim))
#print(harmony(stars, 1000))
#print(harmony(birth, 1000))
# x=harmonize(ode_notes, 1000)
# print(x[0])
# print(x[1])
# print(x[2])
# print(x[3])
# #print(viterbi(row, states, valid, transition))