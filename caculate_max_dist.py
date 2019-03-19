#! /usr/bin/env python3
import argparse
import ete3

def get_args():
    args=argparse.ArgumentParser(description='calculate max distance from leaf to root.')
    args.add_argument('tree_file',type=str,help='tree file name.')
    args=args.parse_args()
    tree_file=args.tree_file

    return tree_file

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
    el_max=el_l[0][1]
    nl_max=nl_l[0][1]
    return el_max,nl_max

if __name__ == '__main__':
    tree_file=get_args()
    tree=ete3.Tree(tree_file)
    el_max,nl_max=get_longest_dist(tree)
    print('el_max:',el_max)
    print('nl_max:',nl_max)
