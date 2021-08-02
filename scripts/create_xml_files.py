from lxml import etree
import argparse
from pathlib import Path

disease_dict = {'nervsyst': {'ntd': ['anenceph', 'spinabif','encephal'],
                             'hydrocep':[],
                             'microcep':[],
                             'arhinenc':[]},
              'eyeanom': {'an_micro': ['anophtal', 'micropht'],
                          'cataract': [],
                          'glaucoma': [],
                          'buphthalmos': []},
              'earanom': {'earfaceneck': ['anotia']},
              'heartdef': {'severechd': ['comarttrun', 'dtranspos',
                                        'alltranspos', 'DORV',
                                        'fallot', 'singvent'],
                             'ASD':['AVSD'],
                             'VSD':['mVSD', 'pVSD'],
                           'bicuspidao':[],
                           'IAA':[],
                           'pulmatr':[],
                           'pulmsten':[],
                           'tricusp':[],
                           'ebstein':[],
                           'aortsten':[],
                           'sub_supra_aortsten':[],
                           'hypoleft':[],
                           'hyporight':[],
                           'patductarte':[],
                           'coarctat':[],
                           'TAPVR':[]},
              'respirat': ['choanatr', 'CCAM','lunghypo'],
              'ofclefts': ['cpalate', 'cleftlip', 'clippal', 'liporpal'],
              'digestiv': ['oesoph', 'smintest', 'atrsteduode','anorecta', 'hirschpr', 'bileatre',
                           'pananna', 'diahernia', 'pylosten', 'malrotat'],
              'genital': ['hypospad', 'indetsex'],
              'urinary': {'bladepi': ['epispadi', 'exbladder'],
                          'bilrenage':{'renaldys': ['multicyst'],
                                       'hydronep': [],
                                       'prunebel':[],
                                       'posturvalve': [],
                                       'uretatrsten': [],
                                       'megauret': [],
                                       'VUR': [],
                                       'horsshoe':[]}},
              'limbanom': {'reddefec':['reddefup', 'reddeflo'],
                            'limbabs': [],
                            'clubft': [],
                            'hip': [],
                           'polydact':['polydacthand', 'polydactfeet'],
                           'syndacty':['syndactyhand', 'syndactyfeet']},
              'abwaldef': ['gastrosc', 'omphaloc'],
              'chromoso':['down',
                          'patau',
                          'edwards',
                          'turner',
                          'klinefel',
                          'triploid'],
              'skeletdys':[],
               'craniosyn':[],
                'amniotic':[],
                'inversus':[],
                'skindis':[],
                'terasyn':[],
                'fetalalcohol':[],
                'valproate':[],
                'MCA':[],
                'hydrops':[]}

