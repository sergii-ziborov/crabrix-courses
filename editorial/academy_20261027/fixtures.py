"""Translate each documented textual contract into a typed Rust call.

No expected answer is computed here; independent Python oracles supply it.
"""
import ast
import json
import re
from oracles import array, lists, matrix, tree, edges, graph, number, ints


def r(value):
    if value is None:return 'None'
    if isinstance(value,bool):return str(value).lower()
    if isinstance(value,str):return json.dumps(value,ensure_ascii=False)
    if isinstance(value,tuple):return '('+','.join(r(x) for x in value)+')'
    if isinstance(value,list):return '['+','.join(r(x) for x in value)+']'
    return str(value)


def vv(values):return '&['+','.join('vec!'+r(row) for row in values)+']'


def rt(root):return 'None' if root is None else f'node({root[0]},{rt(root[1])},{rt(root[2])})'


def call(pattern,text):
    text=text.strip()
    scalar_arrays={
      'linear-scan':'first_negative','min-max-tracking':'spread','frequency-counting':'mode',
      'running-accumulator':'alternating_sum','adjacent-pair-scan':'decreases',
      'boyer-moore-majority':'majority','longest-consecutive-set':'longest_run',
      'slow-fast':'middle_value','three-sum':'zero_triples','container-area':'greatest_container',
      'trapping-water':'trapped','largest-histogram':'largest_rectangle',
      'house-robber':'non_adjacent_sum','kadane':'maximum_subarray','lis-patience':'lis_length',
      'matrix-chain':'matrix_chain','interval-dp':'balloon_coins','xor-cancellation':'single_value',
    }
    vector_arrays={
      'coordinate-compression':'ranks','suffix-aggregate':'suffix_maxima','prefix-suffix-product':'products_except_self',
      'next-greater-stack':'next_greater','monotonic-increasing-stack':'previous_smaller',
      'monotonic-decreasing-stack':'stock_spans','circular-monotonic-stack':'circular_greater',
      'binary-heap':'heap_order',
    }
    strings={
      'palindrome-pointers':'ascii_palindrome','unique-window':'longest_unique',
      'delimiter-stack':'balanced','postfix-evaluation':'postfix','expression-shunting-yard':'to_postfix',
      'palindrome-partition':'palindrome_partitions','decode-ways':'decodings',
      'string-two-pointers':'normalized_palindrome','run-length-encoding':'run_lengths',
      'manacher':'longest_palindrome','suffix-automaton':'distinct_substrings',
    }
    if pattern in scalar_arrays:return f'{scalar_arrays[pattern]}(&{r(array(text))}).to_string()'
    if pattern in vector_arrays:return f'csv({vector_arrays[pattern]}(&{r(array(text))}))'
    if pattern in strings:return f'{strings[pattern]}({r(text)}).to_string()'
    match pattern:
      case 'stable-compaction'|'same-direction'|'dutch-flag'|'insertion-sort'|'quicksort'|'heap-sort'|'radix-sort':
        function={'stable-compaction':'compact_nonzero','same-direction':'keep_at_least','dutch-flag':'sort_three','insertion-sort':'insertion_sort','quicksort':'quicksort','heap-sort':'heap_sort','radix-sort':'radix_sort'}[pattern]
        return '{ let mut values=vec!'+r(array(text))+f'; {function}(&mut values'+(',5' if pattern=='same-direction' else '')+'); csv(values) }'
      case 'predicate-partition':return '{ let mut values=vec!'+r(array(text))+'; partition_even(&mut values).to_string() }'
      case 'selection-sort':return '{ let mut values=vec!'+r(array(text))+'; selection_swaps(&mut values).to_string() }'
      case 'reservoir-sampling':
        a,b=lists(text);return f'reservoir(&{r(a)},&{r(b)}).map_or("none".into(),|x|x.to_string())'
      case 'floyd-state-cycle':return f'cycle_entry(&{r(array(text))}).to_string()'
      case 'hash-membership':return f'has_duplicate(&{r(array(text))}).to_string()'
      case 'hash-frequency':
        a,b=text.split(';');return f'anagrams({r(a.strip())},{r(b.strip())}).to_string()'
      case 'complement-lookup':return f'two_sum(&{r(array(text))},{number(text,"target")}).map_or("-1,-1".into(),|(i,j)|format!("{{i}},{{j}}"))'
      case 'group-by-key':return f'largest_anagram_group(&{r(text.strip("[]").split(","))}).to_string()'
      case 'index-map':return f'nearest_repeat(&{r(array(text))}).map_or("-1".into(),|i|i.to_string())'
      case 'bidirectional-map':
        a,b=text.split(';');return f'follows_pattern({r(a)},&{r(b.split())}).to_string()'
      case 'randomized-set'|'treap':
        ops=[(op in ('add','insert'),int(n)) for op,n in re.findall(r'(add|remove|insert|delete)(-?\d+)',text)]
        return f'csv({"dense_operations" if pattern=="randomized-set" else "treap_operations"}(&{r(ops)}))'
      case 'rolling-fingerprint':return f'digit_hash(&{r(array(text))}).to_string()'
      case 'prefix-sum'|'prefix-xor':return f'{"range_sum" if pattern=="prefix-sum" else "range_xor"}(&{r(array(text))},1,{3 if pattern=="prefix-sum" else 4}).to_string()'
      case 'equilibrium-index':return f'equilibrium(&{r(array(text))}).to_string()'
      case 'difference-array'|'imos-sweep':
        ops=[tuple(map(int,p)) for p in re.findall(r'\((\d+),(\d+),(-?\d+)\)',text)]
        fn='apply_updates' if pattern=='difference-array' else 'peak_load';expr=f'{fn}({number(text,"n")},&{r(ops)})'
        return f'csv({expr})' if pattern=='difference-array' else expr+'.to_string()'
      case 'prefix-sum-2d':return f'rectangle_sum({vv(ast.literal_eval(text))},1,0,2,1).to_string()'
      case 'fenwick-tree':
        ops=[tuple(map(int,p)) for p in re.findall(r'\((\d+),(-?\d+)\)',text)];return f'fenwick_prefix({number(text,"n")},&{r(ops)},{number(text,"query")}).to_string()'
      case 'segment-tree':
        update=tuple(map(int,re.search(r'update=\((\d+),(-?\d+)\)',text).groups()));q=tuple(map(int,re.search(r'query=(\d+)\.\.(\d+)',text).groups()))
        return f'updated_min(&{r(array(text))},{r(update)},{r(q)}).to_string()'
      case 'opposite-ends':return f'pair_exists(&{r(array(text))},10).to_string()'
      case 'sorted-two-sum':return f'sorted_pair(&{r(array(text))},17).map_or("-1,-1".into(),|(a,b)|format!("{{a}},{{b}}"))'
      case 'in-place-merge':
        a,b=lists(text);return '{ let mut a=vec!'+r(a)+f'; merge_into(&mut a,{number(text,"m")},&{r(b)}); csv(a) '+'}'
      case 'fixed-window':return f'greatest_k_sum(&{r(array(text))},3).to_string()'
      case 'variable-window':return f'shortest_sum(&{r(array(text))},7).to_string()'
      case 'at-most-k':return f'longest_k_distinct(&{r(array(text))},2).to_string()'
      case 'exactly-k-difference':return f'exactly_k(&{r(array(text))},2).to_string()'
      case 'frequency-balanced-window':return f'replacement_length({r(text)},1).to_string()'
      case 'minimum-cover-window':return f'minimum_cover({r(text)},"ABC").to_string()'
      case 'monotonic-deque-window'|'rolling-window-statistic'|'dual-heap-window-median':return f'csv({ {"monotonic-deque-window":"window_maxima","rolling-window-statistic":"window_means","dual-heap-window-median":"sliding_medians"}[pattern]}(&{r(array(text))},3))'
      case 'min-stack'|'queue-with-stacks'|'lazy-heap-deletion':return f'{ {"min-stack":"stack_min","queue-with-stacks":"queue_front","lazy-heap-deletion":"valid_min"}[pattern]}(&{r(text.split())}).to_string()'
      case 'merge-sort':
        pairs=[(int(k),v) for k,v in re.findall(r'\((-?\d+),([^,)]+)\)',text)];literal='['+','.join(f'({k},{repr(v)})' for k,v in pairs)+']'
        return f'stable_merge_sort(&{literal}).iter().map(|(k,v)|format!("{{k}}{{v}}")).collect::<Vec<_>>().join(",")'
      case 'counting-sort':return f'csv(counting_sort(&{r(array(text))},5))'
      case 'bucket-sort':return f'csv(bucket_sort(&{r(array(text))}))'
      case 'quickselect':return '{ let mut a=vec!'+r(array(text))+'; quickselect(&mut a,2).to_string() }'
      case 'median-of-medians':return f'deterministic_select(&{r(array(text))},4).to_string()'
      case 'binary-exact'|'rotated-search'|'exponential-search':
        fn,target={'binary-exact':('exact_index',9),'rotated-search':('rotated_index',0),'exponential-search':('exponential_index',21)}[pattern]
        return f'{fn}(&{r(array(text))},{target}).to_string()'
      case 'lower-bound'|'upper-bound':return f'{pattern.replace("-","_")}(&{r(array(text))},4).to_string()'
      case 'first-last-position':return '{ let (a,b)=first_last(&'+r(array(text))+',8); format!("{a},{b}") }'
      case 'peak-search':return f'peak_index(&{r(array(text))}).to_string()'
      case 'matrix-binary-search':return f'matrix_contains({vv(matrix(text))},16).to_string()'
      case 'binary-search-answer':return f'shipping_capacity(&{r(array(text))},{number(text,"days")}).to_string()'
      case 'partition-median':
        a,b=lists(text);return f'sorted_median(&{r(a)},&{r(b)}).to_string()'
      case 'list-reversal'|'list-middle'|'remove-nth-from-end'|'partition-list'|'reorder-list'|'reverse-k-group':
        a=list(map(int,text.split('->'))) if text else [];head='list(&'+r(a)+')'
        if pattern=='list-middle':return f'list_middle(&{head}).to_string()'
        fn,arg={'list-reversal':('reverse',''),'remove-nth-from-end':('remove_from_end',',2'),'partition-list':('partition_list',',3'),'reorder-list':('reorder',''),'reverse-k-group':('reverse_groups',',3')}[pattern]
        return f'csv(list_values(&{fn}({head}{arg})))'
      case 'merge-two-lists':
        a,b=text.split(' and ');return f'csv(list_values(&merge_lists(list(&{r(ints(a))}),list(&{r(ints(b))}))))'
      case 'list-cycle':
        a=array(text);tail=text.split('tail->')[1];nexts=[f'Some({i+1})' for i in range(len(a)-1)]+['None' if tail=='none' else f'Some({tail})']
        return 'contains_cycle(&['+','.join(nexts)+']).to_string()'
      case 'list-intersection':
        a,b,shared=lists(text);return '{ let tail=shared_list(&'+r(shared)+',None); let a=shared_list(&'+r(a)+',tail.clone()); let b=shared_list(&'+r(b)+',tail); intersection(&a,&b).map_or("none".into(),|x|x.to_string()) }'
      case 'copy-random-list':
        a,targets=lists(text.replace('null','None'));option='['+','.join('None' if x is None else f'Some({x})' for x in targets)+']'
        return f'copied_pairs(&{r(a)},&{option})'
      case 'tree-preorder'|'tree-inorder'|'tree-postorder'|'tree-level-order':
        fn={'tree-preorder':'preorder','tree-inorder':'inorder','tree-postorder':'postorder','tree-level-order':'level_sums'}[pattern]
        return f'csv({fn}(&{rt(tree(text))}))'
      case 'tree-height-balance':return f'is_balanced(&{rt(tree(text))}).to_string()'
      case 'bst-search-insert':return '{ let mut root='+rt(tree(text))+'; insert_bst(&mut root,5); csv(bst_values(&root)) }'
      case 'lowest-common-ancestor':return f'ancestor(&{rt(tree(text))},5,1).unwrap().to_string()'
      case 'tree-serialize':return f'serialize(&{rt(tree(text))})'
      case 'tree-diameter':return f'diameter(&{rt(tree(text))}).to_string()'
      case 'tree-dp':return f'tree_independent_sum(&{rt(tree(text))}).to_string()'
      case 'tree-rerooting':
        g,_=graph(text);return f'csv(distance_sums({vv([[u for u,w in ns] for ns in g])}))'
      case 'top-k-minheap'|'kth-stream':return f'csv({"top_k" if pattern=="top-k-minheap" else "kth_largest_stream"}(&{r(array(text))},3))'
      case 'k-way-merge':return f'csv(merge_many({vv([ast.literal_eval(p) for p in text.split(";")])}))'
      case 'closest-k-heap':return f'closest(&{r(ast.literal_eval(text))},2).iter().map(|(x,y)|format!("{{x}}:{{y}}")).collect::<Vec<_>>().join(",")'
      case 'two-heap-median':return f'csv(stream_medians(&{r(array(text))}))'
      case 'priority-scheduling':
        jobs=[tuple(map(int,x)) for x in re.findall(r'\(id(\d+),t(\d+),d(\d+)\)',text)];return f'csv(completion_order(&{r(jobs)}))'
      case 'meeting-rooms-heap':return f'rooms(&{r(ast.literal_eval(text))}).to_string()'
      case 'huffman-greedy-heap':return f'merge_cost(&{r(array(text))}).to_string()'
      case 'adjacency-list':return f'csv(neighbors({number(text,"n")},&{r(edges(text))},2))'
      case 'graph-dfs'|'graph-bfs'|'connected-components'|'bipartite-coloring'|'undirected-cycle'|'kahn-topological'|'dfs-topological'|'strong-components':
        g,_=graph(text,pattern in ['kahn-topological','dfs-topological','strong-components']);literal=vv([[u for u,w in ns] for ns in g])
        if pattern=='graph-dfs':return f'csv(dfs_order({literal},0))'
        if pattern=='graph-bfs':return f'csv(edge_distances({literal},0))'
        if pattern=='strong-components':return f'semicolon(strongly_connected({literal}))'
        if pattern in ['kahn-topological','dfs-topological']:return f'csv({"smallest_topological" if pattern=="kahn-topological" else "dfs_topological"}({literal}))'
        return f'{ {"connected-components":"component_count","bipartite-coloring":"bipartite","undirected-cycle":"has_cycle"}[pattern]}({literal}).to_string()'
      case 'grid-flood-fill':return f'component_size({vv(matrix(text))},(1,1)).to_string()'
      case 'dijkstra'|'zero-one-bfs'|'dag-shortest-path'|'prim-mst':
        g,_=graph(text,pattern=='dag-shortest-path',True);literal=vv(g)
        if pattern=='dijkstra':return f'csv(dijkstra({literal},0))'
        return f'{ {"zero-one-bfs":"zero_one_distance","dag-shortest-path":"dag_distance","prim-mst":"prim_weight"}[pattern]}({literal}'+(',0,3' if pattern=='zero-one-bfs' else ',0,4' if pattern=='dag-shortest-path' else '')+').to_string()'
      case 'kruskal-mst'|'bellman-ford'|'dinic-max-flow':
        g,es=graph(text,pattern!='kruskal-mst',True);n=max(4,len(g)) if pattern=='dinic-max-flow' else len(g)
        if pattern=='kruskal-mst':return f'csv(kruskal_weights({n},&{r(es)}))'
        if pattern=='bellman-ford':return f'csv(bellman_ford({n},&{r(es)},0))'
        return f'max_flow({n},&{r(es)},0,3).to_string()'
      case 'floyd-warshall':return 'all_pairs(vec!['+','.join('vec!'+r(row) for row in matrix(text))+'])[0][2].to_string()'
      case 'a-star':
        a,b,c,d=ints(text);return f'grid_a_star(4,4,({a},{b}),({c},{d})).to_string()'
      case 'bidirectional-bfs':
        a,b=text.split(' via ')[0].split(' -> ');words=text.split('[')[1].split(']')[0].split(',');return f'ladder_length({r(a)},{r(b)},&{r(words)}).to_string()'
      case 'subsets':return f'semicolon(subsets_in_mask_order(&{r(array(text))}))'
      case 'permutations':return f'permutation_count(&{r(array(text))}).to_string()'
      case 'combinations':return f'semicolon(combinations(&{r(array(text))},2))'
      case 'combination-sum':return f'semicolon(combinations_sum(&{r(array(text))},7))'
      case 'parentheses-generation':return f'parentheses({number(text,"n")}).join(";")'
      case 'word-grid-search':
        a,b=re.fullmatch(r'grid=(.*) word=(.*)',text).groups();literal='&['+','.join(f'{r(row)}.as_bytes().to_vec()' for row in a.split(','))+']'
        return f'word_exists({literal},{r(b)}.as_bytes()).to_string()'
      case 'n-queens':return f'queens({number(text,"n")}).to_string()'
      case 'sudoku':
        row=text.split('=')[1];missing=row.index('.');grid=[[int(c) for c in line] for line in ['534678912','672195348','198342567','859761423','426853791','713924856','961537284','287419635','345286179']];grid[0]=[int(c) if c!='.' else 0 for c in row]
        return '{ let mut grid='+r(grid)+f'; assert!(solve_sudoku(&mut grid)); grid[0][{missing}].to_string() '+'}'
      case 'meet-in-middle':return f'subset_exists(&{r(array(text))},15).to_string()'
      case 'activity-selection'|'merge-intervals'|'insert-interval'|'sweep-line-events'|'minimum-arrows':
        data=r(ast.literal_eval(text))
        if pattern in ['merge-intervals','insert-interval']:
          fn,arg=('merged_intervals','') if pattern=='merge-intervals' else ('inserted_interval',',(4,8)')
          return f'{fn}(&{data}{arg}).iter().map(|(a,b)|format!("{{a}}-{{b}}")).collect::<Vec<_>>().join(",")'
        return f'{ {"activity-selection":"maximum_meetings","sweep-line-events":"maximum_sessions","minimum-arrows":"arrows"}[pattern]}(&{data}).to_string()'
      case 'jump-game'|'jump-game-two':return f'{"can_reach" if pattern=="jump-game" else "minimum_jumps"}(&{r(array(text))}).to_string()'
      case 'gas-station':
        a,b=lists(text);return f'starting_station(&{r(a)},&{r(b)}).to_string()'
      case 'partition-labels':return f'csv(partition_lengths({r(text)}))'
      case 'deadline-scheduling':
        data=[tuple(map(int,p)) for p in re.findall(r'\(d(\d+),p(\d+)\)',text)];return f'maximum_profit(&{r(data)}).to_string()'
      case 'memoization'|'tabulation'|'matrix-exponentiation':return f'{ {"memoization":"fibonacci","tabulation":"climb_ways","matrix-exponentiation":"fibonacci_matrix"}[pattern]}({number(text,"n")}).to_string()'
      case 'rolling-dp':return f'stair_cost(&{r(array(text))}).to_string()'
      case 'coin-change-min':return f'fewest_coins(&{r(array(text))},11).to_string()'
      case 'word-break-dp':
        a,b=re.fullmatch(r'text=(.*) dict=\[(.*)\]',text).groups();return f'word_break({r(a)},&{r(b.split(","))}).to_string()'
      case 'zero-one-knapsack':
        a,b=lists(text);return f'knapsack(&{r(a)},&{r(b)},7).to_string()'
      case 'grid-path-dp':return f'grid_paths({number(text,"rows")},{number(text,"cols")}).to_string()'
      case 'subset-sum':return f'subset_sum(&{r(array(text))},11).to_string()'
      case 'longest-common-subsequence'|'edit-distance':
        a,b=text.split(' and ' if pattern=='longest-common-subsequence' else ' -> ');return f'{"lcs" if pattern=="longest-common-subsequence" else "edit_distance"}({r(a)},{r(b)}).to_string()'
      case 'longest-pal-subsequence':return f'palindromic_subsequence({r(text)}).to_string()'
      case 'digit-dp':return f'digit_sum_count({number(text,"bound")},{number(text,"sum")}).to_string()'
      case 'bitmask-dp':return 'travelling_salesman('+vv(matrix(text))+').to_string()'
      case 'string-frequency':return f'first_unique_ascii({r(text)}).map_or("none".into(),|c|c.to_string())'
      case 'kmp'|'rabin-karp':
        a,b=re.fullmatch(r'text=(.*) pattern=(.*)',text).groups();expr=f'{"kmp_first" if pattern=="kmp" else "rolling_matches"}({r(a)},{r(b)})';return expr+'.to_string()' if pattern=='kmp' else f'csv({expr})'
      case 'z-algorithm'|'suffix-array':return f'csv({"z_values" if pattern=="z-algorithm" else "suffix_array"}({r(text)}))'
      case 'trie':
        words,prefix=re.fullmatch(r'words=\[(.*)\] prefix=(.*)',text).groups();return f'prefix_count(&{r(words.split(","))},{r(prefix)}).to_string()'
      case 'aho-corasick':
        a,b=re.fullmatch(r'text=(.*) patterns=\[(.*)\]',text).groups();return f'multi_pattern_count({r(a)},&{r(b.split(","))}).to_string()'
      case 'euclid-gcd':return f'gcd({number(text,"a")},{number(text,"b")}).to_string()'
      case 'bitmask-enumeration':return f'csv(matching_masks(&{r(array(text))},5))'
      case 'sieve':return f'csv(primes_to({number(text,"n")}))'
      case 'fast-power':return f'mod_power({number(text,"base")},{number(text,"exp")},{number(text,"mod")}).to_string()'
      case 'modular-inverse':return f'modular_inverse({number(text,"a")},{number(text,"mod")}).unwrap().to_string()'
      case 'binomial-coefficients':return f'choose({number(text,"n")},{number(text,"k")}).to_string()'
      case 'gray-code':return f'csv(gray_codes({number(text,"n")}))'
      case 'miller-rabin':return f'is_prime({number(text,"n")}).to_string()'
      case 'sparse-table'|'mo-algorithm':return f'csv({"sparse_minima" if pattern=="sparse-table" else "distinct_queries"}(&{r(array(text))},&{r([(0,3),(2,5),(4,6)] if pattern=="sparse-table" else [(0,3),(2,5),(0,5)])}))'
      case 'disjoint-set-union':return f'components_after_unions({number(text,"n")},&{r(edges(text))}).to_string()'
      case 'lazy-segment-tree':return f'lazy_example(&{r(array(text))}).to_string()'
      case 'skip-list':return f'skip_contains(&{r(array(text))},19).to_string()'
      case 'dsu-rollback':
        before,after=text.split(' checkpoint ');pairs=edges(after);query=tuple(map(int,re.search(r'query=\((\d+),(\d+)\)',text).groups()))
        return f'rollback_query({number(text,"n")},&{r(edges(before))},&{r(pairs[:-1])},{r(query)}).to_string()'
      case 'heavy-light':
        raw,values=text.split(' values=');g,_=graph(raw);return f'heavy_light_sum({vv([[u for u,w in ns] for ns in g])},&{values},2,4).to_string()'
      case 'centroid-decomposition':
        g,_=graph(text);return f'centroid_root({vv([[u for u,w in ns] for ns in g])}).to_string()'
      case _:raise NotImplementedError(pattern)
