import pandas as pd
import numpy as np
from scipy.stats.contingency import expected_freq
from scipy.stats import chi2_contingency
from statsmodels.stats.contingency_tables import Table2x2
from tqdm import tqdm
from pathlib import Path
import argparse


anomalies_list = ['nervsyst', 'anenceph', 'spinabif',
       'encephal', 'ntd', 'hydrocep', 'microcep', 'arhinenc', 'eyeanom',
       'anophtal', 'micropht', 'glaucoma', 'buphthalmos', 'an_micro',
       'cataract', 'earanom', 'earfaceneck', 'anotia', 'heartdef',
       'severechd', 'comarttrun', 'dtranspos', 'alltranspos', 'DORV',
       'fallot', 'singvent', 'ASD', 'AVSD', 'VSD', 'mVSD', 'pVSD',
       'bicuspidao', 'IAA', 'pulmatr', 'pulmsten', 'tricusp', 'ebstein',
       'aortsten', 'sub_supra_aortsten', 'hypoleft', 'hyporight',
       'patductarte', 'coarctat', 'TAPVR', 'respirat', 'choanatr', 'CCAM',
       'lunghypo', 'ofclefts', 'cpalate', 'cleftlip', 'clippal',
       'liporpal', 'digestiv', 'oesoph', 'smintest', 'atrsteduode',
       'anorecta', 'hirschpr', 'bileatre', 'pananna', 'diahernia',
       'pylosten', 'malrotat', 'genital', 'hypospad', 'indetsex',
       'urinary', 'bladepi', 'epispadi', 'exbladder', 'bilrenage',
       'renaldys', 'multicyst', 'hydronep', 'prunebel', 'posturvalve',
       'uretatrsten', 'megauret', 'VUR', 'horsshoe', 'limbanom',
       'reddefec', 'reddefup', 'reddeflo', 'limbabs', 'clubft', 'hip',
       'polydact', 'polydacthand', 'polydactfeet', 'syndacty',
       'syndactyhand', 'syndactyfeet', 'abwaldef', 'gastrosc', 'omphaloc',
       'chromoso', 'down', 'patau', 'edwards', 'turner', 'klinefel',
       'triploid', 'skeletdys', 'craniosyn', 'amniotic', 'inversus',
       'skindis', 'terasyn', 'fetalalcohol', 'valproate', 'MCA',
       'hydrops']


atccodes_list = ['A01T1', 'A02T1', 'A03T1', 'A04T1', 'A05T1', 'A06T1', 'A07T1',
       'A08T1', 'A09T1', 'A10T1', 'A11T1', 'A12T1', 'A13T1', 'A14T1',
       'A15T1', 'A16T1', 'B01T1', 'B02T1', 'B03T1', 'B05T1', 'B06T1',
       'C01T1', 'C02T1', 'C03T1', 'C04T1', 'C05T1', 'C07T1', 'C08T1',
       'C09T1', 'C10T1', 'D01T1', 'D02T1', 'D03T1', 'D04T1', 'D05T1',
       'D06T1', 'D07T1', 'D08T1', 'D09T1', 'D10T1', 'D11T1', 'G01T1',
       'G02T1', 'G03T1', 'G04T1', 'H01T1', 'H02T1', 'H03T1', 'H04T1',
       'H05T1', 'J01T1', 'J02T1', 'J04T1', 'J05T1', 'J06T1', 'J07T1',
       'L01T1', 'L02T1', 'L03T1', 'L04T1', 'M01T1', 'M02T1', 'M03T1',
       'M04T1', 'M05T1', 'M09T1', 'N01T1', 'N02T1', 'N03T1', 'N04T1',
       'N05T1', 'N06T1', 'N07T1', 'P01T1', 'P02T1', 'P03T1', 'R01T1',
       'R02T1', 'R03T1', 'R05T1', 'R06T1', 'R07T1', 'S01T1', 'S02T1',
       'S03T1', 'V01T1', 'V03T1', 'V04T1', 'V06T1', 'V07T1', 'V08T1',
       'V09T1', 'V10T1', 'V20T1', 'A10AT1', 'A10BT1', 'A10XT1', 'A11CT1', 'B03AT1',
       'B03BT1', 'B03BB01T1', 'N05AN01T1', 'D01BT1', 'D10BT1', 'G03AT1',
       'G03BT1', 'G03CT1', 'G03DT1', 'G03GT1', 'G03HT1', 'G03XT1',
       'H01CT1', 'J01AT1', 'J01CT1', 'J01ET1', 'J01FT1', 'J01GT1',
       'N02AT1', 'N02AA05T1', 'N02BT1', 'N02CT1', 'N05AT1', 'N05BT1',
       'N05CT1', 'N06AT1', 'N06AAT1', 'N06ABT1', 'N06AFT1', 'N06AGT1',
       'N06AXT1', 'N06BT1', 'N06CT1', 'N06DT1', 'P01AT1', 'P01BT1',
       'P01CT1', 'R01AT1', 'R01BT1', 'R03AT1', 'R03BT1', 'R03CT1',
       'R03DT1', 'R05CT1', 'R05DT1', 'S01AT1', 'S01BT1', 'S01ET1',
       'S01FT1', 'S01GT1', 'S01HT1', 'S01JT1', 'S01LT1']

