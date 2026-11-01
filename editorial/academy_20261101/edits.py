"""Authored text for this pass. apply_pass.py turns these tables into lesson edits."""

# Full replacement of `algorithm.task`, and through it of `writing.task`,
# `concept`, `summary`, `rule` and both starter comments on the challenge step.
TASKS = {
    'index-map': 'Return the shortest distance between two equal values, or -1 when no value repeats.',
    'equilibrium-index': 'Return the first index whose strict left and right sums match, or -1 when no such index exists.',
    'randomized-set': 'Tokens addN and removeN arrive separated by spaces. Adding a value already present and removing an absent value change nothing. Apply them to dense vector storage, then return the remaining values sorted ascending, or an empty string when nothing remains.',
    'difference-array': 'Parse n and inclusive (l,r,delta) updates on a zero-filled array of length n; delta may be negative. Apply every update and return the final array.',
    'list-cycle': 'Parse values plus one link form: tail->k (the last node links to zero-based node k), tail->none, or next=[...] (each node\'s next index or none). Starting from node 0, return whether following links ever repeats a node. An empty list has no cycle. Compare node indexes, not values.',
    'rotated-search': 'Return the index of 0 in the rotated sorted array of distinct values, or -1 if 0 is absent.',
    'first-last-position': 'Return the first and last index of 8 in the sorted values as first,last, or -1,-1 if 8 is absent.',
    'exponential-search': 'Return the index of 21 in the ascending values using exponential bracketing, or -1 if 21 is absent.',
    'gas-station': 'Return the smallest valid starting station, or -1 when no start completes the circuit.',
    'dfs-topological': 'Parse n and directed edges a->b. Run DFS from vertices in ascending order, visit each vertex\'s neighbors in ascending order, and return the reverse of the finishing order.',
    'kth-stream': 'Parse the integer stream, written [...] with an optional stream= prefix. With k=3, return the third largest value after each insertion, starting once three values have arrived.',
    'tree-dp': 'Parse the compact level-order binary tree, written [...] with an optional tree= prefix, where null omits a node. Return the maximum sum of chosen nodes when no parent and child are both chosen.',
    'rolling-dp': 'Parse cost=[...]. Start on stair 0 or stair 1. Landing on a stair pays its cost, and from there you move up one or two stairs. Return the minimum total cost to move beyond the final stair.',
    'min-stack': 'Tokens pushN, pop and a final min arrive separated by spaces. Apply them in order and return the minimum of the remaining stack at min. The stack is nonempty at every pop and at min.',
    'tree-preorder': 'Parse the compact level-order binary tree, where null omits a node. Return its preorder values.',
    'tree-inorder': 'Parse the compact level-order binary tree, where null omits a node. Return its inorder values; the tree need not be a BST.',
    'tree-postorder': 'Parse the compact level-order binary tree, where null omits a node. Return its postorder values.',
    'tree-level-order': 'Parse the compact level-order binary tree, where null omits a node. Return the sum of each level from the root downward.',
    'tree-diameter': 'Parse the compact level-order binary tree, where null omits a node. Return the diameter measured in edges; the longest path need not pass through the root.',
    'container-area': 'Each value is a wall height at its index. Walls i<j hold area (j-i)*min(height[i],height[j]). Return the greatest area.',
    'variable-window': 'For positive values, return the minimum length of a contiguous subarray with sum at least 7, or 0 when no such subarray exists.',
    'selection-sort': 'Sort ascending with classic selection sort, choosing the first occurrence of the minimum in each pass, and return the count of exchanges between different positions. Do not count self-swaps.',
    'lower-bound': 'Return the first index whose value is at least 4, or the array length when every value is below 4.',
    'upper-bound': 'Return the first index whose value is greater than 4, or the array length when no value is greater.',
    'connected-components': 'Parse n and undirected edges; edges= with nothing after it and edges=none both mean no edges. Return the number of connected components, counting isolated vertices.',
    'graph-dfs': 'Edges are undirected, and vertices run from 0 to the largest endpoint. Return recursive DFS order from node 0 using ascending neighbors.',
    'graph-bfs': 'Parse n and undirected edges. Return the distance in edges from node 0 to every node in vertex order, or -1 for an unreachable node.',
    'dijkstra': 'Edges a-b:w are undirected with nonnegative weights, and vertices run from 0 to the largest endpoint. Return shortest distances from node 0 in vertex order, or -1 for an unreachable node.',
    'zero-one-bfs': 'Edges a-b:w are undirected with weight 0 or 1. Return the minimum cost from 0 to 3.',
    'bellman-ford': 'Edges a->b:w are directed and may be negative, with no reachable negative cycle, and they arrive in any order; vertices run from 0 to the largest endpoint. Return shortest distances from 0 in vertex order, or -1 for an unreachable vertex.',
    'dag-shortest-path': 'Edges a->b:w form a directed acyclic graph and may be negative. Return the shortest distance from 0 to 4.',
    'kahn-topological': 'Parse n and directed edges a->b. Return the lexicographically smallest valid topological order.',
    'floyd-warshall': 'Matrix entries are directed edge weights and inf means no edge. Return the shortest distance from 0 to 2.',
    'dinic-max-flow': 'Edges a->b:c are directed with capacity c. Return the maximum flow from 0 to 3.',
    'bipartite-coloring': 'Parse n and undirected edges; the graph may be disconnected. Return whether it can be two-colored.',
    'undirected-cycle': 'Edges are undirected, and vertices run from 0 to the largest endpoint; the graph may be disconnected and has no self-loops or parallel edges. Return whether it contains a cycle.',
    'merge-intervals': 'The closed intervals may arrive unsorted. Return them merged in ascending order; touching endpoints merge.',
    'activity-selection': 'The meetings may arrive in any order, and one ending at t is compatible with one starting at t. Return the maximum number of compatible meetings.',
    'meeting-rooms-heap': 'A room freed at time t can host a meeting starting at t. Return the minimum rooms required.',
    'minimum-arrows': 'A point hits every closed interval containing it. Return the minimum points needed to hit all intervals.',
    'bidirectional-map': 'Return whether pattern letters map one-to-one onto the words.',
    'delimiter-stack': 'Return whether the delimiters are correctly nested.',
    'hash-frequency': 'Return whether the two lowercase words have identical character counts.',
    'hash-membership': 'Return whether any badge ID occurs more than once.',
    'matrix-binary-search': 'Return whether 16 is present.',
    'meet-in-middle': 'Return whether a subset sums to 15.',
    'opposite-ends': 'Return whether two different positions of the sorted values sum to 10.',
    'string-two-pointers': 'Ignore non-alphanumeric ASCII and case; return whether the text is a palindrome.',
    'tree-height-balance': 'Parse the compact level-order binary tree, where null omits a node. Return whether every subtree has child heights differing by at most one.',
    'bucket-sort': 'Values are decimals in [0,1). Distribute them into n buckets by floor(n*x), where n is the input length, sort each bucket, and return all values ascending.',
    'radix-sort': 'Sort the nonnegative integers, each fitting u32, in ascending order with stable least-significant-digit passes. The worked program uses 8-bit digits; any digit base that reaches every digit works.',
    'kruskal-mst': 'The undirected graph on vertices 0 to the largest endpoint is connected. Return the weights of the edges Kruskal selects, in selection order: ascending weight, ties by smaller endpoints.',
    'lazy-heap-deletion': 'Tokens pushN, deleteN and a final min arrive separated by spaces. deleteN removes one occurrence of a value that is live at that moment. Return the smallest live value at min, or none when nothing is live.',
    'combinations': 'The values are in strictly ascending order. Return all size-two combinations in lexicographic order, or an empty string when fewer than two values exist.',
    'combination-sum': 'Return the unique nondecreasing combinations summing to 7, commas within a combination and semicolons between them, in ascending lexicographic order. A candidate may repeat within a combination. Return an empty string when none exists.',
    'min-max-tracking': 'Return max - min for the sensor readings. Readings are 32-bit signed integers, so the difference can need 64 bits.',
    'treap': 'Apply the space-separated insertN and deleteN tokens, then return the keys ascending at inorder. Keys form a set: inserting a present key and deleting an absent key change nothing.',
    'deadline-scheduling': 'Each job takes one time slot and earns its profit only if it runs in a slot no later than its 1-based deadline. Return the maximum total profit.',
    'remove-nth-from-end': 'Remove the second node from the end of a list with at least two nodes and return the remaining values.',
    'copy-random-list': 'Parse values, random (each a node index or null) and optional next (each node\'s next index or none; when absent, nodes link in array order). Every node is reachable from node 0. Deep-copy the list, following next, with an old-to-new map. Return value:target for each copied node in list order, where target is the random node\'s position in the copied list, or null. Values may repeat, so identify nodes by index.',
    'rolling-fingerprint': 'Parse digits in 0..9; leading zeros are allowed. Keep a window of the last three digits, or fewer before three have arrived. Maintain hash=(hash*10+digit)%101 for the window, removing the outgoing digit\'s contribution, and return the final window\'s hash.',
    'rolling-window-statistic': 'For each window of length three, return the mean rounded down, toward negative infinity. For input written variance=[...], return each window\'s population variance rounded down instead.',
    'tree-serialize': 'Given tree=[...], a compact level-order tree where null omits a node, serialize it in preorder using comma separators and # for every missing child. Given data=... instead, deserialize that preorder text and return the tree\'s inorder values.',
    'sudoku': 'Two input forms. row0=... is the first row of a valid solved board with one digit replaced by a dot: return that digit. board=... lists 81 cells row by row, with dots for blanks and exactly one solution: return the solved board as 81 digits.',
    'a-star': 'On a 4x4 grid, coordinates are row,col and optional walls=(r,c),... lists cells that cannot be entered. Return the fewest four-neighbor moves from start to goal using A* with the Manhattan heuristic, or -1 when walls block every route.',
    'bidirectional-bfs': 'Return the number of words in the shortest ladder from start to goal, counting both ends and changing one letter at a time. Every word after start must be in the list, including goal. Return 0 when goal is absent from the list or no ladder exists.',
    'insertion-sort': 'Sort ascending with a stable insertion process. Input is either plain integers or keyed pairs (key,label); sort pairs by key only, keep equal keys in input order, and print each pair as its key immediately followed by its label.',
    'bst-search-insert': 'Parse the level-order BST, insert 5 (equal keys go right), then return inorder values. With a trailing order=preorder, return preorder values instead, which reveal where 5 landed.',
    'permutations': 'Given [...], return the number of permutations of the distinct items, counting one empty permutation for an empty list. Given list=[...], return every permutation instead, trying unused input positions left to right, with commas within a permutation and semicolons between them.',
    'predicate-partition': 'Place even values before odd values and return the boundary index after the evens. Given arranged=[...] instead, return the rearranged values; any order with every even before every odd is accepted.',
    'list-intersection': 'Input is one of two forms. a_prefix, b_prefix and shared arrays: build separate prefix nodes and attach both to the same shared tail. Or values=[...] next=[...] a=i b=j: an arena of nodes where next holds each node\'s next index or none, and a and b are the two head indexes. Return the first shared node\'s value, or none when the lists share no node. Equal values do not identify shared nodes.',
    'list-middle': 'Return the middle value of the list; for even length return the second middle.',
    'in-place-merge': 'Parse a, whose first m entries are sorted live values and whose remainder is free capacity, and sorted b. Merge b into a and return all values. Live values may be zero.',
    'fixed-window': 'Return the greatest sum of any three adjacent values; values may be negative.',
    'coin-change-min': 'Return the fewest coins needed for amount 11, or -1 when that amount is unreachable.',
    'kmp': 'Return the first pattern index in the text, or -1 if absent.',
    'rabin-karp': 'Return every start index of the pattern, ascending, or an empty string if absent. Confirm the bytes after a hash match.',
    'jump-game-two': 'Return the minimum jumps to the final index, or -1 when it is unreachable.',
    'circular-monotonic-stack': 'Return each value\'s next greater value in circular order, or -1 when none exists.',
    'three-sum': 'Return the number of unique value triples summing to zero; triples with the same values count once.',
    'longest-consecutive-set': 'Return the length of the longest run of consecutive integer values; duplicates count once.',
    'floyd-state-cycle': 'Given next indexes, return the index where the cycle reached from index 0 begins.',
    'fast-power': 'Parse base, exp and a positive mod; return base^exp modulo mod, including exp=0, so mod=1 gives 0.',
    'binary-heap': 'Insert the values into a min-heap and return pop order.',
    'two-heap-median': 'Return the running median after each inserted value.',
}

