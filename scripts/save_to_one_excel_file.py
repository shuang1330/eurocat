import pandas as pd
import argparse
from pathlib import Path

def parse():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--results_directory', dest='results_directory', type=str)
    return argument_parser.parse_args()

def main():
    arguments = parse()
    results_dir = Path(arguments.results_directory)
    save_cols = ['Drug_use_number', 'Disease_number_within_Drug_Use',
                 'Disease_ratio_within_Drug_Use', 'p', 'expected_disease_ratio',
                 'odds_ratio', 'odds_ratio_ci_lower', 'odds_ratio_ci_higher', 'disease',
                 'drug', 'corrected_p']
    df1 = pd.read_csv(results_dir/'allcombinations_atccodes_results.tsv', sep='\t')
    df2 = pd.read_csv(results_dir/'allcombinations_othermedications_results.tsv', sep='\t')
    df3 = pd.read_csv(results_dir/'significant_atccodes_results.tsv', sep='\t')
    df4 = pd.read_csv(results_dir/'significant_othermedications_results.tsv', sep='\t')
    df5 = pd.read_csv(results_dir/'pruned_atccodes_results.tsv', sep='\t')
    df6 = pd.read_csv(results_dir/'pruned_othermedications_results.tsv', sep='\t')

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(results_dir/'merged_results.xlsx', engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    df1.to_excel(writer, sheet_name='allcombinations_atccodes')
    df2.to_excel(writer, sheet_name='allcombinations_othermedi')
    df3.to_excel(writer, sheet_name='significant_atccodes')
    df4.to_excel(writer, sheet_name='significant_othermedications')
    df5[save_cols].to_excel(writer, sheet_name='pruned_atccodes')
    df6[save_cols].to_excel(writer, sheet_name='pruned_othermedications')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

if __name__ == '__main__':
    main()