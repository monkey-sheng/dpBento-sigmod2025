# remove the csv files

import os


curr_dir = os.path.dirname(os.path.realpath(__file__))

# remove if exist
if os.path.exists(os.path.join(curr_dir, 'lat.out')):
    os.remove(os.path.join(curr_dir, 'lat.out'))
if os.path.exists(os.path.join(curr_dir, 'lat.csv')):
    os.remove(os.path.join(curr_dir, 'lat.csv'))
if os.path.exists(os.path.join(curr_dir, 'band.csv')):
    os.remove(os.path.join(curr_dir, 'band.csv'))
if os.path.exists(os.path.join(curr_dir, 'band.out')):
    os.remove(os.path.join(curr_dir, 'band.out'))
print("Removed all csv files for memory benchmarks")
