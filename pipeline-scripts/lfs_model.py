import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge, Lasso, HuberRegressor,  QuantileRegressor
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score
from matplotlib import pyplot as plt
from random import seed, random
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import QuantileTransformer
import json
import os


def main():

    os.chdir('../logs')
    
    df = pd.read_csv('cleaned_lfs.csv')

    os.chdir('../logs')

    # features of interest for modelling
    features=['AGE_12_NUM','FTPTMAIN','SEX','EDUC',
                'NOC_43','NAICS_21','HRLYEARN','TENURE',
                'UHRSMAIN','PROV']
    
    df=df[features]

    numeric_features = ['TENURE','UHRSMAIN','AGE_12_NUM']
    cat_features = list(set(df.columns)-set(numeric_features))
    cat_features.remove('HRLYEARN')


    df = encode_onehot(df,cat_features)

    X=df.drop('HRLYEARN', axis=1)
    y=df[['HRLYEARN']] 


    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

    reg = train_model(X_train,y_train)


   # log metrics
    y_predict = reg.predict(X_test)
    y_test=y_test

    MAE = np.mean(np.absolute(y_predict - y_test.to_numpy().ravel()))
    RMSE = np.sqrt(((y_predict - y_test.to_numpy().ravel()) ** 2).mean())
    R2 =  r2_score( y_test.to_numpy().ravel(),y_predict) 

    metrics = [MAE,RMSE,R2]

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

    feat_importance = reg.feature_importances_.tolist()
    labels = np.array(X.columns).tolist()

    importances = aggregate_importance(feat_importance,labels,cat_features)

  
    imp_df = pd.DataFrame(importances)

    imp_df.to_csv("importances.txt",index=False,header=None,sep=' ')

    return



def normalize_data(df,numeric_features):

    scaler = MinMaxScaler()
    df[numeric_features] = scaler.fit_transform(df[numeric_features])

    return df



def encode_onehot(df,numeric_features):
     
    df = pd.get_dummies(df,columns=cat_features)       

    return df


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


def train_model(X_train, y_train):

        model  = GradientBoostingRegressor(loss='absolute_error', n_estimators=100,
                                            max_depth=10).fit(X_train, y_train.to_numpy().ravel())

        return model 

# run script
if __name__ == "__main__":
    
    main()