IDEAS = {
    'variable-window': 'Expand until the sum reaches the target, then shrink from the left while it stays at or above the target.',
    'dutch-flag': 'Maintain less-than, equal, unknown, and greater-than regions with three boundaries.',
    'deadline-scheduling': 'Take jobs in descending profit and place each in the latest free slot at or before its deadline.',
    'treap': 'Keep BST order by key and heap order by random priority; insertion rotates a new node up and deletion merges its children.',
    'index-map': 'Remember the latest position of each value and measure each repeat against it.',
}

# Model `rule` text where `idea` would state the quiz answer. Every other model rule is `idea`.
RULES = {
    'treap': "Give every key a random priority, rotate a new node up on insertion, and merge a deleted node's children.",
    'bellman-ford': 'Relax every edge V-1 times, because a shortest simple path has at most V-1 edges.',
    'merge-two-lists': 'Merge by moving ownership of existing nodes, one per comparison, until one list runs out.',
    'lis-patience': 'Keep one candidate tail per subsequence length and binary-search where each new value belongs.',
    'gray-code': 'Map each index i to i xor (i shifted right by one) to produce binary-reflected Gray code order.',
    'frequency-balanced-window': 'Track the dominant character count and shrink the window once it needs more replacements than allowed.',
    'at-most-k': 'Keep a frequency state for the window, grow it on the right, and record the best valid length.',
    'min-stack': 'Pair each stack entry with a cached summary so pop restores the previous answer in constant time.',
    'n-queens': 'Place one queen per row and reject any square an earlier queen attacks before recursing.',
    'edit-distance': 'Each state takes the cheapest single edit from adjacent smaller prefixes.',
    'centroid-decomposition': 'Remove a balancing centroid and recurse on each remaining component, which keeps the depth logarithmic.',
    'partition-median': 'Binary-search a cut in the shorter array and derive the matching cut in the other.',
    'tree-preorder': 'Work top-down so parent context is available to the subtrees below.',
    'rotated-search': "Compare the midpoint with the interval ends to learn the rotation's shape, then choose the viable side.",
    'container-area': 'Start with the widest pair and move one boundary inward after each area check.',
    'lower-bound': 'Keep one boundary on each side of the answer and narrow them until they meet.',
    'two-heap-median': 'Keep the lower half in a max-heap and the upper half in a min-heap, rebalancing after every insert.',
    'bipartite-coloring': 'Assign opposite colors across every edge while traversing each component.',
    'in-place-merge': 'Fill free capacity from the end, taking the larger of the two unread tails.',
    'remove-nth-from-end': 'Walk the list once with two cursors, then unlink the target through its predecessor.',
}

