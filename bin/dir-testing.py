import os

bin_dir = os.path.dirname(os.path.abspath(__file__)) # /home/bryan/Documents/ADFTool/bin
root_dir = os.path.dirname(bin_dir) # /home/bryan/Documents/ADFTool
scripts_dir = os.path.join(root_dir, "scripts") # /home/bryan/Documents/ADFTool/scripts
result_dir = os.path.join(os.path.dirname(root_dir), "results") # /home/bryan/Documents/ADFTool/results
print(bin_dir)
print(root_dir)
print(scripts_dir)
print(result_dir)