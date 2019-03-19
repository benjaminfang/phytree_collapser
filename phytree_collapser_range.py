#! /usr/bin/env python3
import argparse
import ete3
import phytree_collapser as collapser

def get_args():
    args=argparse.ArgumentParser(description='collapse whitin a range.')
    args.add_argument('-tree_file',type=str,required=True,help='tree file.')
    args.add_argument('-start',type=float,required=True,help='range start.')
    args.add_argument('-end',type=float,required=True,help='range end.')
    args.add_argument('-step_len',type=float,required=True,help='step length.')
    args.add_argument('-dist_type',type=str,required=True,help='distance type.')
    args.add_argument('-list_file',type=str,default='None',help='leaf node list file name.')
    args=args.parse_args()
    tree_file,start,end,step_len,dist_type,list_file=args.tree_file,args.start,args.end,args.step_len,args.dist_type,args.list_file
    return tree_file,start,end,step_len,dist_type,list_file

tree_file,start,end,step_len,dist_type,list_file=get_args()
tree=ete3.Tree(tree_file)
leaves_list=collapser.get_node_list(tree,list_file)
i=0
j=0
while True:
    if j==1:break
    collapse_value=start+i*step_len
    collapsed_node_name='CLPS'+str(i)+'_'
    if  collapse_value > end:
        collapse_value=end
        j=1
    collapser.collapser(tree,dist_type,collapse_value,'e',leaves_list,collapsed_node_name)
    i+=1

tree.write(outfile='tree_res.nwk',format=0)
tree.render('tree_res.pdf')
