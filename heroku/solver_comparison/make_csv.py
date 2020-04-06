import warnings
import scipy.io as sc
import pandas as pd
import numpy as np

filename=r'RandInitResults_solvers_AnalysisOnly.mat'
filename2=r'RandInitResults_solvers_AnalysisOnly_mainConly.mat'
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    data = sc.loadmat(filename)
    data2 = sc.loadmat(filename2)

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
df_2=pd.DataFrame()
for kkk in range(len(solvers)):
    for kk in range(len(a)):
        aa1 = a[kk][:-2]
        aa2 = a[kk][-2:]
        for k in range(len(b)):
            for j in [0]:
                f = {d[i]: data2[solvers[kkk]][a[kk]][0][0][b[k]][0][0][c[j]][0][0]['analysis'][0][0][d[i]][0][0][0] for i in range(len(d)-1)}
                df_2=df_2.append(pd.DataFrame(f, index=pd.MultiIndex.from_tuples([(solvers[kkk],aa1,aa2,b[k],'set{:03d}'.format(int(c[j][3:])), i) for i in range(16)])))

d=list(data[solvers[1]][a[0]][0][0][b[0]][0][0][c[0]][0][0]['analysis'][0][0].dtype.fields.keys())
df_gurobifail = pd.DataFrame()
for kkk in [1]:
    for kk in range(len(a)):
        aa1 = a[kk][:-2]
        aa2 = a[kk][-2:]
        for k in range(len(b)):
            for j in range(len(c)):
                f = {'gurobifail': [data[solvers[1]][a[kk]][0][0][b[k]][0][0][c[j]][0][0]['analysis'][0][0]['gurobifail'][0][0][0][i].shape[0]>0 for i in range(16)]}
                df_gurobifail = df_gurobifail.append(pd.DataFrame(f, index=pd.MultiIndex.from_tuples(
                    [(solvers[kkk], aa1, aa2, b[k], 'set{:03d}'.format(int(c[j][3:])), i) for i in range(16)])))

df['gurobifail']=False
df.loc[df_gurobifail.index,df_gurobifail.columns]=df_gurobifail
df_gurobifail_2 = pd.DataFrame()
for kkk in [1]:
    for kk in range(len(a)):
        aa1 = a[kk][:-2]
        aa2 = a[kk][-2:]
        for k in range(len(b)):
            for j in [0]:
                f = {'gurobifail': [data[solvers[1]][a[kk]][0][0][b[k]][0][0][c[j]][0][0]['analysis'][0][0]['gurobifail'][0][0][0][i].shape[0]>0 for i in range(16)]}
                df_gurobifail_2 = df_gurobifail_2.append(pd.DataFrame(f, index=pd.MultiIndex.from_tuples(
                    [(solvers[kkk], aa1, aa2, b[k], 'set{:03d}'.format(int(c[j][3:])), i) for i in range(16)])))

df_2['gurobifail']=False
df_2.loc[df_gurobifail_2.index,df_gurobifail_2.columns]=df_gurobifail_2

df.to_csv('data.csv')
df_2.to_csv('data_initial.csv')


dfs=[df,df_2]
dfs_suffix=['','_initial']
for iii in range(2):
    data=dfs[iii]
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
    df2.to_csv('data2' + dfs_suffix[iii] + '.csv')
    df3.to_csv('data3' + dfs_suffix[iii] + '.csv')
