import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, RocCurveDisplay, roc_auc_score,
                             recall_score, precision_score, f1_score)
from sklearn.feature_selection import VarianceThreshold, RFE
from imblearn.over_sampling import SMOTENC
from imblearn.under_sampling import RandomUnderSampler
import pickle


def evaluate_model(name, model, X_test, y_test):
    ''' Calculate metrics, confusion matrix and record results.'''
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:,1]

    results = {
        "Model": name,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1": f1_score(y_test, y_pred),
        "ROC_AUC": roc_auc_score(y_test, y_proba),
    }
    print(f"\n{name} - Confusion matrix [Stayed, Churned]:")
    print(confusion_matrix(y_test, y_pred, labels=[0,1]))
    return results


'''STEP 1: Read CSV'''
data_file = "data/Telco-Customer-Churn.csv"
df = pd.read_csv(data_file)
# print(df.head())

'''STEP 2: Dataset Validation: Check for missing values and column types'''
# print(df.info())
# print(f"Missing values: {df.isna().sum()}")

# Check if TotalCharges has non-numeric entries
total_charges_numeric = pd.to_numeric(df["TotalCharges"], errors='coerce')
# print(total_charges_numeric)

# Entries with missing or non-numeric values for TotalCharges
#  print(df.loc[
#     total_charges_numeric.isna(), ['customerID', 'tenure','TotalCharges']
#       ])

'''STEP 3: Data Cleaning'''
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors='coerce')
# print("Missing TotalCharges", df["TotalCharges"].isna().sum())
# print("Duplicate rows", df.duplicated().sum())
# print("Duplicate customer ids", df["customerID"].duplicated().sum())

# Exclude identifier and outcome -> INPUT
X = df.drop(columns=["customerID", "Churn"])
# Outcome only -> OUTPUT
Y = df["Churn"].map({"Yes": 1, "No": 0})
# print(f"Input Shape: {X.shape}")
# print(f"Output counts: {Y.value_counts()}")
# print(f"Missing counts: {Y.isna().sum()}")

''' STEP 4: DATA SPLIT - TRAIN, TEST'''
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)
# print("Training inputs:", X_train.shape)
# print("Test inputs:", X_test.shape)
# print("Training churn proportions:")
# print(y_train.value_counts(normalize=True))

''' STEP 5: TACKLE MISSING DATA'''
charges_median = X_train["TotalCharges"].median()
X_train["TotalCharges"] = X_train["TotalCharges"].fillna(charges_median)
X_test["TotalCharges"] = X_test["TotalCharges"].fillna(charges_median)

print("Training TotalCharges w/ missing values:", X_train["TotalCharges"].isnull().sum())
print("Testing TotalCharges w/ missing values:", X_test["TotalCharges"].isnull().sum())

''' STEP 6: ONE HOT ENCODING'''
categorical_columns = X_train.select_dtypes(include=["object", "string", "category"]).columns
encoder = OneHotEncoder(
    drop="first",
    handle_unknown="ignore",
    sparse_output=False
)
train_categories = encoder.fit_transform(X_train[categorical_columns])
test_categories = encoder.transform(X_test[categorical_columns])

''' STEP 7: CONCATENATION OF ONE HOT ENCODING W/ NUMERIC'''
numerical_columns = X_train.columns.difference(categorical_columns)
categorical_columns = encoder.get_feature_names_out(categorical_columns)

X_train_encoded = pd.concat(
    [
    X_train[numerical_columns],
    pd.DataFrame(train_categories, columns=categorical_columns, index=X_train.index)
        ],
    axis=1
)

X_test_encoded = pd.concat(
    [
    X_test[numerical_columns],
    pd.DataFrame(test_categories, columns= categorical_columns, index=X_test.index)
        ],
    axis=1
)
print(X_train_encoded.head())
print(f"Training shape: {X_train_encoded.shape}")
print(f"Testing shape: {X_test_encoded.shape}")

