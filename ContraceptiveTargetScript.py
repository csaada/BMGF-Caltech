# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:58:55 2021

@author: Carrie
"""
import proteinAtlasAccess as paa
import openTargetsAccess as ota
import ContraceptiveConstants as cc
from datetime import datetime
import csv
import time
import pandas as pd



def compare_targets(csv_str, ens_col = cc.ENSID_KEY):
    """
    Given a csv of targets with ensembl IDs, generates a dataframe and adds
    the protein atlas information for each target. Names for new columns are
    provided in ContraceptiveConstants.py. Currently, added data are:
        -the RNA tissue data from the Human Protein Atlas
        -the protein tissue data from the Human Protein Atlas
        
    Parameters
    ----------
    csv_str : str
        a string that is the name of the csv file of targets. Expects a 
        csv with a column of ensembl IDs
    ens_col : str
        the name of the column containing ensembl IDs

    Returns
    -------
    target_df : df
        A a data frame containing the RNA and protein tissue data 
        from the Human Protein Atlas; in addition to the original information
        provided in the csv

    """
    counter = 0 #so I can see that it's working
    df = pd.read_csv(csv_str, encoding = 'utf-8-sig')
    #adding 3 columns: 
    #   -cc.RNA_EXP_KEY
    #   -cc.STROMA
    #   -cc.FOLLICLE
    rna = [None] * len(df)
    stroma = [None] * len(df)
    follicle = [None] * len(df)
    for i in range (len(df)):
        #Setup
        target_ID = df[ens_col][i]
        #if we have a valid ensembl ID:
        if type(target_ID) == str: 
            paXML = paa.get_protein_xml(target_ID)
            ovaryTissues = paa.get_ovary_tags(paXML)
            #RNA Expression
            norm_RNA_exp = paa.get_RNA_tissue_data(paXML, ovaryTissues)
            rna[i] = norm_RNA_exp
            #Protein Expression
            protein_dict = paa.get_protein_exp_data(paXML, ovaryTissues, 
                                                tissueTypes = cc.OVARY_TYPES)
            stroma[i] = protein_dict[cc.STROMA]
            follicle[i] = protein_dict[cc.FOLLICLE]
            #debug
            print(counter)
            counter += 1
            print(df[cc.GS_KEY][i])
        #otherwise, no ensembl ID, so report expression as not available
        #RNA will default to NaN since that column is floats, not strings
        else:
            stroma[i] = cc.EXP_NA
            follicle[i] = cc.EXP_NA
            print("no ens ID for target " + df[cc.GS_KEY][i])
    df[cc.RNA_EXP_KEY] = rna
    df[cc.STROMA] = stroma
    df[cc.FOLLICLE] = follicle
    return df

def date_csv_name(csv_name):
    """
    given the name for a csv file, inserts the date at the end

    Parameters
    ----------
    csv_name : str
        the name of a csv file

    Returns
    -------
     str
        the csv file with the date inserted

    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")

    if csv_name[-4:].lower() == ".csv":
        return csv_name[:-4] + "_" + date_str + ".csv"
    else:
        return csv_name + "_" + date_str + ".csv"
        
    

def write_target_csv(target_df, out_csv = "target_list.csv"):
    """
    Writes the dataframe of target dictionaries to a csv file with a 
    timestamped file name. By default the file is named 
    "target_list_[today's date+time].csv"
    
    The datetime in the filename should prevent overwriting of existing files
    
    Parameters
    ----------
    target_df
        The dataframe provided by compare targets
    out_csv : str
        The name of the csv file to output. Accepts strings with or without
        the .csv extension

    Returns
    -------
    None.

    """
    out_csv_name = date_csv_name(out_csv)
    target_df.to_csv(out_csv_name, encoding = "utf-8-sig", index = False)
            
    
def script_wrapper(out_csv, in_csv = cc.CSV_NAME):
    """
    Wrapper function that runs the script. Generates the target list and
    writes it to a csv file. 

    Returns
    -------
    None.

    """
    start = time.perf_counter() #timing
    
    target_df = compare_targets(in_csv)
    write_target_csv(target_df, out_csv)
    
    stop = time.perf_counter()
    print("time for full run on open targets csv:")
    print(stop - start)
    
def test_run():
    df = compare_targets(cc.TEST_CSV, cc.ENSID_KEY)
    return df
    
    
    
    
    
    