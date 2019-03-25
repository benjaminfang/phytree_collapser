#! /usr/bin/env python3
import argparse
import ete3
import time

def offer_timemarker():
    time_now=time.localtime()
    time_now=''.join([format(time_now.tm_year,'04'),format(time_now.tm_mon,'02'),
                      format(time_now.tm_mday,'02'),format(time_now.tm_hour,'02'),
                      format(time_now.tm_min,'02'), format(time_now.tm_sec,'02')])

    return time_now

def get_args():
    args=argparse.ArgumentParser(description='this is a utility for collapsing phylogenic tree.',epilog='any problem please contect benjaminfang.ol@outlook.com, or visite https://github.com/benjaminfang.')
    args.add_argument('-alg',type=str,required=True,choices=['r2l_hier','l2r_hier', 'greed'],help='algrisme.')
    args.add_argument('-tree_file',type=str,required=True,help='the file name of newik tree.')
    args.add_argument('-collapse_value',type=float,nargs='+',required=True,help='location where collapse performed.')
    args.add_argument('-dist_type',type=str,default='el',choices=['el','nl','elf','nlf'],help='distance type. el for edge distance, nl for node distance.')
    args.add_argument('-list_file',type=str,default='None',help='leaf node list file name.')
    args.add_argument('-list_type',type=str,default='e',choices=['e','i'],help='if "e" all parent of leaf within leaves list will except collapse, and "i" do reverse.')
    args.add_argument('-collapsed_node_name',type=str,default='CLPS',help='node name prefix of collapsed nodes.')
    args.add_argument('-orientation', type=str, default='lr', choices=['lr','rl'], help='orientaion when alg greed find node. used when algrisme "greed" chosed.')
    args.add_argument('-o_tree_fname',type=str,default='collapsed_tree_'+offer_timemarker()+'.nwk',help='tree file name of collapsed.')
    args.add_argument('-o_tree_plot_fname',type=str,default='collapsed_tree_plot_'+offer_timemarker()+'.pdf',help='a plot of collapsed tree.')
    args.add_argument('-o_collapsed_node_fname',type=str,default='collapsed_node_'+offer_timemarker()+'.ndi',help='file contain node information which was collapsed.')
    args=args.parse_args()
    alg=args.alg
    tree_file=args.tree_file
    dist_type=args.dist_type
    collapse_value=args.collapse_value
    list_type=args.list_type
    list_file=args.list_file
    collapsed_node_name=args.collapsed_node_name
    orientation=args.orientation
    o_tree_fname=args.o_tree_fname
    o_tree_plot_fname=args.o_tree_plot_fname
    o_collapsed_node_fname=args.o_collapsed_node_fname

    return alg,tree_file,dist_type,collapse_value,list_type,list_file,collapsed_node_name,orientation,o_tree_fname,o_tree_plot_fname,o_collapsed_node_fname

def get_except_leaf_node(tree,list_file,list_type):
    # get leaf node which should be keep when collapse performing.
    leaves_list=[]
    if list_file == 'None':
        if list_type=='e':
            return leaves_list
        elif list_type=='i':
            for leaf in tree:
                leaves_list.append(leaf)
            return leaves_list
    else:
        a_leaves_name=[line.rstrip() for line in open(list_file)]
        if list_type=='e':
            for leaf in tree:
                if leaf.name in a_leaves_name:
                    leaves_list.append(leaf)
            return leaves_list
        elif list_type == 'i':
            for leaf in tree:
                if leaf.name not in a_leaves_name:
                    leaves_list.append(leaf)
            return leaves_list

def get_longest_dist(tree):
    el_max=tree.get_farthest_leaf()
    nl_max=tree.get_farthest_leaf(topology_only=True)
    return el_max[1],nl_max[1]

def get_collapse_position(tree,collapse_value,dist_type):
    collapse_position=[]
    el_max,nl_max=get_longest_dist(tree)
    if len(collapse_value) not in [1,3]:
        raise Exception('error, worng collapse value amount.')
    if len(collapse_value)==1:
        if dist_type == 'el' or dist_type=='nl':
            collapse_position.append(collapse_value[0])
        elif dist_type=='elf':
            collapse_position.append(collapse_value[0]*el_max)
        elif dist_type=='nlf':
            collapse_position.append(collapse_value[0]*nl_max)
        else:
            raise Exception('error, wrong dist type.')
    else:
        i=0
        tmp=[]
        start=collapse_value[0]
        end=collapse_value[1]
        step=collapse_value[2]
        while True:
            point=start+i*step
            if point >= end:
                collapse_position.append(point)
                break
            collapse_position.append(point)
            i+=1
        if dist_type=='elf':
            for point in collapse_position:
                tmp.append(el_max*point)
            collapse_position=tmp
        elif dist_type=='nlf':
            for point in collapse_position:
                tmp.append(nl_max*point)
            collapse_position=tmp
    return collapse_position

