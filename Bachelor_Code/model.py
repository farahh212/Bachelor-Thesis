# train_shc_xgb.py
import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

# XGBoost
from xgboost import XGBClassifier

# ------------------------------------------------------------------
# 1) Load data
# ------------------------------------------------------------------
CSV_PATH = r"C:\Users\farah\Desktop\Bachelor Thesis\Bachelor_Code\synthetic_SHC_dataset_DIN_full_PATCHED.csv"
df = pd.read_csv(CSV_PATH)

# Keep only the classes we want to predict
df = df[df["label"].isin(["press", "key", "spline"])].copy()
df.reset_index(drop=True, inplace=True)

# ------------------------------------------------------------------
# 2) Define features (avoid leakage!)
# ------------------------------------------------------------------
LEAK_COLS = {
    "p_erf","p_zul","Z_erf","Z_zul","G","U_erf","U_zul","U_nom",
    "tol_shaft_mm","tol_hub_mm","QI","QA",
    "Mt_from_pzul","Mt_press",
    "Mt_key","Mt_spline",
    "label","label_score","Mt_label",
    "score_press","score_key","score_spline",
    "assembly_method","tA","tI",
}

CANDIDATE_FEATURES = [
    "d_mm","L_mm","L_rule","bending",
    "shaft_mat","hub_mat","shaft_type",
    "DiI_mm","DaA_mm","mu","S_R","RzI_um","RzA_um",
    "M_req_Nmm",
    "key_b_mm","key_h_mm","key_l_mm",
    "spline_z","spline_b_mm","spline_hproj_mm","spline_D_mm",
    "pref_ease","pref_movement","pref_cost","pref_vibration","pref_speed","pref_bidirectional",
]

all_cols = set(df.columns)
safe_features = [c for c in CANDIDATE_FEATURES if c in all_cols and c not in LEAK_COLS]

X = df[safe_features].copy()
y = df["label"]

# ------------------------------------------------------------------
# 3) Encode labels → numeric
# ------------------------------------------------------------------
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_enc = le.fit_transform(y)
print("Label mapping:", dict(zip(le.classes_, le.transform(le.classes_))))

# ------------------------------------------------------------------
# 4) Split
# ------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.20, random_state=42, stratify=y_enc
)

# ------------------------------------------------------------------
# 5) Preprocessing: numerics vs categoricals
# ------------------------------------------------------------------
cat_cols = X.select_dtypes(include=["object","bool","category"]).columns.tolist()
num_cols = [c for c in X.columns if c not in cat_cols]

numeric_pipe = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipe = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])

preprocess = ColumnTransformer(
    transformers=[
        ("num", numeric_pipe, num_cols),
        ("cat", categorical_pipe, cat_cols),
    ],
    remainder="drop"
)

# ------------------------------------------------------------------
# 6) XGBoost model
# ------------------------------------------------------------------
xgb = XGBClassifier(
    objective="multi:softprob",
    num_class=len(le.classes_),
    eval_metric="mlogloss",
    tree_method="hist",
    learning_rate=0.08,
    n_estimators=500,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.0,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1
)

model = Pipeline(steps=[
    ("prep", preprocess),
    ("clf", xgb)
])

# ------------------------------------------------------------------
# 7) Train
# ------------------------------------------------------------------
print("\nTraining model...")
model.fit(X_train, y_train)
print("Training complete.\n")

# ------------------------------------------------------------------
# 8) Evaluate
# ------------------------------------------------------------------
pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)
f1m = f1_score(y_test, pred, average="macro")

print(f"Accuracy: {acc:.3f}")
print(f"Macro F1: {f1m:.3f}\n")
print("Classification report:")
print(classification_report(y_test, pred, target_names=le.classes_, digits=3))

print("Confusion matrix (rows=true, cols=pred):")
print(pd.DataFrame(confusion_matrix(y_test, pred), 
                   index=le.classes_, columns=le.classes_))

# ------------------------------------------------------------------
# 9) Feature importances
# ------------------------------------------------------------------
prep = model.named_steps["prep"]
feature_names = []
if len(num_cols):
    feature_names += list(num_cols)
if len(cat_cols):
    ohe = prep.named_transformers_["cat"].named_steps["ohe"]
    cat_names = ohe.get_feature_names_out(cat_cols).tolist()
    feature_names = list(num_cols) + cat_names

booster = model.named_steps["clf"].get_booster()
importances = booster.get_fscore()
mapped = []
for i, fname in enumerate(feature_names):
    score = importances.get(f"f{i}", 0.0)
    mapped.append((fname, score))

fi = pd.DataFrame(mapped, columns=["feature","importance"]).sort_values("importance", ascending=False)
print("\nTop 20 features by XGBoost split-gain proxy:")
print(fi.head(20).to_string(index=False))

# ------------------------------------------------------------------
# 10) Save model + encoder + metadata
# ------------------------------------------------------------------
OUT_DIR = "./models"
os.makedirs(OUT_DIR, exist_ok=True)
joblib.dump(model, os.path.join(OUT_DIR, "shc_xgb_model.pkl"))
joblib.dump(le, os.path.join(OUT_DIR, "label_encoder.pkl"))
meta = {
    "features_used": safe_features,
    "cat_cols": cat_cols,
    "num_cols": num_cols,
    "classes": le.classes_.tolist()
}
joblib.dump(meta, os.path.join(OUT_DIR, "shc_xgb_meta.pkl"))

print("\nSaved:")
print(" - models/shc_xgb_model.pkl")
print(" - models/label_encoder.pkl")
print(" - models/shc_xgb_meta.pkl")

# ------------------------------------------------------------------
# 11) Example inference
# ------------------------------------------------------------------
# X_new = X_test.iloc[:5].copy()
# y_hat = le.inverse_transform(model.predict(X_new))
# print("\nSample predictions:", y_hat.tolist())
