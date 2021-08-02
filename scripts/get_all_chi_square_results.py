import pandas as pd
from statsmodels.stats.multitest import multipletests
from lxml import etree
import os
from pathlib import Path
import argparse


def find_upmost_parent(element, parent_list):
    if element.tag in parent_list:
        res = element.tag
    elif element.getparent().tag in parent_list:
        res = element.getparent().tag
    else:
        res = find_upmost_parent(element.getparent(), parent_list)
    return res


def isrepresented_by_children(disease, disease_group_tree, disease_res_df, column_name='disease'):
    children_diseases = set([item.tag for item in disease_group_tree.getchildren()])
    affected_individual_num = disease_res_df['Disease_number_within_Drug_Use'][disease_res_df[column_name]==disease].values[0]
    children_affected_individual_num = 0
    for child_disease in children_diseases:
        if child_disease in disease_res_df[column_name].unique():
            children_affected_individual_num += disease_res_df['Disease_number_within_Drug_Use'][disease_res_df[column_name]==child_disease].values[0]
    if children_affected_individual_num >= affected_individual_num*0.8:
        print(f"{disease} is fully represnted by its children.")
        return True
    else:
        return False


def parse():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--input_directory', dest='input_directory', type=str)
    argument_parser.add_argument('--xml_directory', dest='xml_directory', type=str)
    argument_parser.add_argument('--output_directory', dest='output_directory', type=str)
    return argument_parser.parse_args()


def main():
    arguments = parse()
    input_directory = Path(arguments.input_directory)
    xml_directory = Path(arguments.xml_directory)
    output_directory = Path(arguments.output_directory)
    # read from the xml file
    disease_et = etree.parse(xml_directory/"anomalies_ontology.xml")
    drug_et = etree.parse(xml_directory/"medication_atccodes_ontology.xml")
    res_df = pd.read_csv(input_directory/'allcombinations_atccodes_results.tsv', sep='\t')
    res_othermedication = pd.read_csv(input_directory/'allcombinations_othermedications_results.tsv', sep='\t')
    res_df = res_df[res_df['Disease_number_within_Drug_Use'] > 10]
    res_df['corrected_df'] = multipletests(res_df['p'], method='fdr_bh')[1]
    sig_res_df = res_df[res_df['corrected_df'] < 0.05]
    res_othermedication = res_othermedication[res_othermedication['Disease_number_within_Drug_Use'] > 10]
    res_othermedication['corrected_df'] = multipletests(res_othermedication['p'], method='fdr_bh')[1]
    sig_res_othermedication = res_othermedication[res_othermedication['corrected_df'] < 0.05]
    # add the most upper parent to each medication & anomaly
    disease_root = disease_et.getroot()
    parent_list = [item.tag for item in disease_root.getchildren()]
    res_df['upmost_disease_parent'] = [find_upmost_parent(disease_et.xpath(f'//{disease}')[0], parent_list)
                                       for disease in res_df['disease']]
    sig_res_othermedication['upmost_disease_parent'] = [
        find_upmost_parent(disease_et.xpath(f'//{disease}')[0], parent_list)
        for disease in sig_res_othermedication['disease']]
    drug_root = drug_et.getroot()
    drug_parent_list = [item.tag for item in drug_root.getchildren()]
    res_df['upmost_drug_parent'] = [find_upmost_parent(drug_et.xpath(f'//{drug}')[0], drug_parent_list)
                                    for drug in res_df['drug']]
    res_df_noduplicated_diseases = pd.DataFrame()
    for disease_group in sig_res_df['upmost_disease_parent'].unique():
        drug_list = sig_res_df['drug'][(sig_res_df['upmost_disease_parent'] == disease_group)].unique()
        for drug in drug_list:
            subset_res_df = sig_res_df[(sig_res_df['upmost_disease_parent'] == disease_group) &
                                       (sig_res_df['drug'] == drug)]
            subset_res_df['is_represented_by_children_diseases'] = [isrepresented_by_children(disease,
                                                                                              disease_et.xpath(
                                                                                                  f'//{disease}')[0],
                                                                                              subset_res_df)
                                                                    for disease in subset_res_df['disease']]

            num = subset_res_df[subset_res_df['is_represented_by_children_diseases']].shape[0]
            if num > 0:
                print(f"Deleting {num} diseases that are fully represented in its children.")
            subset_res_df = subset_res_df[subset_res_df['is_represented_by_children_diseases'] == False]
            res_df_noduplicated_diseases = pd.concat([res_df_noduplicated_diseases, subset_res_df], axis=0)
    sig_res_othermedication_noduplicated_diseases = pd.DataFrame()
    for disease_group in sig_res_othermedication['upmost_disease_parent'].unique():
        drug_list = sig_res_othermedication['drug'][
            (sig_res_othermedication['upmost_disease_parent'] == disease_group)].unique()
        for drug in drug_list:
            subset_res_df = sig_res_othermedication[
                (sig_res_othermedication['upmost_disease_parent'] == disease_group) &
                (sig_res_othermedication['drug'] == drug)]
            subset_res_df['is_represented_by_children_diseases'] = [isrepresented_by_children(disease,
                                                                                              disease_et.xpath(
                                                                                                  f'//{disease}')[0],
                                                                                              subset_res_df)
                                                                    for disease in subset_res_df['disease']]

            num = subset_res_df[subset_res_df['is_represented_by_children_diseases']].shape[0]
            if num > 0:
                print(f"Deleting {num} diseases that are fully represented in its children.")
            subset_res_df = subset_res_df[subset_res_df['is_represented_by_children_diseases'] == False]
            sig_res_othermedication_noduplicated_diseases = pd.concat([sig_res_othermedication_noduplicated_diseases,
                                                                       subset_res_df], axis=0)
    res_df_uniquecombi = pd.DataFrame()
    for drug_group in res_df_noduplicated_diseases['upmost_drug_parent'].unique():
        for disease in res_df_noduplicated_diseases['disease'][res_df['upmost_drug_parent'] == drug_group].unique():
            subset_res_df = res_df_noduplicated_diseases[
                (res_df_noduplicated_diseases['upmost_drug_parent'] == drug_group) &
                (res_df_noduplicated_diseases['disease'] == disease)]
            subset_res_df['is_represented_by_children_drugs'] = [isrepresented_by_children(drug,
                                                                                           drug_et.xpath(f'//{drug}')[
                                                                                               0],
                                                                                           subset_res_df,
                                                                                           'drug')
                                                                 for drug in subset_res_df['drug']]
            num = subset_res_df[subset_res_df['is_represented_by_children_drugs']].shape[0]
            if num > 0:
                print(f"Deleting {num} drug that are fully represented in its children.")
            res_df_uniquecombi = pd.concat([res_df_uniquecombi,
                                            subset_res_df[subset_res_df['is_represented_by_children_drugs'] == False]],
                                           axis=0)
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)
    res_df_uniquecombi.sort_values(by=['upmost_disease_parent',
                                       'upmost_drug_parent']).to_csv(output_directory/'pruned_atccodes_results.tsv',
                                                                     sep='\t')

    sig_res_othermedication_noduplicated_diseases.sort_values(by=['upmost_disease_parent']).to_csv(
        output_directory/'pruned_othermedications_results.tsv',
        sep='\t')

if __name__ == '__main__':
    main()

