# -*- coding: utf-8 -*-
"""NewApproach.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JY3_nUk0OHL5WpQQtodVx6_jZngi4uoT
"""

import os
import glob
import random
import sys
from typing import *

class Mutagen:
    def __init__(self, patterns:List[str]=None, actions:List[str]=None):
        self.patterns = patterns or []
        self.actions  = actions or []
    
    def load_mutagen(self, filename:str):
        with open(filename) as handle:
            for line in handle:
                line = line.strip()
                if '@' not in line: continue
                
                pattern, action = line.split('@')
                
                self.patterns.append(pattern)
                self.actions.append(action)
    
    def match(self, s:str, pattern:str) -> int:
        l = pattern.split(';')
        
        for i in range(len(s) - len(l)):
            
            for j, pattern_ch in enumerate(l):
                if s[i+j] not in pattern_ch:
                    break
            else:
                return i
        
        return -1
 
    def mutate(self, genome:str, m:int) -> str:
        length  = len(genome)
        mutable = list(genome)
        
        for numMutations in range(m):
            start = random.randint(0, length)
            rotated_genome = (mutable[start:] + mutable[:start]) * 2
            
            pattern_action_pairs = list(zip(self.patterns, self.actions))
            random.shuffle(pattern_action_pairs)
            
            for pattern, action in pattern_action_pairs:
                k = self.match(rotated_genome, pattern)
                
                # Mutation pattern not found
                if k == -1: continue
                tmp_idx = (start+k) % length
                
                # Apply action
                new_mutable = mutable[:]
                for j, ach in enumerate(action):
                    idx = (start + k + j) % length
                    
                    if '0' <= ach <= '9':
                        new_mutable[idx] = mutable[(start + k + int(ach))%length]
                    else:
                        new_mutable[idx] = ach
                
                if new_mutable != mutable:
                    mutable = new_mutable
                    break
                
            else:
                # Never broke out of loop, meaning no change was done
                self.num_mutations = numMutations;
                return ''.join(mutable)
        
        self.num_mutations = m;
        return ''.join(mutable)
    
    def getNumberOfMutations(self) -> int:
        return self.num_mutations
    
    def add(self, pattern:str, action:str):
        self.patterns.append(pattern)
        self.actions.append(action)
    
    def remove(self, i:int):
        if i>0 and i<patterns.size():
            self.patterns.remove(i)
            self.actions.remove(i)
    
    def getPatterns(self): return self.patterns
    def getActions(self): return self.actions
    def getPatternActionPairs(self):
        return [f"{pattern}@{action}" for pattern, action in zip(self.patterns, self.actions)]
    
    def __eq__(self, other):
        if len(self.patterns) != len(other.patterns):
            return False
        
        return set(self.getPatternActionPairs()) == set(other.getPatternActionPairs())

    def translate(c:str) -> int:
        return {'a':0, 'c':1, 'g':2, 't':3}.get(c, -1)

def visualize_change(genome, mutated):
    for idx, (c1, c2) in enumerate(zip(genome, mutated)):
        print(c1 if c1==c2 else f"\x1b[31m{c1}\x1b[0m", end='')
        if idx % 100 == 99: print()
    
    print()
    for idx, (c1, c2) in enumerate(zip(genome, mutated)):
        print(c1 if c1==c2 else f"\x1b[32m{c2}\x1b[0m", end='')
        if idx % 100 == 99: print()
    
    if len(genome) % 100 != 0:
        print()

def generate_random_genome(length=1000):
    return ''.join(['actg'[random.randint(0,3)] for _ in range(length)])

def convert(x):
    return ''.join(y if f"{y}" in "actg" else '0123456789ABCDEFGHIJ'[y] for y in x) or "_"

def convert_hypothesis(hypothesis):
    return " ".join([convert(tmp) for tmp in hypothesis])

def intersect(action1, action2):
    return [a1.intersection(a2) for a1, a2 in zip(action1, action2)]

def parse_offset(elements, offset):
    offset = abs(offset)
    return set(e if isinstance(e, str) else e-offset for e in elements if isinstance(e, str) or (e>=offset and e<offset+10))

def action_potential(action):
    prod = 1
    for ch in action: prod *= len(ch)
    return prod

def hack_action(enumidxes, ch):
    if isinstance(ch, str) and len(ch)==1:
        return set(enumidxes[ch])
    
    tmp = set()
    for c in ch:
        for t in enumidxes[c]:
            tmp.add(t)
    return tmp
    