drug_dict = {'A01T1': [],
             'A02T1': [],
             'A03T1': [],
             'A04T1': [],
             'A05T1': [],
             'A06T1': [],
             'A07T1': [],
             'A08T1': [],
             'A09T1': [],
             'A10T1': ['A10AT1', 'A10BT1', 'A10XT1', 'A11CT1'],
             'A11T1': [],
             'A12T1': [],
             'A13T1': [],
             'A14T1': [],
             'A15T1': [],
             'A16T1': [],
             'B01T1': [],
             'B02T1': [],
             'B03T1': {'B03AT1': [],
                       'B03BT1': ['B03BB01T1']},
             'B05T1': [],
             'B06T1': [],
             'C01T1': [],
             'C02T1': [],
             'C03T1': [],
             'C04T1': [],
             'C05T1': [],
             'C07T1': [],
             'C08T1': [],
             'C09T1': [],
             'C10T1': [],
             'D01T1': ['D01BT1'],
             'D02T1': [],
             'D03T1': [],
             'D04T1': [],
             'D05T1': [],
             'D06T1': [],
             'D07T1': [],
             'D08T1': [],
             'D09T1': [],
             'D10T1': ['D10BT1'],
             'D11T1': [],
             'G01T1': [],
             'G02T1': [],
             'G03T1': ['G03AT1', 'G03BT1', 'G03CT1', 'G03DT1', 'G03GT1', 'G03HT1', 'G03XT1'],
             'G04T1': [],
             'H01T1': ['H01CT1'],
             'H02T1': [],
             'H03T1': [],
             'H04T1': [],
             'H05T1': [],
             'J01T1': ['J01AT1', 'J01CT1', 'J01ET1', 'J01FT1', 'J01GT1'],
             'J02T1': [],
             'J04T1': [],
             'J05T1': [],
             'J06T1': [],
             'J07T1': [],
             'L01T1': [],
             'L02T1': [],
             'L03T1': [],
             'L04T1': [],
             'M01T1': [],
             'M02T1': [],
             'M03T1': [],
             'M04T1': [],
             'M05T1': [],
             'M09T1': [],
             'N01T1': [],
             'N02T1': {'N02AT1': ['N02AA05T1'],
                       'N02BT1': [],
                       'N02CT1': []},
             'N03T1': [],
             'N04T1': [],
             'N05T1': {'N05AT1': ['N05AN01T1'],
                       'N05BT1': [],
                       'N05CT1': []},
             'N06T1': {'N06AT1': ['N06AAT1', 'N06ABT1', 'N06AFT1', 'N06AGT1', 'N06AXT1'],
                       'N06BT1': [],
                       'N06CT1': [],
                       'N06DT1': []},
             'N07T1': [],
             'P01T1': ['P01AT1', 'P01BT1','P01CT1'],
             'P02T1': [],
             'P03T1': [],
             'R01T1': ['R01AT1', 'R01BT1'],
             'R02T1': [],
             'R03T1': ['R03AT1', 'R03BT1', 'R03CT1', 'R03DT1'],
             'R05T1': ['R05CT1', 'R05DT1'],
             'R06T1': [],
             'R07T1': [],
             'S01T1': ['S01AT1', 'S01BT1', 'S01ET1', 'S01FT1', 'S01GT1', 'S01HT1', 'S01JT1', 'S01LT1'],
             'S02T1': [],
             'S03T1': [],
             'V01T1': [],
             'V03T1': [],
             'V04T1': [],
             'V06T1': [],
             'V07T1': [],
             'V08T1': [],
             'V09T1': [],
             'V10T1': [],
             'V20T1': [],
             'foliumzuur': []}

def add_elements_from_list(disease_subtree, list_of_diseases):
    if len(list_of_diseases) > 0:
        for disease in list_of_diseases:
            final_level_tree = etree.SubElement(disease_subtree, disease)
        return final_level_tree
    else:
        return None

def add_trees_from_dict(disease_subtree, dict_of_diseases):
    for key in dict_of_diseases.keys():
        next_level_tree = etree.SubElement(disease_subtree, key)
        if type(dict_of_diseases[key]) == list:
            next_level_tree = add_elements_from_list(next_level_tree, dict_of_diseases[key])
        else:
            next_level_tree = add_trees_from_dict(next_level_tree, dict_of_diseases[key])
    return next_level_tree

def parse():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--output_directory', dest='output_directory', type=str)
    return argument_parser.parse_args()

def main():
    arguments = parse()
    output_dir = Path(arguments.output_directory)
    disease_root = etree.Element("root")
    for key in disease_dict.keys():
        disease_firstlevel = etree.SubElement(disease_root, key)
        if type(disease_dict[key]) == list:
            disease_subtree = add_elements_from_list(disease_firstlevel, disease_dict[key])
        else:
            disease_subtree = add_trees_from_dict(disease_firstlevel, disease_dict[key])
    # save the tree in a xml file
    disease_et = etree.ElementTree(disease_root)
    disease_et.write(output_dir/'anomalies_ontology.xml', pretty_print=True)
    drug_root = etree.Element("root")
    for key in drug_dict.keys():
        drug_firstlevel = etree.SubElement(drug_root, key)
        if type(drug_dict[key]) == list:
            drug_subtree = add_elements_from_list(drug_firstlevel, drug_dict[key])
        else:
            drug_subtree = add_trees_from_dict(drug_firstlevel, drug_dict[key])
    # save the tree in a xml file
    drug_et = etree.ElementTree(drug_root)
    drug_et.write(output_dir/'medication_atccodes_ontology.xml', pretty_print=True)

if __name__ == '__main__':
    main()