def collapse_node(candidate_nodes,leaves_list,collapsed_node_name='CLPS',clps_count=0):
    collapsed_node={}
    node_need_collapse=[]
    for node in candidate_nodes:
        i=0
        for leaf in node:
            if leaf in leaves_list:
                i=1
                break
        if i==0:
            node_need_collapse.append(node)
    i=clps_count
    for node in node_need_collapse:
        if not node.is_leaf():
            i+=1
            node_keep=node.copy()
            for child in node.get_children():
                child.detach()
            new_name=collapsed_node_name+'_'+str(i)
            node.name=new_name
            collapsed_node[new_name]=node_keep

    return collapsed_node,i

def collapser_rl(tree,dist_type,collapse_position,leaves_list,collapsed_node_name='CLPS'):

    def get_candidate_node_by_el(root_node, node, el_cutoff):
        for child in node.children:
            if root_node.get_distance(child) >= el_cutoff:
                all_candidate_nodes.append(child)
            else:
                get_candidate_node_by_el(root_node,child,el_cutoff)

    def get_candidate_node_by_nl(root_node, node, nl_cutoff):
        for child in node.children:
            if root_node.get_distance(child, topology_only=True) >= nl_cutoff:
                all_candidate_nodes.append(child)
            else:
                get_candidate_node_by_nl(root_node, child, nl_cutoff)

    clps_count_used=0
    a_collapsed_node={}
    for cutoff in collapse_position:
        all_candidate_nodes=[]
        i=clps_count_used
        if dist_type=='el' or dist_type=='elf':
            get_candidate_node_by_el(tree,tree,cutoff)
        elif dist_type=='nl' or dist_type=='nlf':
            get_candidate_node_by_nl(tree,tree,cutoff)
        collapsed_node,clps_count_used=collapse_node(all_candidate_nodes,leaves_list,collapsed_node_name,i)
        a_collapsed_node.update(collapsed_node)
    return a_collapsed_node

def collapser_rl_go(tree,dist_type,collapse_value,list_type,list_file,collapsed_node_name):
    leaves_list=get_except_leaf_node(tree, list_file, list_type)
    collapse_position=get_collapse_position(tree, collapse_value, dist_type)
    collapsed_node=collapser_rl(tree, dist_type, collapse_position, leaves_list, collapsed_node_name)
    return collapsed_node

def collapse_lr(tree, dist_type, collapse_position, leaves_list, collapsed_node_name='CLPS'):
    def get_candidate_node_by_el(leaf, node, el_cutoff):
        if node and  node.get_distance(leaf)>=el_cutoff:
            all_candidate_nodes.add(node)
        elif node:
            get_candidate_node_by_el(leaf, node.up, el_cutoff)

    def get_candidate_node_by_nl(leaf, node, nl_cutoff):
        if node and node.get_distance(leaf, topology_only=True)>=nl_cutoff:
            all_candidate_nodes.add(node)
        elif node:
            get_candidate_node_by_nl(leaf, node.up, nl_cutoff)

    clps_count_used=0
    all_collapsed_nodes={}
    for cutoff in collapse_position:
        all_candidate_nodes=set()
        i=clps_count_used
        if dist_type=='el' or dist_type=='elf':
            for leaf in tree:
                get_candidate_node_by_el(leaf, leaf.up, cutoff)
        elif dist_type=='nl' or dist_type=='nlf':
            for leaf in tree:
                get_candidate_node_by_nl(leaf, leaf.up, cutoff)

        collapsed_node,clps_count_used=collapse_node(all_candidate_nodes,leaves_list,collapsed_node_name,i)
        all_collapsed_nodes.update(collapsed_node)
    return all_collapsed_nodes