def get_action(before, after):
    enumidxes = {}
    for key in 'acgt':
        enumidxes[key] = [key] + [i for i, ch in enumerate(before) if (isinstance(ch, str) and ch==key) or (isinstance(ch, set) and key in ch)]
#         key: [key] + [i for i, ch in enumerate(before) if ch==key] for key in 'actg'}
    
    return [hack_action(enumidxes, ch) for ch in after]

mask = {'a':1, 'c':2, 'g':4, 't':8}
lens = [(i&1)+((i&2)>>1)+((i&4)>>2)+((i&8)>>3) for i in range(16)]

def get_pattern(before):
    return [mask[ch] for ch in before]

def union_pattern(pattern1, pattern2):
    return [p1|p2 for p1, p2 in zip(pattern1, pattern2)]

def get_offset(idx1, idx2):
    offset = None
    
    # idx1, idx2 should already be sorted by (exp, idx) format
    for (e1, i1), (e2, i2) in zip(idx1, idx2):
        if offset is None and e1==e2:
            offset = i2 - i1
        elif e1==e2:
            if i2-i1 != offset:
                return None
    
    return offset
            
    
def reduce_hypothesis(actionlist):
    """ Isomorphisms are hard to detect """
    newactionlist = []
    for actions1 in actionlist:
        action1, pattern1, idxes1 = actions1
        
        for nalidx, actions2 in enumerate(newactionlist):
            action2, pattern2, idxes2 = actions2
            
            offset = get_offset(idxes1, idxes2)
            if offset is None:
                continue
            
            
            offseta = abs(offset)            
            for i in range(offseta, 10-offseta):
                if offset < 0:
                    if pattern1[i] != pattern2[i+offseta]: break
                    if action1[i]  != parse_offset(action2[i+offseta], offseta): break
                else:
                    if pattern2[i] != pattern1[i+abs(offset)]: break
                    if action2[i]  != parse_offset(action1[i+offseta], offseta): break
            else:
                if offset < 0:
                    newactionlist[nalidx] = actions1
                break
        else:
            newactionlist.append(actions1)
        
    return newactionlist

def find_intervals(genome, result, mp):
    if mp == 0: return []
    
    diffs = [idx for idx, (c1, c2) in enumerate(zip(genome, result)) if c1 != c2]
    
    intervals = []
    
    startidx = None
    for d in diffs:
        if startidx is None:
            startidx, curidx = d, d
        
        elif d - curidx < 10:
            curidx = d
        
        else:
            intervals.append((startidx, curidx))
            startidx, curidx = d, d
    
    intervals.append((startidx, curidx))
    return intervals

def reduce_hypothesis(actionlist):
    """ Isomorphisms are hard to detect """
    newactionlist = []
    for actions1 in actionlist:
        action1, pattern1, idxes1 = actions1
        
        for nalidx, actions2 in enumerate(newactionlist):
            action2, pattern2, idxes2 = actions2
            
            offset = get_offset(idxes1, idxes2)
            if offset is None:
                continue
            
            
            offseta = abs(offset)            
            for i in range(offseta, 10-offseta):
                if offset < 0:
                    if pattern1[i] != pattern2[i+offseta]: break
                    if action1[i]  != parse_offset(action2[i+offseta], offseta): break
                else:
                    if pattern2[i] != pattern1[i+abs(offset)]: break
                    if action2[i]  != parse_offset(action1[i+offseta], offseta): break
            else:
                if offset < 0:
                    newactionlist[nalidx] = actions1
                break
        else:
            newactionlist.append(actions1)
        
    return newactionlist

def new_approach_one(genome, result):
    l = len(genome)
    
    possible_hypothesis = []
    
    for idx in range(l - 9):
        action = get_action(genome[idx:idx+10], result[idx:idx+10])
        
        if action_potential(action) > 0:
            possible_hypothesis.append((action, idx))
    
    return possible_hypothesis

