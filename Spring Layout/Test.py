#{"source": "0", "target": "1"}
edge_list = [{"source": "a", "target": "b"},
             {"source": "a", "target": "c"},
             {"source": "b", "target": "d"},
             {"source": "b", "target": "e"},
             {"source": "c", "target": "f"},
             {"source": "c", "target": "g"},
             {"source": "g", "target": "h"}
             ]
# "b":{"id":"b","x":324,"y":530,"z":342,"lock":False,"label":"Banana"}
node_list = {"a" : {"id" : "a"},
             "b" : {"id" : "b"},
             "c" : {"id" : "c"},
             "d" : {"id" : "d"},
             "e" : {"id" : "e"},
             "f" : {"id" : "f"},
             "g" : {"id" : "g"},
             "h" : {"id" : "h"},
             }
tree_list = {}

def sorter():
    for edge in edge_list:
        if not tree_list.get(edge.get("source")):
            tree_list[edge.get("source")] = set([])
        tree_list[edge.get("source")].add(edge.get("target"))
        if not tree_list.get(edge.get("target")):
            tree_list[edge.get("target")] = set([])

def dfs(tree_list, start, visited=None, counter = 0):
    if visited is None:
        visited = set()
    visited.add(start)
    count = counter
    if tree_list[start]:
        count = counter + 1
        for next in tree_list[start] - visited:
            node_list[next]["level"] = count
        for next in tree_list[start] - visited:
            count = dfs(tree_list, next, visited, count)
    else:
        node_list[start]["level"] = count
    return count

sorter()
print tree_list
print dfs(tree_list, "a")
print node_list