''' STEP 8: SCALING NUMERIC FEATURES'''
scaler = StandardScaler()
X_train_encoded[numerical_columns] = scaler.fit_transform(X_train_encoded[numerical_columns])
X_test_encoded[numerical_columns] = scaler.transform(X_test_encoded[numerical_columns])
print(X_train_encoded.head())

''' STEP 9: FEATURE VISUALIZATION'''
fig, ax = plt.subplots(figsize=(8,5))
for outcome, label in [(0, "Stayed"), (1, "Churn")]:
    customers = X_train.loc[y_train==outcome]
    ax.scatter(
        customers["tenure"],
        customers["MonthlyCharges"],
        label=label,
        alpha=0.3,
        s=15
    )
ax.set_xlabel("Tenure (months)")
ax.set_ylabel("Monthly charges")
ax.set_title("Training Customers: Tenure, Charges and Churn")
ax.legend()
fig.tight_layout()
fig.savefig( "results/tenure_charges_churn.png", dpi=300)
# plt.show()

''' STEP 10: LOGISTIC REGRESSION MODEL BUILDING'''
baseline_model = LogisticRegression(max_iter=1000)
baseline_model.fit(X_train_encoded, y_train)
print("Baseline model trained.")

''' STEP 11: BASELINE MODEL VALIDATION'''
# y_pred = baseline_model.predict(X_test_encoded)
# y_proba = baseline_model.predict_proba(X_test_encoded)[:, 1]
#
# print(f"Accuracy: {round(accuracy_score(y_test, y_pred), 2)}")
# print(f"Precision: {round(precision_score(y_test, y_pred), 2)}")
# print(f"Recall: {round(recall_score(y_test, y_pred), 2)}")
# print(f"F1 Score: {round(f1_score(y_test, y_pred), 2)}")
# print(f"ROC-AUC: {round(roc_auc_score(y_test, y_proba), 2)}")
#
# print("\nConfusion Matrix [Stayed, Churned]:")
# print(confusion_matrix(y_test, y_pred, labels=[0, 1]))



# RocCurveDisplay.from_predictions(y_test, y_proba)
# plt.title("Baseline Logistic Regression: ROC Curve")
# plt.tight_layout()
# plt.savefig("results/baseline_roc_curve.png", dpi=300)
# plt.show()
evaluation_results = []
evaluation_results.append(evaluate_model("Baseline", baseline_model, X_test_encoded, y_test))

''' STEP 12: FEATURE SELECTION
1. Barrier Threshold (Variance) - Remove Features with Zero Variance i.e. don't change
2. Recursive Feature Elimination (RFE) - Repeatedly fit the model, remove feature with smallest absolute 
                                         coefficient until a set number of features with coefficients remain.
'''

# 1. Barrier Threshold (Variance) : Remove which features have nonzero variance in training data
selector = VarianceThreshold(threshold=0.0)
selector.fit(X_train_encoded)

selected_columns = X_train_encoded.columns[selector.get_support()]
X_train_selected = X_train_encoded[selected_columns]
X_test_selected = X_test_encoded[selected_columns]

print("Features before:", X_train_encoded.shape[1])
print("Features after:", X_train_selected.shape[1])
print("Removed:", X_train_selected.columns.difference(selected_columns).tolist())

# 2. Recursive Fit Elimination (RFE)
rfe = RFE(
    estimator=LogisticRegression(max_iter=1000),
    n_features_to_select=15,
    step=1,
)

rfe.fit(X_train_selected, y_train)
rfe_columns = X_train_selected.columns[rfe.support_]

X_train_rfe = X_train_selected[rfe_columns]
X_test_rfe = X_test_selected[rfe_columns]

print("Selected features:")
print(rfe_columns.tolist())

evaluation_results.append(evaluate_model("RFE", rfe, X_test_selected, y_test))