def new_approach_two(genome, result):
    l = len(genome)
    
    alldiffs = set(idx for idx, (c1, c2) in enumerate(zip(genome, result)) if c1 != c2)
    
    enumidxes = {}
    for key in 'atcg':
        enumidxes[key] = [key] + [i for i, ch in enumerate(genome) if ch==key]
    
    separate_actions = []
    for idx1 in range(l-19):
        remdiff1 = set(i for i in alldiffs if not idx1<=i<idx1+10)
        if len(remdiff1) > 10 or max(remdiff1)-min(remdiff1) > 10: continue

        action1  = [parse_offset(enumidxes[ch], idx1) for ch in result[idx1:idx1+10]]        
        
        for idx2 in range(idx1+10, l-9):
            
            # If the two windows don't cover all differences, it cannot be possible
            remdiff2 = set(i for i in remdiff1 if not idx2<=i<idx2+10)
            if len(remdiff2) > 0: continue

            action2  = [parse_offset(enumidxes[ch], idx2) for ch in result[idx2:idx2+10]]
            action   = intersect(action1, action2)
            
            # Check if the intersection is possible
            if set() not in action:
                # Add to possible actions
                separate_actions.append((action, (idx1, idx2)))

    combined_actions = []
    for idx1 in range(l-9):
        remdiff1 = set(i for i in alldiffs if not idx1<=i<idx1+10)
        if len(remdiff1) > 10 or (remdiff1 and max(remdiff1)-min(remdiff1) > 10): continue
            
        for idx2 in range(max(0, idx1-9), min(l-9, idx1+10)):
            # If the two windows don't cover all differences, it cannot be possible
            remdiff2 = set(i for i in remdiff1 if not idx2<=i<idx2+10)
            if len(remdiff2) > 0: continue
            
            minidx, maxidx = min(idx1, idx2), max(idx1, idx2)
            intersection_idxes = set(range(maxidx, minidx+10))
            
            idx1off = idx1 - minidx
            idx2off = idx2 - minidx
            
            before = [genome[i] for i in range(minidx, maxidx+10)]
            middle = [set('actg') for i in range(minidx, maxidx+10)]
            after  = [result[i] for i in range(minidx, maxidx+10)]
            
            for i in range(10):
                if i+idx1 not in intersection_idxes:
                    middle[i+idx1-minidx] = after[i+idx1-minidx]

                if i+idx2 not in intersection_idxes:
                    middle[i+idx2-minidx] = before[i+idx2-minidx]

            for i in range(20):
                action1 = get_action(before[idx1-minidx:idx1-minidx+10], middle[idx1-minidx:idx1-minidx+10])
                action2 = get_action(middle[idx2-minidx:idx2-minidx+10], after [idx2-minidx:idx2-minidx+10])

                action   = intersect(action1, action2)

                if action_potential(action) == 0:
                    break

                prev_middle = middle[:]
                
                # Check overlaps calculated from before
                for i in range(minidx + 10 - maxidx):
                    from_before = set(before[dst+idx1-minidx] for dst in action[i+maxidx-idx1] if isinstance(dst, int))
                    middle[i+maxidx-minidx] = from_before.intersection(middle[i+maxidx-minidx])
                    
                    # Convert set to character if possible
                    if len(middle[i+maxidx-minidx]) == 1:
                        middle[i+maxidx-minidx] = list(middle[i+maxidx-minidx])[0]

                # Check overlaps calculated from after
                for i in range(10):
                    if len(action[i]) != 1: continue
                    
                    src = list(action[i])[0]
                    if isinstance(src, str): continue
                        
                    if after[i + (idx2 - minidx)] not in middle[src+idx2-minidx]: # Handle both str and set()
                        middle[src+idx2-minidx] = set()
                    else:
                        middle[src+idx2-minidx] = after[i + (idx2 - minidx)]
                
                if prev_middle == middle: break
                        
            if action_potential(action) == 0: continue

            combined_actions.append((action, (idx1, idx2)))

    return separate_actions + combined_actions

"""# Main test script"""

memory = []
genomes = (sys.argv[1]).strip('][').split(',')
mutatedGenomes = (sys.argv[2]).strip('][').split(',')
numMutationsList = (sys.argv[3]).strip('][').split(',')

# mute = Mutagen()
# mute.add('t;a;g', '9123456780')
# m = 10

for experiment in range(100):
    genome = genomes[experiment]
    result = mutatedGenomes[experiment]
    mp = int(numMutationsList[experiment])
# for experiment in range(10):
#     genome = generate_random_genome()
#     result = mute.mutate(genome, m)
#     mp = mute.getNumberOfMutations()

