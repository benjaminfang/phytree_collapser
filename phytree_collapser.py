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
    args.add_argument('-tree_file',type=str,required=True,help='the file name of newik tree.')
    args.add_argument('-collapse_proportion',type=float,required=True,help='proportion of oritation "root node to leaf",node out this proportion will be collapsed.')
    args.add_argument('-dist_type',type=str,default='el',choices=['el','nl'],help='distance type. el for edge distance, nl for node distance.')
    args.add_argument('-list_type',type=str,default='e',choices=['e','i'],help='if "e" all parent of leaf within leaves list will except collapse, and "i" do reverse.')
    args.add_argument('-list_file',type=str,default='None',help='leaf node list file name.')
    args.add_argument('-collapsed_node_name',type=str,default='CLPS',help='node name prefix of collapsed nodes.')
    args.add_argument('-o_tree_fname',type=str,default='collapsed_tree_'+offer_timemarker()+'.nwk',help='tree file name of collapsed.')
    args.add_argument('-o_tree_plot_fname',type=str,default='collapsed_tree_plot_'+offer_timemarker()+'.pdf',help='a plot of collapsed tree.')
    args.add_argument('-o_collapsed_node_fname',type=str,default='collapsed_node_'+offer_timemarker()+'.ndi',help='file contain node information which was collapsed.')
    args=args.parse_args()
    tree_file=args.tree_file
    dist_type=args.dist_type
    collapse_proportion=args.collapse_proportion
    list_type=args.list_type
    list_file=args.list_file
    collapsed_node_name=args.collapsed_node_name
    o_tree_fname=args.o_tree_fname
    o_tree_plot_fname=args.o_tree_plot_fname
    o_collapsed_node_fname=args.o_collapsed_node_fname

    return tree_file,dist_type,collapse_proportion,list_type,list_file,collapsed_node_name,o_tree_fname,o_tree_plot_fname,o_collapsed_node_fname

def get_node_list(tree,list_file):
    leaves_list=[]
    if list_file == 'None':
        return leaves_list
    else:
        a_leaves_name=[line.rstrip() for line in open(list_file)]
        for leaf in tree:
            if leaf.name in a_leaves_name:
                leaves_list.append(leaf)

    return leaves_list

def collapser(tree,dist_type,collapse_proportion,list_type,leaves_list,collapsed_node_name='CLPS'):
    def get_longest_dist(tree):
        el_l=[]
        nl_l=[]
        for leaf in tree:
            el=tree.get_distance(leaf)
            nl=tree.get_distance(leaf,topology_only=True)
            el_l.append([leaf,el])
            nl_l.append([leaf,nl])
        el_l.sort(key=lambda x:x[1],reverse=True)
        nl_l.sort(key=lambda x:x[1],reverse=True)
#        print(el_l[0:2])
#        print(nl_l[0:2])
        el_max=el_l[0][1]
        nl_max=nl_l[0][1]
        return el_max,nl_max

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

    def collapse_node(candidate_nodes,list_type,leaves_list,collapsed_node_name='CLPS'):
        collapsed_node={}
        print(leaves_list)
        node_need_collapse=[]
        if list_type=='e':
            for node in candidate_nodes:
                i=0
                for leaf in node:
                    if leaf in leaves_list:
                        i=1
                        break
                if i==0:
                    #print(node)
                    node_need_collapse.append(node)
        elif list_type=='i':
            for node in candidate_nodes:
                #print(node)
                i=0
                for leaf in node:
                    if leaf in leaves_list:
                        #print(leaf)
                        i=1
                        break
                if i==1:
                    #print(node)
                    node_need_collapse.append(node)
            #print(node_need_collapse)
        i=0
        for node in node_need_collapse:
            if not node.is_leaf():
                i+=1
                node_keep=node.copy()
                for child in node.get_children():
                    child.detach()
                new_name=collapsed_node_name+'_'+str(i)
                node.name=new_name
                collapsed_node[new_name]=node_keep

        return collapsed_node

    el_max,nl_max=get_longest_dist(tree)
    all_candidate_nodes=[]
    if dist_type=='el':
        el_cutoff=el_max*collapse_proportion
        get_candidate_node_by_el(tree,tree,el_cutoff)
    elif dist_type=='nl':
        nl_cutoff=nl_max*collapse_proportion
        get_candidate_node_by_nl(tree,tree,nl_cutoff)
    else:
        print('error...')

    collapsed_node=collapse_node(all_candidate_nodes,list_type,leaves_list,collapsed_node_name)

    return collapsed_node


if __name__ == '__main__':
    tree_file,dist_type,collapse_proportion,list_type,list_file,collapsed_node_name,o_tree_fname,o_tree_plot_fname,o_collapsed_node_fname=get_args()
    tree=ete3.Tree(tree_file)
    leaves_list=get_node_list(tree,list_file)
    collapsed_node=collapser(tree,dist_type,collapse_proportion,list_type,leaves_list,collapsed_node_name)
    #print(tree,dist_type,collapse_proportion,list_type,leaves_list,collapsed_node_name)

    tree.write(outfile=o_tree_fname,format=0)
    tree.render(o_tree_plot_fname)
    o_collapsed_node_file=open(o_collapsed_node_fname,'w')
    for node_name in collapsed_node:
        print('>',node_name,file=o_collapsed_node_file)
        print(collapsed_node[node_name].write(),file=o_collapsed_node_file)