other_medications_list = ['foliumzuur', 'oxycodon', 'lithium', 'citalopram', 'lamotrigine',
       'carbamazepine', 'clobazam', 'valproinezuur', 'Tramadol',
       'ondansetron', 'mefloquine', 'hydroxocobalamine', 'escitalopram',
       'Tramadolparacetamol', 'omeprazol', 'fluoxetine', 'alprazolam',
       'atazanavir', 'emtricitabinetenofovir', 'mirtazapine',
       'venlafaxine', 'clomipramine', 'tretinoinecr', 'levetiracetam',
       'diethylstilbestrol', 'pertuzumab', 'trastuzumab', 'thiamazol',
       'adalimumab', 'cyproteronethinylestradiol', 'gelekoortsvaccin',
       'azathioprine', 'prednison', 'beclometasonformoterol',
       'prednisolon', 'salbutamol', 'varenicline', 'propylthiouracil',
       'nortriptyline', 'olanzapine', 'hydroxychloroquine', 'cetirizine',
       'clonazepam', 'haloperidol', 'cabergoline', 'quetiapine',
       'tacrolimus', 'cotrimoxazol', 'bupropion', 'lorazepam',
       'isotretinoine', 'paroxetine', 'sumatriptan', 'fentanyl',
       'papillomavirusvaccin']

def get_chi2_results(data, disease, drug):
    contigency_table = pd.crosstab(data[drug], data[disease])
    use_drug_number = data[(data[drug]==1)].shape[0]
    have_disease_number = data[(data[disease]==1)].shape[0]
    use_drug_and_have_disease_number = data[(data[disease]==1)&(data[drug]==1)].shape[0]
    negative_num = data[(data[disease]==0)&(data[drug]==0)].shape[0]
    if use_drug_number * have_disease_number * use_drug_and_have_disease_number * negative_num == 0:
        return None
    try:
        disease_ratio_in_drug_usages = use_drug_and_have_disease_number / use_drug_number
        expected_disease_ratio_in_drug_usages = expected_freq(contigency_table)[1][1]
        if np.prod(expected_freq(contigency_table)) == 0:
            return None
        stat, p, dof, expected = chi2_contingency(contigency_table, correction=True)
        table = Table2x2(contigency_table)
        od = table.oddsratio
        od_ci = table.oddsratio_confint(alpha=0.05)
        return use_drug_number, use_drug_and_have_disease_number, disease_ratio_in_drug_usages, p, \
               expected_disease_ratio_in_drug_usages, od, od_ci[0], od_ci[1]
    except:
        print("Some kind of error I didn't manage to catch..., see the contingency table below:")
        print(contigency_table)

def parse():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--inputsav', dest='input_path', type=str)
    argument_parser.add_argument('--output_directory', dest='output_directory', type=str)
    return argument_parser.parse_args()

def main():
    arguments = parse()
    # read input file
    data = pd.read_spss(arguments.input_path)
    # save results for ATCcodes & anomalies
    results = []
    for disease in tqdm(anomalies_list):
        for drug in atccodes_list:
            item = [get_chi2_results(data, disease, drug), disease, drug]
            if item[0] != None:
                results.append(list(item[0]) + item[1:])
    res_df = pd.DataFrame(data=results,
                          columns=['Drug_use_number', 'Disease_number_within_Drug_Use',
                                   'Disease_ratio_within_Drug_Use',
                                   'p', 'expected_disease_ratio', 'odds_ratio',
                                   'odds_ratio_ci_lower', 'odds_ratio_ci_higher',
                                   'disease', 'drug'])
    output_dir = Path(arguments.output_directory)
    res_df.to_csv(output_dir/'allcombinations_atccodes_results.tsv', sep='\t', index=False)
    # save results for other medications & anomalies
    other_results = []
    for disease in tqdm(anomalies_list):
        for drug in other_medications_list:
            item = [get_chi2_results(data, disease, drug), disease, drug]
            if item[0] != None:
                other_results.append(list(item[0]) + item[1:])
    res_df = pd.DataFrame(data=other_results,
                          columns=['Drug_use_number', 'Disease_number_within_Drug_Use', 'Disease_ratio_within_Drug_Use',
                                   'p', 'expected_disease_ratio', 'odds_ratio',
                                   'odds_ratio_ci_lower', 'odds_ratio_ci_higher',
                                   'disease', 'drug'])
    res_df.to_csv(output_dir/'allcombinations_othermedications_results.tsv', sep='\t', index=False)

if __name__ == '__main__':
    main()
