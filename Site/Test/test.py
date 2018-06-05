from ete3 import Tree, TreeStyle

t = Tree('long.tre', format=1)

ts = TreeStyle()
ts.show_leaf_name = True
ts.mode = "c"
ts.arc_start -180
ts.arc_span = 360
t.show(tree_style=ts)