def collapse_lr_go(tree,dist_type,collapse_value,list_type,list_file,collapsed_node_name):
    collapse_position=get_collapse_position(tree, collapse_value, dist_type)
    leaves_list=get_except_leaf_node(tree, list_file, list_type)
    collapsed_node=collapse_lr(tree, dist_type, collapse_position, leaves_list, collapsed_node_name)
    return collapsed_node

def collapse_greed(tree, keeped_nodes, leaves_list):
    for node in keeped_nodes:
        while node:
            for sister in node.get_sisters():
                if True not in map(lambda x : x in leaves_list,sister):
                    sister.detach()
            node=node.up

def collapse_greed_lr(tree, collapse_value, dist_type, leaves_list):
    def get_candidate_node_by_el(leaf, node, el_cutoff):
        if node and node.get_distance(leaf)>=el_cutoff:
            all_candidate_nodes.add(node)
        elif node:
            get_candidate_node_by_el(leaf, node.up, el_cutoff)

    def get_candidate_node_by_nl(leaf, node, nl_cutoff):
        #print(node)
        if node and node.get_distance(leaf, topology_only=True)>=nl_cutoff:
            all_candidate_nodes.add(node)
        elif node:
            get_candidate_node_by_nl(leaf, node.up, nl_cutoff)

    all_candidate_nodes=set()
    cutoff=collapse_value
    if dist_type=='el' or dist_type=='elf':
        for leaf in leaves_list:
            get_candidate_node_by_el(leaf, leaf.up, cutoff)
    elif dist_type=='nl' or dist_type=='nlf':
        for leaf in leaves_list:
            get_candidate_node_by_nl(leaf, leaf.up, cutoff)
    all_keeped_node=all_candidate_nodes
    collapse_greed(tree, all_keeped_node, leaves_list)

def collapse_greed_rl(tree, collapse_value, dist_type, leaves_list):
    def get_candidate_node_by_el(root_node, node, el_cutoff):
        for child in node.children:
            if node and root_node.get_distance(child) >= el_cutoff:
                all_candidate_nodes.append(child)
            elif node:
                get_candidate_node_by_el(root_node,child,el_cutoff)

    def get_candidate_node_by_nl(root_node, node, nl_cutoff):
        for child in node.children:
            if node and root_node.get_distance(child, topology_only=True) >= nl_cutoff:
                all_candidate_nodes.append(child)
            elif node:
                get_candidate_node_by_nl(root_node, child, nl_cutoff)

    cutoff=collapse_value
    all_candidate_nodes=[]
    if dist_type=='el' or dist_type=='elf':
        get_candidate_node_by_el(tree,tree,cutoff)
    elif dist_type=='nl' or dist_type=='nlf':
        get_candidate_node_by_nl(tree,tree,cutoff)
    keeped_nodes=[]
    for node in all_candidate_nodes:
        if True in map(lambda x:x in leaves_list, node):
            keeped_nodes.append(node)
    collapse_greed(tree, keeped_nodes, leaves_list)

def collapse_greed_go(tree, dist_type, collapse_value, list_type, list_file, orientation):
    if len(collapse_value)>1:
        raise Exception('too many collapse value.')
    else:
        collapse_position=get_collapse_position(tree, collapse_value, dist_type)[0]
    leaves_list=get_except_leaf_node(tree, list_file, list_type)
    if orientation=='lr':
        collapse_greed_lr(tree, collapse_position, dist_type, leaves_list)
    elif orientation=='rl':
        collapse_greed_rl(tree, collapse_position, dist_type, leaves_list)

def main():
    alg,tree_file,dist_type,collapse_value,list_type,list_file,collapsed_node_name,orientation,o_tree_fname,o_tree_plot_fname,o_collapsed_node_fname=get_args()
    tree=ete3.Tree(tree_file)
    #print(tree)
    if alg=='r2l_hier':
        collapsed_node=collapser_rl_go(tree,dist_type,collapse_value,list_type,list_file,collapsed_node_name)
        print(tree)
        for node in collapsed_node:
            print(node)
            print(collapsed_node[node].write())
    elif alg=='l2r_hier':
        collapsed_node=collapse_lr_go(tree, dist_type, collapse_value, list_type, list_file, collapsed_node_name)
        print(tree)
        for node in collapsed_node:
            print(node)
            print(collapsed_node[node].write())
    elif alg=='greed':
        collapse_greed_go(tree, dist_type, collapse_value, list_type, list_file, orientation)
        print(tree)
        #tree.render('hhhhh.pdf')


if __name__ == '__main__':
    main()
