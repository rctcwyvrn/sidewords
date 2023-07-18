import itertools
from multiprocessing import Pool
# from tqdm import tqdm
# from tqdm.contrib import *

def get_words(filename):
    return [s.strip().lower() for s in open(filename).readlines()]

wordlist = get_words("/usr/share/dict/words")
# wordlist = get_words("../letter_boxed/english-words/words_alpha.txt")
# wordlist.extend(get_words("additional_words.txt"))
print("Input the two sidewords")
code = input("> ")

# spicy
# code = "searing,poultry"
# code = "botched,guitars"

# others
# code = "alter,best" 
# code = "escort,under"
# code = "slated,surgeon"

print("solving", code)
rows, cols = code.strip().split(",")
pairs = list(itertools.product(rows, cols))

def decompose(word):
    if len(word) <= 2:
        return False
    
    writings = [("","")]

    def add_left(l):
        return [(x+l, y) for x,y in writings]

    def add_right(l):
        return [(x, y+l) for x,y in writings]

    for letter in word:
        if letter in rows and letter in cols:
            writings = add_left(letter) + add_right(letter)
        elif letter in rows:
            writings = add_left(letter)
        elif letter in cols:
            writings = add_right(letter)
        else:
            return False
    
    writings = filter(lambda pair: len(pair[0]) > 0 and len(pair[1]) > 0, writings)

    def substr(base, x):
        counts = {}
        for l in x:
            if l not in counts:
                counts[l] = 1
            else:
                counts[l] += 1
        for l, saw in counts.items():
            if base.count(l) < saw:
                return False
        return True

    # handles words with duplicate letters
    writings = filter(lambda pair: substr(rows, pair[0]) and substr(cols, pair[1]), writings)
    writings = list(writings)

    if len(writings) == 0:
        return False

    return [(w, word) for w in writings]

def parify(decomp):
    writing, _ = decomp
    x,y = writing
    p = list(itertools.product(x,y)) # yes this has to be a list 
    return p

def pairs_in(pairs, decomp):
    uses = parify(decomp)
    return list(filter(lambda p: p in uses, pairs))

game_words = [w for writings in filter(lambda x: x, map(decompose, wordlist)) for w in writings]
shortest = sorted(game_words, key=lambda s: len(s[1]), reverse=False)
longest = sorted(game_words, key=lambda s: len(s[1]), reverse=True)

# for multiprocessing and pickle
def dfs_packed(x):
    return dfs(*x)

def dfs(solution, used):
    # print("> solution", [word for _, word in solution])
    # print("> solution", solution)
    # print("used", used, len(set(used)))
    if len(set(used)) == len(rows) * len(cols):
        print("SOLUTION: ", [word for _, word in solution])
        print("> EXACT: ", solution)
        return solution
    
    # missing one
    if len(set(used)) == (len(rows) * len(cols)) - 1:
        return False

    possible_next = list(filter(lambda word: len(pairs_in(used, word)) == 0, longest))

    # spawn threads breadth first on the first layer
    if len(solution) == 0:
        calls = [(solution + [word], used + pairs_in(pairs, word)) for word in possible_next]
        with Pool(12) as p:
            calls = [(solution + [word], used + pairs_in(pairs, word)) for word in possible_next]
            results = p.map(dfs_packed, calls)
        # results = process_map(dfs_packed, calls, max_workers=12)
        if not any(results):
            return False
        else:
            return list(filter(lambda x: x, results))

    # then go depth first
    for word in possible_next:
        uses = pairs_in(pairs, word)
        res = dfs(solution + [word], used + uses)
        if not res:
            continue
        else:
            return res

dfs([],[])