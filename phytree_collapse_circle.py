#! /usr/bin/env python3

import argparse
import ete3

class GNode:
    def __init__(self,node_name=''):
        self.name=node_name
        self.linked_nodes=set()

    def link_node(self,node):
        self.linked_nodes.add(node)
        node.linked_nodes.add(self)

    def get_graph_nodes(self):
        def get_node(node):
            for linked_n in node.linked_nodes:
                if linked_n not in all_nodes_linked:
                    all_nodes_linked.add(linked_n)
                    get_node(linked_n)

        all_nodes_linked=set()
        all_nodes_linked.add(self)
        get_node(self)
        return all_nodes_linked

def get_args():
    args=argparse.ArgumentParser('find out and collapse monophyletic.')
    args.add_argument('-tree_file', type=str, required=True, help='file name of newik tree.')
    args.add_argument('-collapse_value', type=float, required=True, help='value for find nearby nodes.')
    args.add_argument('-dist_type', type=str, default='el', help='distance type edge lenth of topology lenth.')
    args.add_argument('-list_file', type=str, required=True, help='leaf node name which need to be find out monophyletic.')
    args=args.parse_args()
    tree_file,collapse_value,dist_type,list_file=args.tree_file,args.collapse_value,args.dist_type,args.list_file
    return tree_file,collapse_value,dist_type,list_file

def item_leaf_node(tree,list_file):
    data_out=[]
    leaf_list=[line.rstrip() for line in open(list_file)]
    for leaf in tree:
        if leaf.name in leaf_list:
            data_out.append(leaf)
    return data_out

def find_internal_node(tree, leaves_node, collapse_value, dist_type):
    leaf_internal_dic={}
    if dist_type=='el':
        for leaf in leaves_node:
            leaf_internal_dic[leaf]=set()
            upper_node=leaf.up
            while True:
                if upper_node.get_distance(leaf) <= collapse_value:
                    leaf_internal_dic[leaf].add(upper_node)
                    upper_node=upper_node.up
                else:
                    break
    elif dist_type=='nl':
        for leaf in leaves_node:
            leaf_internal_dic[leaf]=set()
            upper_node=leaf.up
            while True:
                if upper_node.get_distance(leaf, topology_only=True)<=collapse_value:
                    leaf_internal_dic[leaf].add(upper_node)
                    upper_node=upper_node.up
                else:
                    break
    return leaf_internal_dic

def merge_internal(leaf_internal_dic):
    merged_leaf_internal={}
    gnode_set=[]
    for leaf1 in leaf_internal_dic:
        if leaf1.name not in [n.name for n in gnode_set]:
            gn_1=GNode(leaf1.name)
            gnode_set.append(gn_1)
        tmp=[]
        for leaf2 in leaf_internal_dic:
            if leaf1==leaf2: continue
            if leaf_internal_dic[leaf1]&leaf_internal_dic[leaf2]:
                tmp.append(leaf2)

        for ele in tmp:
            if ele.name not in [n.name for n in gnode_set]:
                gn_2=GNode(ele.name)
                gn_1.link_node(gn_2)
                gnode_set.append(gn_2)
    i=0
    tmp=set()
    groups=[]
    leaf_node_dic={key.name:key for key in leaf_internal_dic}
    for gn in gnode_set:
        if gn not in tmp:
            a_gn=gn.get_graph_nodes()
            groups.append(a_gn)
            tmp.update(a_gn)
    for gg in groups:
        i+=1
        key='g_'+str(i)
        merged_leaf_internal[key]=[[],set()]
        for gn in gg:
            #print(gn)
            leaf_node=leaf_node_dic[gn.name]
            merged_leaf_internal[key][0].append(leaf_node)
            merged_leaf_internal[key][1].update(leaf_internal_dic[leaf_node])
    return merged_leaf_internal

def delete_unwant_node(tree, merged_leaf_internal, collapse_value, dist_type):
    def delete_node(ancestor_node, leaf_nodes, collapse_value, dist_type):
        node_need_rm=[]
        if dist_type=='el':
            for node in ancestor_node.get_descendants():
                #print(node)
                dist=[]
                for leaf in leaf_nodes:
                    #print(leaf)
                    #print(tree.get_distance(node, leaf))
                    dist.append(tree.get_distance(node, leaf))
                #print(min(dist))
                if min(dist)>collapse_value:
                    node_need_rm.append(node)
        elif dist_type=='nl':
            for node in ancestor_node.get_descendants():
                dist=[]
                for leaf in leaf_nodes:
                    dist.append(tree.get_distance(node, leaf, topology_only=True))
                    if min(dist)>collapse_value:
                        node_need_rm.append(node)
        print(node_need_rm)
        for node in node_need_rm:
            tmp=[]
            for node2 in node_need_rm:
                tmp.append(node in node2)
            if True not in tmp:
                node.detach()

    keeped_nodes=[]
    for group in merged_leaf_internal:
        #print(group)
        if len(merged_leaf_internal[group][1])>=1:
            group_common_ancestor=tree.get_common_ancestor(merged_leaf_internal[group][1])
            keeped_nodes.append(group_common_ancestor)
            #print(group_common_ancestor)
            delete_node(group_common_ancestor,merged_leaf_internal[group][0],collapse_value, dist_type)
        else:
            keeped_nodes.append(merged_leaf_internal[group][0][0])
            print('worning1...')
    return keeped_nodes

def collapse_greed(tree, keeped_nodes, leaves_list):
    for node in keeped_nodes:
        while node:
            for sister in node.get_sisters():
                if True not in map(lambda x : x in leaves_list,sister):
                    sister.detach()
            node=node.up

def main():
    tree_file,collapse_value,dist_type,list_file=get_args()
    tree=ete3.Tree(tree_file)
    #print(tree)
    item_leaves=item_leaf_node(tree,list_file)
    #print(item_leaves)
    leaf_internal_dic=find_internal_node(tree, item_leaves, collapse_value, dist_type)
    #print(leaf_internal_dic)
    #for leaf in leaf_internal_dic:
    #    print(leaf)
    #    for node in leaf_internal_dic[leaf]:
    #        print([node])
    #        print(node)
    merged_leaf_internal=merge_internal(leaf_internal_dic)
    #print(merged_leaf_internal)
    keeped_nodes=delete_unwant_node(tree,merged_leaf_internal, collapse_value, dist_type)
    collapse_greed(tree, keeped_nodes, item_leaves)
    print(tree)

if __name__ == '__main__':
    main()
