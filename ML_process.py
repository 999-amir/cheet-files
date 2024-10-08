# ========================================================================================================================== check dataset
# ------------------------------------------------------------------------------------------ auto check
ProfileReport(df)

# ------------------------------------------------------------------------------------------ manual check
print('='*55, '[check] data & type')
print(df.info())

print('='*55, ['check null data'])
print(df.isna().sum())

print('='*55, 'number of unique values in each column')
print(df.nunique())

print('='*55, '[check] imbalenced data')
for i in df.columns:
    print('-'*45, i)
    print(df[i].value_counts())

print('='*55, '[check] scaling')
print(df.describe())


# ========================================================================================================================== clean data
# ------------------------------------------------------------------------------------------ remove charecter
pd.to_numeric(df['YearsCode'], errors='raise')
df.replace({'YearsCode': {
    'More than 50 years': 50,
    'Less than 1 year': 0.5
}}, inplace=True)
df['Area'] = df['Area'].apply(lambda x: re.sub(',', '', x))

# ------------------------------------------------------------------------------------------ seperate multi values and encode it
def values_seperator_encoder(data, feature, keyword):
    column = data[feature]
    seperator_dict = {}
    zeros_list = np.zeros(shape=(1, len(column)))[0]
    for k in keyword:
        seperator_dict[f'[{feature}]-{k}'] = zeros_list
    seperator_df = pd.DataFrame(seperator_dict)
    for i in tqdm(range(len(column))):
        li = []
        for k in keyword:
            try:
                if k in column[i]:
                    seperator_df[f'[{feature}]-{k}'][i] = 1
            except:
                pass
    return seperator_df
# how to use it
keyword = ['React.js', 'Node.js', 'jQuery', 'Flask', 'Django', 'Angular', 'ASP.NET Core', 'ASP.NET',
          'Express', 'Laravel', 'FastAPI']
df = pd.concat([df, values_seperator_encoder(df, 'Webframework', keyword)], axis=1)
df.drop('Webframework', axis=1, inplace=True)

# ------------------------------------------------------------------------------------------ categorical to numerical
dfp = df.merge(pd.get_dummies(dfp['Address']), left_index = True, right_index = True)
dfp.drop(columns = 'Address', inplace = True)

# ------------------------------------------------------------------------------------------ values repeated over 85%
imbalence_limit = 0.85
print('befor:', len(X.columns))
for c in X.columns:
    vc = pd.DataFrame(X[c].value_counts())
    if (vc.iloc[0]>len(X)*imbalence_limit)[0]:
        X.drop(c, axis=1, inplace=True)
print('after:', len(X.columns))

# ------------------------------------------------------------------------------------------ fill NaN
si = SimpleImputer(missing_values=np.NaN, strategy='median') # check later
df = pd.DataFrame(si.fit_transform(df), columns=df.columns)
df.isna().sum()

# ------------------------------------------------------------------------------------------ outliers
# detect outliers
for c in ['YearsCode', 'YearsCodePro', 'Salary']:
    p = ex.box(x=c, data_frame=df1)
    p.update_layout(height=200, width=800, title_text=c)
    p.show()
# remove outliers -> quantile (boxplot)
for c in ['YearsCode', 'YearsCodePro', 'Salary']:
    Q1 = df[c].quantile(0.25)
    Q3 = df[c].quantile(0.75)
    IQR = Q3 - Q1
    upper_limit = Q1 + 1.5*IQR
    lower_limit = Q1 - 1.5*IQR
    df1 = df1[
        (df1[c]>lower_limit) & (df1[c]<upper_limit)
    ]
    p = ex.box(x=c, data_frame=df1)
    p.update_layout(height=200, width=800, title_text=c)
    p.show()


# ========================================================================================================================== check models
setup(df, target='FLAG', session_id=42, use_gpu=True)
compare_models()


# ========================================================================================================================== EDA


# ========================================================================================================================== visualization
# ------------------------------------------------------------------------------------------ distribution on categorical data
matplotlib.rcParams.update({'font.size': 8})
fig, ax = plt.subplots(ncols=4, nrows=13, figsize=(15,35))
colors = ['#F4B942', '#EE2E31']
columns = df1.drop(['YearsCode', 'YearsCodePro', 'Salary'], axis=1).columns
j, k = 0, 0
for i in tqdm(range(len(columns))):
    if k >= 4:
        k -= 4
        j += 1
    data = df1[columns[i]].value_counts()
    ax[j, k].pie(data, labels=data.values, shadow=True, colors=colors)
    ax[j, k].legend(labels=data.index, fontsize='small')
    ax[j, k].set_title(columns[i])
    k += 1

# ------------------------------------------------------------------------------------------ distribution on numerical data
def plot_bar_chart(df, column):
    p = ex.bar(x = df[column].value_counts().keys(), y = df[column].value_counts(),
               color=df[column].value_counts().keys())
    p.update_layout(height = 300, width = 600, title_text = column)
    p.update(layout_coloraxis_showscale=False)
    p.show()

for c in ['YearsCode', 'YearsCodePro', 'Salary']:
    plot_bar_chart(df1, 'YearsCode')

# ------------------------------------------------------------------------------------------ relation plot -> search in django and machine learning
sns.set_theme(style='darkgrid')
sns.relplot(x='YearsCodePro', y='Salary', data=df1, hue='[Employment]-full-time',
            style='[Employment]-freelancer', col='[Webframework]-Django',
            row='[DevType]-machine learning', s=15).figure.set_size_inches(18.5, 10.5)

# ------------------------------------------------------------------------------------------ violin
sns.catplot(x='Churn', y='MonthlyCharges', data=df, kind='violin').figure.set_size_inches(3.5, 3.5)


