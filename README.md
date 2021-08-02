This repository has scripts & notebooks for 
1) creating chi square results for all possible medication-anomaly combinations; 
2) create the xml files, within which records the ATC code and anomaly hierachical structure
3) prune the results from 1) according to xml files in 2)


Below are instructions to use the scripts in scripts/ directory:
for step 1): ```scripts/create_all_chi_square_files.py --inputsav /path/to/input/sav/file --output_directory /path/to/save/output/files```
for step 2): ```scripts/create_xml_files.py --output_directory /path/to/save/xml/files```
for step 3): ```scripts/prune_results.py --input_directory /path/to/directory/where/results/in/step1/are/in --xml_directory /path/to/xml/directory --output_directory /path/to/save/pruned/results```
