# phytree_collapser
initial time: 20190310.
a ultilty to collapse phylogenic tree.

usage: phytree_collapser.py [-h] -tree_file TREE_FILE -collapse_proportion
                            COLLAPSE_PROPORTION [-dist_type {el,nl}]
                            [-list_type {e,i}] [-list_file LIST_FILE]
                            [-collapsed_node_name COLLAPSED_NODE_NAME]
                            [-o_tree_fname O_TREE_FNAME]
                            [-o_tree_plot_fname O_TREE_PLOT_FNAME]
                            [-o_collapsed_node_fname O_COLLAPSED_NODE_FNAME]

this is a utility for collapsing phylogenic tree.

optional arguments:
  -h, --help            show this help message and exit
  -tree_file TREE_FILE  the file name of newik tree.
  -collapse_proportion COLLAPSE_PROPORTION
                        proportion of oritation "root node to leaf",node out
                        this proportion will be collapsed.
  -dist_type {el,nl}    distance type. el for edge distance, nl for node
                        distance.
  -list_type {e,i}      if "e" all parent of leaf within leaves list will
                        except collapse, and "i" do reverse.
  -list_file LIST_FILE  leaf node list file name.
  -collapsed_node_name COLLAPSED_NODE_NAME
                        node name prefix of collapsed nodes.
  -o_tree_fname O_TREE_FNAME
                        tree file name of collapsed.
  -o_tree_plot_fname O_TREE_PLOT_FNAME
                        a plot of collapsed tree.
  -o_collapsed_node_fname O_COLLAPSED_NODE_FNAME
                        file contain node information which was collapsed.

any problem please contect benjaminfang.ol@outlook.com, or visite
https://github.com/benjaminfang.