# ========================================================================================================================== feature importance
# ------------------------------------------------------------------------------------------ correlation
p = ex.imshow(df.corr(), x = df.columns, y = df.columns, color_continuous_scale = 'rainbow')
p.update_layout(height = 900, width = 900, title_text = 'correlation')
p.update(layout_coloraxis_showscale=False)
p.show()
# color_continuous_scale items
# fig = ex.colors.sequential.swatches_continuous() 
# fig.show()

# ------------------------------------------------------------------------------------------ shap
pycaret_xgb = create_model('xgboost')
interpret_model(pycaret_xgb)
plot_model(estimator=pycaret_xgb, plot='feature')


# ========================================================================================================================== train & test
X = df.drop('FLAG', axis=1)
Y = df['FLAG']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=42, test_size=0.3, stratify=Y)


# ========================================================================================================================== preprocessing
# ------------------------------------------------------------------------------------------ over sampling (SMOTE)
smote = SMOTE(random_state=42)
X_train, Y_train = smote.fit_resample(X_train, Y_train)

# ------------------------------------------------------------------------------------------ scaling
sc = StandardScaler()
X_train = pd.DataFrame(sc.fit_transform(X_train), columns=X.columns)
X_test = pd.DataFrame(sc.fit_transform(X_test), columns=X.columns)


# ========================================================================================================================== hyper parameters
# ------------------------------------------------------------------------------------------ regression
def parameter_finder (model, parameters={}):
    grid = GridSearchCV(model, 
                        param_grid = parameters, 
                        refit = True, 
                        cv = KFold(shuffle = True, random_state = 1), 
                        n_jobs = -1)
    grid_fit = grid.fit(X_train, Y_train)
    Y_train_pred = grid_fit.predict(X_train)
    Y_pred = grid_fit.predict(X_test)
    train_score =r2_score(Y_train_pred, Y_train)
    test_score = r2_score(Y_pred, Y_test)
    RMSE = np.sqrt(mean_squared_error(Y_test, Y_pred))
    model_name = str(model).split('(')[0]
    print('='*45, model_name)
    print(f'best param: {grid_fit.best_params_}')
    print(f'R2 score (train): {train_score}')
    print(f'R2 score (test): {test_score}')
    print(f'RSME score: {RMSE:,}')

# ------------------------------------------------------------------------------------------ classification
def parameter_finder (model, parameters={}):
    X_train, X_test = X_train1, X_test1
    grid = GridSearchCV(model, 
                        param_grid = parameters, 
                        refit = True, 
                        cv = KFold(shuffle = True, random_state = 1), 
                        n_jobs = -1)
    grid_fit = grid.fit(X_train, Y_train)
    Y_train_pred = grid_fit.predict(X_train)
    Y_pred = grid_fit.predict(X_test)
    print('='*55, str(model).split('(')[0])
    print(f'best param: {grid_fit.best_params_}')
    print('-'*55, 'train report')
    print(classification_report(Y_train, Y_train_pred))
    print('-'*55, 'test report')
    print(classification_report(Y_test, Y_pred))
    print('*'*55, 'recall score')
    print('train:', np.round(recall_score(Y_train, Y_train_pred)*100, 2), '%')
    print('test:', np.round(recall_score(Y_test, Y_pred)*100, 2), '%')

# use function
xgbc = XGBClassifier()
params = {
      'learning_rate':[0.5],
      'n_estimators':[100],
      'subsample':[0.004],
       'max_depth':[3],
       'colsample_bytree':[0.7]
}
parameter_finder(xgbc, params)


# ========================================================================================================================== ML
xgbc = XGBClassifier(colsample_bytree= 0.7, learning_rate= 0.5, max_depth= 3, n_estimators= 100,
                     subsample= 0.004)
xgbc.fit(X_train, Y_train)


# ========================================================================================================================== metrics
# ------------------------------------------------------------------------------------------ regression
# error
def metrics_score_ml(Y, Y_pred):
    return [
            mean_absolute_error(Y, Y_pred),
            mean_squared_error(Y, Y_pred),
            np.sqrt(mean_squared_error(Y, Y_pred)),
            r2_score(Y, Y_pred)
           ]
data = [
    metrics_score_ml(Y_train, gbr.predict(X_train)),
    metrics_score_ml(Y_test, gbr.predict(X_test))
]
pd.DataFrame(data, columns=['MAE', 'MSE', 'RMSE', 'r2'], index=['train', 'test'])

# error plot
plt.scatter(Y_test, gbr.predict(X_test), c='red', s=10)
plt.plot(Y_test, Y_test, c='black')
plt.show()

# ------------------------------------------------------------------------------------------ classification
# ROC
fig, ax = plt.subplots()
RocCurveDisplay.from_estimator(xgbc, X_test, Y_test, ax=ax)
plt.show()
# ERROR
Y_pred = xgbc.predict(X_test)
Y_train_pred = xgbc.predict(X_train)

print('-'*55, 'train report')
print(classification_report(Y_train, Y_train_pred))
print('-'*55, 'test report')
print(classification_report(Y_test, Y_pred))

print('train:', np.round(recall_score(Y_train, Y_train_pred)*100, 2), '%')
print('test:', np.round(recall_score(Y_test, Y_pred)*100, 2), '%')

sns.heatmap(confusion_matrix(Y_test, Y_pred), square=True, fmt='.1f', annot=True, annot_kws={'size': 10}, cmap='viridis', cbar=False)
plt.title('confusion matrix heatmap')
plt.show()


# ========================================================================================================================== save model
joblib.dump(xgbc, 'churn_xgbc.joblib')

