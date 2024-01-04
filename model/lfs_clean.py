import numpy as np
import pandas as pd
import pickle
import os


def main():

    os.chdir('data')

    raw_data = pd.read_csv('data_current.csv')

    cleaned_data = drop_data(raw_data)

    # keep a copy of the numerical age labels before decoding 
    age_12_num = cleaned_data['AGE_12'].copy()

    gen_code_dict()

    # decode variables based on LFS_PUMF_EPA_FGMD_codebook 
    decoded_data = decode_lfs_labels(cleaned_data) 

    # keep 2 AGE_12 columns: numerical is useful for modelling, labelled categorical for easy analysis
    decoded_data = decoded_data.assign(AGE_12_NUM=age_12_num.values)
    decoded_data.rename(columns={'AGE_12': 'AGE_12_CAT'},inplace=True)


    decoded_data.to_csv('cleaned_lfs.csv',index=False)



def gen_code_dict():



    code_list=pd.read_csv('LFS_PUMF_EPA_FGMD_codebook.csv', encoding = 'latin1').to_numpy()

    code_dict = {}

    for i in range(len(code_list)) :

        field_num = code_list[i][0]

        if (not(np.isnan(field_num))): 

            variable = code_list[i][3].upper().strip()

            code_dict[variable] = {}

        elif (np.isnan(field_num)):

            try: 
                variable_val = int(code_list[i][3])
            except:
                variable_val = code_list[i][3]

            label = code_list[i][4]
            code_dict[variable][variable_val] = label


    with open('lfs_code_dict.txt','wb') as handle:
        pickle.dump(code_dict,handle)
        

def drop_data(df):

    """
    Drops data in dataframe unncessesary for plotting or modelling
     
    Removes rows with no reported income, income less than minimum wage 
    (set to $14.00 for all provinces), or with information indicating
    unemployment. 

    Removes unnecessary or redundant columns
    """

    # drop no income
    df =df.dropna(subset=['HRLYEARN'])

    # drop invalid income
    df=df.drop(df[df.HRLYEARN < 1400].index)

    # drop if not in active labour force
    df=df.drop(df[df.LFSSTAT != 1].index)

    # columns associated with unemployment
    unemployed_cols= ['DURUNEMP','FLOWUNEM','UNEMFTPT',
                      'WHYLEFTO','WHYLEFTN','DURJLESS',
                      'AVAILABL','LKEMPLOY','LKRELS',
                      'LKATADS','LKANSADS','LKOTHERN',
                      'PRIORACT','YNOLOOK','TLOLOOK',
                      'LKPUBAG']
    
    # drop any rows with having unemploymnent indicators
    df = df.drop(df.dropna(subset=unemployed_cols).index)

    # drop respective unemployment columns
    df = df.drop(unemployed_cols,axis=1)
    
    
    # drop unnecessary or redundant columns
    unnecessary_cols = ['REC_NUM','SURVYEAR','SURVMNTH',
                        'AGE_6','EVERWORK','PREVTEN',
                        'FTPTLAST','EFAMTYPE', 'AGYOWNK',
                        'IMMIG','FINALWT']

    df = df.drop(unnecessary_cols,axis=1)


    return df

def decode_lfs_labels(df):

    with open('lfs_code_dict.txt', 'rb') as handle:
        code_dict = pickle.loads(handle.read())


    for variable in df.columns:

        for variable_val in code_dict[variable]:

            if (type(variable_val)==int):

                df.loc[df[variable] == variable_val,variable] = code_dict[variable][variable_val]

        
    return df




# run script
if __name__ == "__main__":
    
    main()





