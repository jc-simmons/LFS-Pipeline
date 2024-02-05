import numpy as np
import pandas as pd
import pickle
import os


def main():

    os.chdir('data')

    raw_data = pd.read_csv('raw_lfs_data.csv.csv')

    # keep a copy of the numerical age labels before decoding 
    age_12_num = raw_data['AGE_12'].copy()


    # decode variables based on LFS_PUMF_EPA_FGMD_codebook 
    gen_code_dict()
    decoded_data = decode_lfs_labels(raw_data) 


    # keep 2 AGE_12 columns: numerical is useful for modelling, labelled categorical for easy analysis
    decoded_data = decoded_data.assign(AGE_12_NUM=age_12_num.values)
    decoded_data.rename(columns={'AGE_12': 'AGE_12_CAT'},inplace=True)


    cleaned_data = drop_data(decoded_data)

    decoded_data.to_csv('cleaned_lfs.csv',index=False)




def decode_lfs_labels(df):

    with open('lfs_code_dict.txt', 'rb') as handle:
        code_dict = pickle.loads(handle.read())


    for variable in df.columns:

        for variable_val in code_dict[variable]:

            if (type(variable_val)==int):

                df.loc[df[variable] == variable_val,variable] = code_dict[variable][variable_val]

        
    return df


def gen_code_dict():

    """
    parses the codebook to generate a decoding dictionary based on the variables, variable values, and variable labels.
    ex:
    variable = prov
    variable_val = 13
    variable_label = New Brunswick

    result is a dictionary of dictionaries:    { variable: {   {variable_val: variable_label} , .. } , .. } 
    """
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
        



def drop_data(input_data):

    """
    Drops data in dataframe unncessesary for plotting or modelling
     
    Removes rows with no reported income, income less than minimum wage 
    at time of writing, or with information indicating
    unemployment. 

    Removes unnecessary or redundant columns for hourly income analysis

    """

    df = input_data.copy()

    # drop entries containing no income data
    df = df.dropna(subset=['HRLYEARN'])

    # drop if not in active labour force
    df = df.drop(df[df.LFSSTAT != 'Employed, at work'].index)

    # rescale units
    df.HRLYEARN = df.HRLYEARN/100.0

    # drop invalid income
    min_wage = {
    'Alberta' : 15.00,
    'British Columbia': 16.75,
    'Manitoba': 15.30,
    'New Brunswick': 14.75,
    'Newfoundland and Labrador': 15.00,
    'Nova Scotia': 15.00,
    'Ontario': 16.55,
    'Prince Edward Island': 15.00,
    'Quebec': 15.25,
    'Saskatchewan': 14.00
    }


    wages = df[['PROV','HRLYEARN']].values.tolist()

    valid_wage = pd.Series([wage[1] > min_wage[wage[0]] for wage in wages])

    df = df[valid_wage.values]

    # columns associated with unemployment
    unemployed_cols= ['DURUNEMP','FLOWUNEM','UNEMFTPT',
                    'WHYLEFTO','WHYLEFTN','DURJLESS',
                    'AVAILABL','LKEMPLOY','LKRELS',
                    'LKATADS','LKANSADS','LKOTHERN',
                    'PRIORACT','YNOLOOK','TLOLOOK',
                    'LKPUBAG','EVERWORK','PREVTEN','FTPTLAST']
    
    # drop any rows with having unemploymnent indicators
    df = df.drop(df.dropna(subset=unemployed_cols).index)

   # drop the respective unemployment columns
    df = df.drop('LFSSTAT', axis=1)
    df = df.drop(unemployed_cols,axis=1)
    
    
    # drop unnecessary or redundant columns
    unnecessary_cols = ['REC_NUM','SURVYEAR','SURVMNTH',
                    'AGE_6','FINALWT']

    df = df.drop(unnecessary_cols,axis=1)


    return df



# run script
if __name__ == "__main__":
    
    main()





