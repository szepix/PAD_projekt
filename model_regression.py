import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd

data = pd.read_csv('job_offers_cleaned.csv')
categorical_features = ['offer_name', 'company', 'work_modes', "office", "technologies", "seniority", "contract_type"]

categorical_transformer = OneHotEncoder(handle_unknown='ignore')

regressor = GradientBoostingRegressor(random_state=42, learning_rate=0.4, max_depth=4,min_samples_leaf=1, min_samples_split=6, n_estimators=411, criterion="squared_error")

clf = Pipeline(steps=[('preprocessor', categorical_transformer),
                      ('regressor', regressor)])

X = data.drop(['average_salary'], axis=1)
y = data['average_salary']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r_squared = r2_score(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")
print(f"Mean Squared Error: {mse}")
print(f"Root Mean Squared Error: {rmse}")
print(f"R-squared: {r_squared}")

mae_scores = cross_val_score(clf, X, y, cv=10, scoring='neg_mean_absolute_error')
mae_scores = -mae_scores
print(f"Kfold - Average MAE score: {np.mean(mae_scores)}")

mse_scores = cross_val_score(clf, X, y, cv=10, scoring='neg_mean_squared_error')
mse_scores = -mse_scores
print(f"Kfold - Average MSE score: {np.mean(mse_scores)}")

rmse_scores = np.sqrt(mse_scores)
print(f"Kfold - Average RMSE score: {np.mean(rmse_scores)}")

r2_scores = cross_val_score(clf, X, y, cv=10, scoring='r2')
print(f"Kfold - Average R-squared score: {np.mean(r2_scores)}")

import pickle
pickle.dump(clf, open('model.pkl', 'wb'))