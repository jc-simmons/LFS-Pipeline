import numpy as np
import pandas as pd
import json
import os
import pathlib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.ensemble import  GradientBoostingRegressor
from sklearn.metrics import r2_score
from matplotlib import pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer




def main():

    cwd = os.getcwd()
    print(cwd)

    data_path = pathlib.Path('data/cleaned_lfs.csv')
    df = pd.read_csv(data_path)

    # features of interest for modelling
    features=['AGE_12_NUM','FTPTMAIN','SEX','EDUC',
                'NOC_43','NAICS_21','HRLYEARN','TENURE',
                'UHRSMAIN','PROV']
    
    df=df[features]

    numeric_features = ['TENURE','UHRSMAIN','AGE_12_NUM']
    cat_features = list(set(df.columns)-set(numeric_features))
    cat_features.remove('HRLYEARN')

    X=df.drop('HRLYEARN', axis=1)
    y=df[['HRLYEARN']] 

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
    

    ct = ColumnTransformer([
        ("numeric", MinMaxScaler(), numeric_features),
        ("categorial", OneHotEncoder(), cat_features)
    ])

    pipe = Pipeline([
        ('preprocess', ct),
        ('model', GradientBoostingRegressor(loss='absolute_error', n_estimators=100, max_depth=10))
        ])

    reg = pipe.fit(X_train, y_train.to_numpy().ravel())

   # log metrics
    y_predict = reg.predict(X_test)
    y_test=y_test

    MAE = np.mean(np.absolute(y_predict - y_test.to_numpy().ravel()))
    RMSE = np.sqrt(((y_predict - y_test.to_numpy().ravel()) ** 2).mean())
    R2 =  r2_score( y_test.to_numpy().ravel(),y_predict) 

    metrics = [MAE,RMSE,R2]


    os.chdir('logs')
    with open("metrics.json",'w') as outfile:
        json.dump(metrics,outfile)


    # log artifacts: residuals & feature importance plots
    fig ,ax =plt.subplots()

    ax.scatter(y_predict,y_predict-y_test.to_numpy().ravel() ,s=2,color='black' )

    ax.set_ylabel('|$y_{predicted}-y_{actual}$')
    ax.set_xlabel('$y_{predicted}$')
    ax.set_title('Residuals')


    plt.tight_layout()
    plt.savefig("residuals.png")

    plt.clf()

    feat_importance = reg.steps[1][1].feature_importances_.tolist()
    labels = np.array(X.columns).tolist()

    importances = aggregate_importance(feat_importance,labels,cat_features)

  
    imp_df = pd.DataFrame(importances)

    imp_df.to_csv("importances.txt",index=False,header=None,sep=' ')

    return



def aggregate_importance(feature_importance,labels,cat_features):
     
    cat_importance_agg = [0]*len(cat_features)

    for category in cat_features:
          
        for sub_category in labels:
               
            if category in sub_category:
                    
                cat_importance_agg[cat_features.index(category)] = cat_importance_agg[cat_features.index(category)] + feature_importance[labels.index(sub_category)]



    feature = labels + cat_features
    importance = feature_importance + cat_importance_agg

    final = list(zip(feature,importance))

    final_importances = sorted(final,key=lambda x:x[1],reverse=True)


       
    return final_importances


# run script
if __name__ == "__main__":
    
    main()
