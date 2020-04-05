import warnings
import scipy.io as sc
import pandas as pd
import numpy as np

filename=r'RandInitResults_solvers_AnalysisOnly.mat'
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    data = sc.loadmat(filename)

solvers=['LBFGSB','SCP']
a=list(data[solvers[0]].dtype.fields.keys())
b=list(data[solvers[0]][a[0]][0][0].dtype.fields.keys())
c=list(data[solvers[0]][a[0]][0][0][b[0]][0][0].dtype.fields.keys())
d=list(data[solvers[0]][a[0]][0][0][b[0]][0][0][c[0]][0][0]['analysis'][0][0].dtype.fields.keys())
dd=data[solvers[0]][a[0]][0][0][b[0]][0][0]
e=data[solvers[0]][a[0]][0][0][b[0]][0][0][c[0]][0][0]['analysis'][0][0][d[0]][0][0][0]
ee=data[solvers[0]][a[0]][0][0][b[0]][0][0][c[0]][0][0]['analysis'][0][0]

# f={d[i]: ee[d[i]][0][0][0] for i in range(len(d)-1)}
# ff=[{d[i]: dd[c[j]][0][0]['analysis'][0][0][d[i]][0][0][0] for i in range(len(d)-1)} for j in ]

df=pd.DataFrame()
for kkk in range(len(solvers)):
    for kk in range(len(a)):
        aa1 = a[kk][:-2]
        aa2 = a[kk][-2:]
        for k in range(len(b)):
            for j in range(len(c)):
                f = {d[i]: data[solvers[kkk]][a[kk]][0][0][b[k]][0][0][c[j]][0][0]['analysis'][0][0][d[i]][0][0][0] for i in range(len(d)-1)}
                df=df.append(pd.DataFrame(f, index=pd.MultiIndex.from_tuples([(solvers[kkk],aa1,aa2,b[k],'set{:03d}'.format(int(c[j][3:])), i) for i in range(16)])))
    # if kkk==1:
    #     df=df[df.columns.drop('gurobifail')]

df.to_csv('data.csv')

data=df
ex=list(zip(*list(zip(*data.index))[:-1]))[::16]
cols=data.columns
df2=pd.DataFrame()
df3=pd.DataFrame()
for i in range(len(ex)):
    temp=np.argmin(data.loc[ex[i],'err_val'])
    df2=df2.append(data.loc[tuple(list(ex[i])+[temp])])
    df3=df3.append(data.loc[tuple(list(ex[i])+[0])])
df2.index=pd.MultiIndex.from_tuples(df2.index).droplevel(-1)
df3.index=pd.MultiIndex.from_tuples(df3.index).droplevel(-1)
df2=df2.T.stack()
df3=df3.T.stack()
df2=pd.DataFrame(np.sort(df2.loc['err_val'].values,axis=0),columns=df2.columns)
df3=pd.DataFrame(np.sort(df3.loc['err_val'].values,axis=0),columns=df3.columns)
df2.to_csv('data2.csv')
df3.to_csv('data3.csv')