USE_CASES = {
    'kruskal-mst': 'minimum spanning trees of connected graphs and sparse edge lists',
}

COMPLEXITY = {
    'variable-window': 'O(n) time · O(1) state',
    'string-two-pointers': 'O(n) time · O(1) extra state',
    'counting-sort': 'O(n+k) time · O(k) auxiliary counters plus O(n) output',
    'copy-random-list': 'O(n) time · O(n) old-to-new map and copied nodes',
    'hash-frequency': 'O(n+m) expected time · at most 26 map entries for lowercase ASCII',
    'rolling-fingerprint': 'O(n) time · O(1) rolling state',
    'remove-nth-from-end': 'O(n) time · O(1) extra space over the arena',
}

# Replacements for the concept-question facts recorded in academy_20261027/teaching.py.
# Every field is rewritten wherever the old wording appears in the three stages.
FACTS = {
    'remove-nth-from-end': {
        'question': 'How is the second-from-end node located without measuring the list first?',
        'correct': 'Open a gap of two links, then move both cursors until the lead reaches the last node',
        'trace': 'In 1→2→3→4→5, lead moves two links to 3 while trail stays on 1. Both then advance until lead is on 5, leaving trail on 3, just before the target 4. Point trail past the target. In a two-node list, lead falls off the end during the gap, so the target is the head.',
    },
    'copy-random-list': {
        'question': 'Why must a deep copy translate each random link through an old-to-new map?',
        'correct': 'An old index names a source node, so each link must be rewritten to the matching copied node',
        'wrong': ['Copying the records as they are gives the right links in any storage order', 'Random links must be deleted during every copy'],
        'trace': 'With values [7,13,11] and next=[2,none,1], the list order is 7→11→13. The first pass gives the copies slots 0, 1 and 2 in that order. The second pass translates each link: the random target of 11 is source node 1, which holds 13 and lands in slot 2. Changing the copied first value leaves the source unchanged.',
    },
    'rolling-fingerprint': {
        'trace': 'The window keeps the last three digits. Digits 3,1,4 give states 3,31,11. For 2,7,1,8 the window 2,7,1 hashes to 69; removing the outgoing 2 at weight 100 and shifting in 8 gives 718 mod 101=11. That collides with 3,1,4, and [1,0,1] and [0] both hash to 0, so hash equality alone must not stand in for content equality.',
    },
    'rolling-window-statistic': {
        'trace': 'For [2,4,6,8,10] and k=3, exact sums are 12,18,24. Divide only when reporting, producing [4,6,8]. Remove the outgoing sample and add the incoming sample to the sum, not to an already rounded mean. Variance also tracks the sum of squares: [2,4,6] has (3*56-144)/9=24/9, which rounds down to 2.',
    },
    'hash-frequency': {
        'question': "Why compare every letter's count rather than only word length?",
        'trace': 'For rust and tsur, adding the first word and subtracting the second returns every map entry to zero. For abc and abd, c stays at +1 and d reaches -1. The implementation accepts lowercase ASCII as its stated domain.',
    },
    'sudoku': {
        'trace': 'The first row 53.678912 lacks 4, and row, column and 3×3 block checks allow 4 in that hole. A board with many blanks needs more: the program tries an allowed digit, recurses, and resets the cell to zero when that branch fails, so another digit can be tried from the same parent board.',
    },
    'a-star': {
        'question': 'Why is Manhattan distance admissible on a four-neighbor grid, with or without walls?',
        'trace': 'From (0,0) to (3,2), Manhattan distance is 5. Each legal move changes only one coordinate by one, so a five-move path reaches that bound. Walls can only lengthen a route: from (0,0) to (3,0) past walls (1,0),(1,1),(1,2) the estimate is 3 and the true cost is 9. The heap ranks g+h while recorded distances track only g; stale entries are skipped.',
    },
    'bidirectional-bfs': {
        'trace': 'The ladder hit→hot→dot→dog→cog contains 5 words and 4 transformations. Search from both endpoints and expand the smaller frontier layer, comparing meeting distances. A goal missing from the list, or no connecting sequence, yields the explicit result 0.',
    },
    'lazy-heap-deletion': {
        'trace': 'Push 2,4,7, then delete 4. It sits below the top, so mark one occurrence of 4 stale; the minimum stays 2. Delete 2 and the top is pruned, which surfaces the stale 4; prune it too and expose 7. Duplicate values require deletion counts so deleting one 1 does not remove every stored 1. If nothing stays live, min reports none.',
    },
    'insertion-sort': {
        'trace': 'For [5,2,4,6,1,3], inserting 2 moves 5 right; inserting 4 moves only 5. Each processed prefix is sorted. Using a strict comparison avoids moving an equal earlier key behind the newly inserted one, so [(2,a),(1,b),(2,c)] sorts to 1b,2a,2c.',
    },
    'bst-search-insert': {
        'trace': 'Inserting 5 into BST [4,2,7,1,3] follows 4→right to 7, then left to an empty link. Inorder becomes 1,2,3,4,5,7, and preorder 4,2,1,3,7,5 shows where 5 landed. The example explicitly sends duplicate keys to the right.',
    },
    'permutations': {
        'trace': "Four distinct items offer 4 choices, then 3, then 2, then 1, producing 24 leaves. Unmarking after recursion restores the parent's choice set. The function builds every permutation; the count is the length of that list.",
    },
    'tree-serialize': {
        'wrong': ['Null markers sort the values', 'Null markers are needed only for leaves with odd values'],
        'trace': 'Tree [1,2,3,null,null,4,5] serializes to 1,2,#,#,3,4,#,#,5,#,#. The two # markers after 2 distinguish its missing children from the following subtree rooted at 3. Deserializing reads the same tokens in the same preorder, so it rebuilds that shape.',
    },
    'min-max-tracking': {
        'wrong': ['Starting from zero only goes wrong on an empty input', 'The maximum must always be positive'],
        'trace': 'For [8,3,11,6], start low=8 and high=8. Reading 3 changes low to 3; reading 11 changes high to 11. The final difference is 11-3=8, not the sum of the readings. Subtract as i64, because two i32 readings can differ by more than i32 can hold.',
    },
    'complement-lookup': {
        'wrong': ['Inserting first would only make the lookup slower', 'Negative numbers cannot be stored after lookup'],
    },
    'suffix-aggregate': {
        'wrong': ["Each position's suffix maximum depends only on values before it", 'A maximum can only be computed recursively'],
    },
    'list-middle': {
        'wrong': ['It stops slow on the first of the two even-length middles', 'The last node is always the middle'],
    },
    'subsets': {
        'wrong': ['Mask 2, because the input has two values', 'Mask 0, which selects both values'],
    },
    'euclid-gcd': {
        'trace': 'For (252,105), states become (105,42),(42,21),(21,0). The last nonzero remainder is 21. The loop stops once the second argument is zero, so gcd(0,9) takes one transition to (9,0) and returns 9.',
    },
    'gray-code': {
        'question': 'What property of the sequence does i XOR (i shifted right by one) guarantee?',
    },
    'imos-sweep': {
        'trace': 'Applying (0,2,+2) and (1,3,+3) gives load 5 at indexes 1 and 2. Adding (3,4,+1) produces [2,5,5,4,1]. The maximum is 5.',
    },
    'reservoir-sampling': {
        'trace': 'With choices [0,1,1,3], index 0 selects 10, index 1 selects 20, index 2 retains 20, and index 3 selects 40. Each index i replaces with probability 1/(i+1); the supplied choices make that decision reproducible.',
    },
    'gas-station': {
        'trace': 'In the sample, early starts fail and the candidate resets to index 3. The full total gas equals total cost, so this candidate can finish the circuit, and it is the smallest valid start because every earlier start failed. If the total is negative, no starting station is feasible.',
    },
}

