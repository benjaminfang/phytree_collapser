#!
import sys
import ete3

class GNode:
    def __init__(self,base_node):
        self.basenode=base_node
        self.baselink=None
        self.uplink=[]

    def linknode(self, upgnode):
        self.baselink=[(self.basenode,self.basenode.up),upgnode]
        upgnode.uplink.append([(self.basenode.up,self.basenode),self])

    def children(self):
        children=[]
        for uplink in self.uplink:
            children.append(uplink[1])
        return children

    def parent(self):
        return self.baselink[1]

    def is_root(self):
        if self.baselink==None:
            return True
        else:
            return False

    def get_gnodeleafs(self):
        def judge_node(node, uplinkoutnode):
            if node not in uplinkoutnode:
                if node.is_leaf():
                    all_leaves.append(node)
                else:
                    for child in node.children:
                        judge_node(child, uplinkoutnode)
        all_leaves=[]
        uplinkoutnode=[]
        for uplink in self.uplink:
            uplinkoutnode.append(uplink[0][1])
#            print(uplinkoutnode)
        judge_node(self.basenode, uplinkoutnode)
        return all_leaves

    def collapse_gnode(self):
        def rm_node(node, uplinkinnode):
            if node not in uplinkinnode:
                if True not in [n in node for n in uplinkinnode]:
                    node.detach()
                else:
                    for child in node.children:
                        rm_node(child, uplinkinnode)
        uplinkinnode=set()
        for uplink in self.uplink:
            uplinkinnode.add(uplink[0][0])
        #print(uplinkinnode)
        rm_node(self.basenode, uplinkinnode)

def treecluster(node, cutoff, upgnode=None):
    if node.is_root():
        rootgnode=GNode(node)
        upgnode=rootgnode
    else:
        if node.dist > cutoff:
            gnode=GNode(node)
            gnode.linknode(upgnode)
            upgnode=gnode
    for child in node.children:
#        print('2')
        treecluster(child, cutoff, upgnode)
    if node.is_root():
#        print('1')
        return rootgnode

def if_cluster_Heterogeneous(gnode, leaf_dic):
    all_leaf=gnode.get_gnodeleafs()
    #for leaf in all_leaf:
    #    print(leaf.name)
    property=[]
    if len(all_leaf)<2: return False
    for leaf in all_leaf:
        property.append(leaf_dic[leaf.name])
    if len(set(property))<2:
        return False
    else:
        return True

def traverse_gnode(gnode):
    all_gnodes.append(gnode)
    for child in gnode.children():
        traverse_gnode(child)

tree=ete3.Tree(sys.argv[1])
cutoff=float(sys.argv[2])
gnoderes=treecluster(tree,cutoff,upgnode=None)
leaf_dic={line.rstrip().split(',')[0]:line.rstrip().split(',')[1] for line in open(sys.argv[3])}

all_gnodes=[]
traverse_gnode(gnoderes)

for gnode in all_gnodes:
    if len(gnode.get_gnodeleafs())<2:
        print(gnode.get_gnodeleafs())



#gnode_need_collapse=[]
#traverse_gnode(gnoderes, leaf_dic)
#for gnode in gnode_need_collapse:
#    gnode.collapse_gnode()
#ts=ete3.TreeStyle()
#ts.mode='c'
#tree.render('hhh.pdf', tree_style=ts)