''' STEP 13: HANDLING UNBALANCED DATA
1. Balanced Class Weights: Automatically give minority class more weight in training loss.
2. Custom Class Weights: Custom weights  (E.g: Give each churner twice the weight of each customer that stayed.
3. Random Undersampling: Randomly reduce majority class in training set to match minority class, rather than changing class weights.
4. Synthetic Minority Over-sampling Technique for Nominal and Continuous (SMOTENC) 
'''

# 1. Balanced Class Weights
balanced_model = LogisticRegression(max_iter=1000, class_weight="balanced")
balanced_model.fit(X_train_encoded, y_train)

evaluation_results.append(evaluate_model("Balanced weights", balanced_model, X_test_encoded, y_test))

# 2. Custom Class Weights
custom_model = LogisticRegression(max_iter=1000, class_weight={0: 1, 1:2})
custom_model.fit(X_train_encoded, y_train)
y_pred_custom = custom_model.predict(X_test_encoded)
y_proba_custom = custom_model.predict_proba(X_test_encoded)[:, 1]

evaluation_results.append(evaluate_model("Custom Weights", custom_model, X_test_encoded, y_test))

# 3. Random Undersampling: Randomly reduce the majority class to match the minority class
undersampler = RandomUnderSampler(random_state=42)
X_train_under, y_train_under = undersampler.fit_resample(X_train_encoded, y_train)

print(f"Before sampling: {y_train.value_counts()}")
print(f"After sampling: {y_train_under.value_counts()}")

under_model = LogisticRegression(max_iter=1000)
under_model.fit(X_train_under, y_train_under)

evaluation_results.append(evaluate_model("Undersampling", under_model, X_test_encoded, y_test))

# SMOTENC : Synthetically Minority Over-Sampling Technique for Nominal and Continuous
X_for_sampling = X_train.copy()
X_for_sampling[numerical_columns] = scaler.transform(
    X_train[numerical_columns]
)

sampling_categories = X_for_sampling.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

# Include this numeric-coded category
if "SeniorCitizen" in X_for_sampling.columns:
    if "SeniorCitizen" not in sampling_categories:
        sampling_categories.append("SeniorCitizen")

smotenc = SMOTENC(
    categorical_features=sampling_categories,
    random_state=42
)

X_train_synthetic, y_train_synthetic = smotenc.fit_resample(
    X_for_sampling, y_train
)

print("Before:")
print(y_train.value_counts())

print("After:")
print(y_train_synthetic.value_counts())

encoder_columns = encoder.feature_names_in_

synthetic_categories = pd.DataFrame(
    encoder.transform(X_train_synthetic[encoder_columns]),
    columns=encoder.get_feature_names_out(),
    index=X_train_synthetic.index
)

# Combine scaled numeric features with encoded categories
X_train_synthetic_ready = pd.concat(
    [
        X_train_synthetic[numerical_columns],
        synthetic_categories
    ],
    axis=1
)

# Match the original model's column order
X_train_synthetic_ready = X_train_synthetic_ready[
    X_train_encoded.columns
]

smotenc_model = LogisticRegression(max_iter=1000)
smotenc_model.fit(X_train_synthetic_ready, y_train_synthetic)

print("SMOTENC model trained.")
evaluation_results.append(evaluate_model("SMOTENC", smotenc_model, X_test_encoded, y_test))


''' STEP 14: Save Results'''
comparison = pd.DataFrame(evaluation_results)
comparison.to_csv("results/model.comparison.csv", index=False)
print("\nFinal Model Comparison")
print(comparison.head(10))

'''STEP 15: Save Baseline Model'''
# model_package = {
#     "model": baseline_model,
#     "encoder": encoder,
#     "scaler": scaler,
#     "charges_median": charges_median,
#     "input_columns": X_train.columns.tolist(),
#     "categorical_columns": encoder.feature_names_in_.tolist(),
#     "numeric_columns": list(numerical_columns),
#     "feature_columns": X_train_encoded.columns.tolist(),
#     "target_mapping": {"No": 0, "Yes": 1}
# }
#
# with open("models/baseline_model.pkl", "wb") as f:
#     pickle.dump(model_package, f)
# print("Baseline model saved.")