# Direct text edits, applied to every prose string of the pattern's three stages.
TEXT = {
    'binary-search-answer': [(' Capacity 15 belongs to a different five-day example and is not valid for this task.', '')],
}

# stage -> pattern -> {answer index: replacement}. correctAnswer stays where it is.
DISTRACTORS = {
    'recognize': {
        'bucket-sort': {0: '`0.5,0.1,0.9`', 2: '`0.9,0.5,0.1`'},
        'closest-k-heap': {0: '`0:0,1:0`', 2: '`1:0,0:1`'},
        'combination-sum': {0: '`7`', 2: '`1,7`'},
        'copy-random-list': {0: '`1:2,2:1`', 2: '`1:null,2:null`'},
        'expression-shunting-yard': {0: '`8 2 3 + /`', 2: '`8 2 3 / +`'},
        'insert-interval': {0: '`1-2,9-10`', 2: '`1-10`'},
        'list-intersection': {0: '`1`', 2: '`1,1`'},
        'manacher': {0: '`1`'},
        'merge-intervals': {0: '`1-2,2-3`', 2: '`2-2`'},
        'merge-sort': {0: '`2b,3c,3a`', 2: '`3a,2b,3c`'},
        'minimum-cover-window': {0: '`AAABBC`', 2: '`BBC`'},
        'run-length-encoding': {0: '`a`', 2: '`1`'},
        'string-frequency': {0: '`none`'},
        'strong-components': {0: '`0,1,2`', 2: '`0;1,2`'},
        'subsets': {0: '`3;4;3,4`', 2: '`;3;3,4;4`'},
        'tree-serialize': {0: '`1,2,#,#`', 2: '`1,2`'},
        'two-heap-median': {0: '`1,1,2,2,3,3,4`', 2: '`1,2,2,3,3,4,4`'},
        'adjacency-list': {2: 'Not a valid result'},
        'parentheses-generation': {2: 'Not a valid result'},
        'sieve': {2: 'Not a valid result'},
    },
    'challenge': {
        'bucket-sort': {1: '`0.99,0.01`', 2: '`0,1`'},
        'closest-k-heap': {1: '`2:0,0:2`', 2: '`3:4,0:2`'},
        'copy-random-list': {1: '`3:5,4:null,5:3`', 2: '`3:null,4:null,5:null`'},
        'expression-shunting-yard': {1: '`2 3 4 * +`', 2: '`( 2 3 + ) 4 *`'},
        'gas-station': {1: '`3`'},
        'insert-interval': {1: '`2-3,5-6`', 2: '`2-8`'},
        'manacher': {1: '`aba`', 2: '`bacab`'},
        'merge-intervals': {1: '`1-8`', 2: '`1-2,4-8`'},
        'merge-sort': {1: '`4x,2z,1y`', 2: '`1x,2z,4y`'},
        'minimum-cover-window': {1: '`CABAC`', 2: '`ABAC`'},
        'parentheses-generation': {1: 'drop-last', 2: 'reverse-order'},
        'partition-median': {1: '`3`', 2: '`2`'},
        'run-length-encoding': {1: '`a2b3`', 2: '`b3`'},
        'string-frequency': {1: '`a`', 2: '`none`'},
        'subsets': {1: '`5`', 2: '`;`'},
        'tree-serialize': {1: '`1,2,3`', 2: '`2,#,#,1,3,#,#`'},
        'two-heap-median': {1: '`8,7,7,6,6,5,5`', 2: '`8,8,7,7,6,6,5`'},
        'bitmask-enumeration': {2: 'Not a valid result'},
        'combinations': {2: 'Not a valid result'},
    },
}

# Inline-code spans around ordinary English, across every prose field of the course.
MARKUP = [
    ('`String` algorithms', 'String algorithms'),
    ('`Some` patterns', 'Some patterns'),
    ('`String` Two Pointers', 'String Two Pointers'),
]