#     print(f"[{mp}/{m}] mutation(s) found")
    
    # Rotate if necessary
    diffs = [idx for idx, (c1, c2) in enumerate(zip(genome, result)) if c1 != c2]
    if len(diffs) == 0: continue
    
    if diffs[-1] > 990: # Possibility of a rollover
        for i in range(len(diffs)-1):
            if diffs[i+1] - diffs[i] > 20:
                genome = genome[diffs[i]+10:] + genome[:diffs[i]+10]
                result = result[diffs[i]+10:] + result[:diffs[i]+10]
                break

    intervals = find_intervals(genome, result, mp)

    num_mutations = [1 + (d2-d1)//10 for (d1, d2) in intervals]
    cap_mutations = [(num_mutation, num_mutation + mp - sum(num_mutations)) for num_mutation in num_mutations]
    
#     print(intervals, len(intervals))
#     print(num_mutations)
#     print(cap_mutations)

    min_cap = min(d2 for _, d2 in cap_mutations)
    max_cap = max(d2 for _, d2 in cap_mutations)
    # print(f"[{mp:2d}/{m:2d}] mutation(s) found ({len(intervals):2d}) [{min_cap}, {max_cap}]", intervals)

    memory.append((min_cap, max_cap, genome, result, mp))
    
memory = sorted(memory)

actionlist = None

for experiment, (min_cap, max_cap, genome, result, mp) in enumerate(memory):
    # print("RUNNING EXPERIMENT : ", experiment, min_cap, max_cap)
    
    if max_cap > 1: continue
    
    intervals = find_intervals(genome, result, mp)

    num_mutations = [1 + (d2-d1+1)//10 for (d1, d2) in intervals]
    cap_mutations = [(num_mutation, num_mutation + mp - sum(num_mutations)) for num_mutation in num_mutations]

    # print(intervals)
    # print(cap_mutations)

    for count, ((minM, maxM), (d1, d2), (minc, maxc)) in enumerate(sorted(zip(cap_mutations, intervals, cap_mutations))):
        if maxc > 1: continue
        
        possible_actions = []

        actions = new_approach_one(genome[d2-9 : d1+10], result[d2-9 : d1+10])
        actions = [(a, get_pattern(genome[idx+d2-9 : idx+d1+10]), [(experiment, idx + d2-9)]) for a, idx in actions]

        if actionlist is None:
            actionlist = possible_actions = actions
        else:
            for a1, pattern1, idx1 in actionlist:
                for a2, pattern2, idx2 in actions:
                    action = intersect(a1, a2)
                    if action_potential(action) == 0: continue

                    possible_actions.append((action, union_pattern(pattern1, pattern2), idx1+idx2))

        # actionlist = possible_actions
        # print("Action list debug : ", len(actionlist))
        # visualize_change(genome[d2-9 : d1+10], result[d2-9 : d1+10])

        # for action, pattern, idxs in actionlist:
        #     print(f"[{convert_hypothesis([pattern])}] [{convert_hypothesis(action)}] {idxs}")
        #     for exp, idx in idxs:
        #         visualize_change(genome[idx:idx+10], result[idx:idx+10])
        # print()

        actionlist = reduce_hypothesis(actionlist)

def produce_guess(actionlist):
    answers = set()
    
    for action, pattern, _ in actionlist:
        for i in range(9, -1, -1):
            if lens[pattern[i]] < 3: break
        
        pattern_string = ';'.join(''.join(k for k,v in mask.items() if pat&v) for pat in pattern[:i+1])
        
        for i in range(9, -1, -1):
            if action[i] != {i}: break
        
        action = action[:i+1]
        new_action = [set(a) for a in action]
        for i in range(len(action)):
            for ch in list(action[i]):
                if isinstance(ch, int):
                    if lens[pattern[ch]] == 1:
                        new_action[i].remove(ch)
                        new_action[i].add({1:'a', 2:'c', 4:'g', 8:'t'}[pattern[ch]])
        
        if action_potential(new_action) == 1:
            action_string = ''.join(''.join(map(str,ch)) for ch in new_action)
            answers.add(f"{pattern_string}@{action_string}")
        else:
            for naction in itertools.product(*new_action):
                action_string = ''.join(''.join(map(str,ch)) for ch in naction)
                answers.add(f"{pattern_string}@{action_string}")

    print(len(answers), answers)

produce_guess(actionlist)