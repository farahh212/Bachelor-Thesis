# save metadata 

from pathlib import Path
from datetime import datetime
import json
import logging
import time

import joblib
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt

from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)
DATASET_PATH = Path(__file__).parent / "synthetic_SHC_dataset.csv"
RESULTS_DIR = Path(__file__).parent
RESULTS_DIR.mkdir(exist_ok=True)

# Setup logging
def setup_logging():
    """Configure logging to both console and file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = RESULTS_DIR / f"training_log_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger("ConnectionClassifierTraining")
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler with simpler formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, log_file

# Numeric features that actually exist in the generated dataset
FEATURE_NUMERIC = [
    "shaft_diameter",
    "hub_length",
    "has_bending",          # stored as 0.0 / 1.0
    "safety_factor",
    "hub_outer_diameter",
    "shaft_inner_diameter",  # NaN for solid shafts → will be filled
    "required_torque",
    "pref_ease",
    "pref_movement",
    "pref_cost",
    "pref_vibration",
    "pref_speed",
    "pref_bidirectional",
    "pref_maintenance",
    "pref_durability",
]

# Categorical features from the dataset
CATEGORICAL = [
    "shaft_type",
    "shaft_material",
    "surface_condition",
]


def _build_preprocessor():
    numeric_transformer = Pipeline(
        steps=[("scaler", StandardScaler())]
    )
    categorical_transformer = Pipeline(
        steps=[("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, FEATURE_NUMERIC),
            ("cat", categorical_transformer, CATEGORICAL),
        ],
        remainder="drop",
    )


def _build_models():
    return {
        "Random Forest": RandomForestClassifier(
            n_estimators=150,
            random_state=42,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=150,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42,
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=150,
            random_state=42,
        ),
        "CatBoost": CatBoostClassifier(
            n_estimators=150,
            verbose=0,
            random_state=42,
        ),
    }

def save_feature_importance_plot(pipeline: Pipeline, out_path: Path, top_n: int = 20, model_name: str = "Model") -> bool:
    """
    Saves a feature importance bar chart for tree models inside a sklearn Pipeline.
    Returns True if saved, False if not supported.
    """
    if not isinstance(pipeline, Pipeline):
        return False
    if "preprocess" not in pipeline.named_steps:
        return False

    pre = pipeline.named_steps["preprocess"]

    # Get expanded feature names (numeric + one-hot)
    try:
        feature_names = pre.get_feature_names_out()
    except Exception:
        return False

    # Pick estimator step name
    if "model" in pipeline.named_steps:
        est = pipeline.named_steps["model"]
    else:
        return False

    # Get importances for supported estimators
    importances = None
    if hasattr(est, "feature_importances_"):
        importances = np.asarray(est.feature_importances_, dtype=float)
    elif hasattr(est, "get_feature_importance"):
        # catboost native method (usually not needed if feature_importances_ exists)
        try:
            importances = np.asarray(est.get_feature_importance(), dtype=float)
        except Exception:
            return False
    else:
        return False

    if importances is None or len(importances) != len(feature_names):
        return False

    # Top N
    idx = np.argsort(importances)[::-1][:top_n]
    top_feats = np.array(feature_names)[idx]
    top_vals = importances[idx]

    # Plot with enhanced styling
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_feats)))
    bars = ax.barh(range(len(top_feats))[::-1], top_vals[::-1], color=colors, edgecolor='black', alpha=0.8)
    
    # Clean feature names for better readability (remove prefixes from one-hot encoded features)
    clean_labels = []
    for feat in top_feats[::-1]:
        # Remove prefixes like "cat__shaft_type_" or "num__"
        if "__" in feat:
            clean_feat = feat.split("__")[-1]
            # Capitalize and add spaces for readability
            clean_feat = clean_feat.replace("_", " ").title()
        else:
            clean_feat = feat.replace("_", " ").title()
        clean_labels.append(clean_feat)
    
    ax.set_yticks(range(len(top_feats))[::-1])
    ax.set_yticklabels(clean_labels, fontsize=10)
    ax.set_xlabel("Feature Importance", fontsize=12, fontweight='bold')
    ax.set_title(f"Top {top_n} Feature Importances - {model_name}", 
                 fontsize=13, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, top_vals[::-1])):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2,
                f' {width:.4f}',
                ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return True


def save_cm_heatmap(cm, labels, title, out_path):
    """Save confusion matrix as a heatmap image."""
    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(ax=ax, cmap="viridis", values_format="d", colorbar=True)  # heatmap look
    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    # Setup logging
    logger, log_file = setup_logging()
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    logger.info("=" * 80)
    logger.info("CONNECTION CLASSIFIER TRAINING - STARTED")
    logger.info(f"Timestamp: {timestamp}")
    logger.info("=" * 80)
    
    # Initialize results dictionary
    results = {
        "experiment_info": {
            "timestamp": timestamp,
            "dataset_path": str(DATASET_PATH),
            "test_size": 0.2,
            "random_state": 42,
        },
        "dataset_statistics": {},
        "feature_configuration": {
            "numeric_features": FEATURE_NUMERIC,
            "categorical_features": CATEGORICAL,
            "total_features": len(FEATURE_NUMERIC) + len(CATEGORICAL),
        },
        "model_configurations": {},
        "model_results": {},
        "best_model": {},
        "training_summary": {},
    }
    
    logger.info("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    logger.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
    
    # Dataset statistics
    initial_rows = len(df)
    results["dataset_statistics"]["initial_rows"] = initial_rows
    results["dataset_statistics"]["initial_columns"] = len(df.columns)
    
    # Handle expected NaNs: shaft_inner_diameter is None for solid shafts
    if "shaft_inner_diameter" in df.columns:
        nan_count = df["shaft_inner_diameter"].isna().sum()
        df["shaft_inner_diameter"] = df["shaft_inner_diameter"].fillna(0.0)
        logger.info(f"Filled {nan_count} NaN values in 'shaft_inner_diameter' with 0.0 (solid shafts)")
        results["dataset_statistics"]["filled_nan_shaft_inner_diameter"] = int(nan_count)

    # Basic guard: drop rows missing critical geometry/label
    required_cols = ["shaft_diameter", "hub_length", "required_torque", "label"]
    rows_before_drop = len(df)
    df = df.dropna(subset=required_cols)
    rows_after_drop = len(df)
    dropped_rows = rows_before_drop - rows_after_drop
    if dropped_rows > 0:
        logger.warning(f"Dropped {dropped_rows} rows with missing required columns")
    results["dataset_statistics"]["rows_after_cleaning"] = rows_after_drop
    results["dataset_statistics"]["dropped_rows"] = dropped_rows

    features = FEATURE_NUMERIC + CATEGORICAL
    X = df[features].copy()
    y_raw = df["label"].astype(str)   # "press", "key", "spline"
    
    # Label distribution
    label_counts = y_raw.value_counts().to_dict()
    logger.info(f"Label distribution: {label_counts}")
    results["dataset_statistics"]["label_distribution"] = {str(k): int(v) for k, v in label_counts.items()}

    # --- label-encode target so classifiers are happy ---
    le = LabelEncoder()
    y = le.fit_transform(y_raw)  # 0,1,2 - NO +1 SHIFT!
    label_mapping = {int(idx): label for idx, label in enumerate(le.classes_)}
    logger.info(f"Label encoding: {label_mapping}")
    results["dataset_statistics"]["label_mapping"] = label_mapping
    results["dataset_statistics"]["classes"] = le.classes_.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    logger.info(f"Train set: {len(X_train)} samples, Test set: {len(X_test)} samples")
    results["dataset_statistics"]["train_samples"] = len(X_train)
    results["dataset_statistics"]["test_samples"] = len(X_test)
    
    # Feature statistics
    logger.info("Computing feature statistics...")
    numeric_stats = X_train[FEATURE_NUMERIC].describe().to_dict()
    categorical_counts = {}
    for cat_feat in CATEGORICAL:
        categorical_counts[cat_feat] = X_train[cat_feat].value_counts().to_dict()
    results["dataset_statistics"]["numeric_feature_statistics"] = {
        k: {stat: float(v) for stat, v in stats.items()} 
        for k, stats in numeric_stats.items()
    }
    results["dataset_statistics"]["categorical_feature_counts"] = {
        k: {str(cat): int(count) for cat, count in counts.items()}
        for k, counts in categorical_counts.items()
    }

    preprocessor = _build_preprocessor()
    models = _build_models()
    
    # Log model configurations
    for name, estimator in models.items():
        model_config = {
            "type": type(estimator).__name__,
            "parameters": estimator.get_params(),
        }
        results["model_configurations"][name] = model_config
        logger.info(f"{name} configuration: {model_config['type']} with {len(model_config['parameters'])} parameters")

    best_name = None
    best_score = -1.0
    best_metrics = {}
    best_model = None
    all_model_results = {}

    # Train individual models
    logger.info("=" * 80)
    logger.info("TRAINING INDIVIDUAL MODELS")
    logger.info("=" * 80)
    
    for name, estimator in models.items():
        logger.info(f"\n--- Training {name} ---")
        clf = Pipeline(steps=[("preprocess", preprocessor), ("model", estimator)])
        
        train_start = time.time()
        clf.fit(X_train, y_train)
        train_time = time.time() - train_start
        logger.info(f"Training completed in {train_time:.2f} seconds")
        
        y_pred = clf.predict(X_test)
        pred_time = time.time() - train_start - train_time
        
        # Compute metrics
        acc = accuracy_score(y_test, y_pred)
        prec_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
        rec_macro = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
        prec_weighted = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec_weighted = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        cm_path = RESULTS_DIR / f"confusion_matrix_{name.replace(' ', '_')}.png"
        save_cm_heatmap(
            cm,
            labels=le.classes_,
            title=f"Confusion Matrix - {name}",
            out_path=cm_path,
        )
        logger.info(f"Saved confusion matrix heatmap to {cm_path}")

        
        # Per-class metrics
        prec_per_class = precision_score(y_test, y_pred, average=None, zero_division=0)
        rec_per_class = recall_score(y_test, y_pred, average=None, zero_division=0)
        f1_per_class = f1_score(y_test, y_pred, average=None, zero_division=0)
        
        # Classification report
        class_report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True, zero_division=0)
        
        logger.info(f"Accuracy: {acc:.4f}")
        logger.info(f"Precision (macro): {prec_macro:.4f}")
        logger.info(f"Recall (macro): {rec_macro:.4f}")
        logger.info(f"F1-score (macro): {f1_macro:.4f}")
        logger.info(f"Precision (weighted): {prec_weighted:.4f}")
        logger.info(f"Recall (weighted): {rec_weighted:.4f}")
        logger.info(f"F1-score (weighted): {f1_weighted:.4f}")
        logger.info(f"Confusion Matrix:\n{cm}")
        
        # Log per-class metrics
        logger.info("Per-class metrics:")
        for idx, class_name in enumerate(le.classes_):
            logger.info(f"  {class_name}: Precision={prec_per_class[idx]:.4f}, "
                       f"Recall={rec_per_class[idx]:.4f}, F1={f1_per_class[idx]:.4f}")
        
        model_result = {
            "accuracy": float(acc),
            "precision_macro": float(prec_macro),
            "recall_macro": float(rec_macro),
            "f1_macro": float(f1_macro),
            "precision_weighted": float(prec_weighted),
            "recall_weighted": float(rec_weighted),
            "f1_weighted": float(f1_weighted),
            "confusion_matrix": cm.tolist(),
            "per_class_metrics": {
                str(le.classes_[idx]): {
                    "precision": float(prec_per_class[idx]),
                    "recall": float(rec_per_class[idx]),
                    "f1_score": float(f1_per_class[idx]),
                }
                for idx in range(len(le.classes_))
            },
            "classification_report": class_report,
            "training_time_seconds": float(train_time),
            "prediction_time_seconds": float(pred_time),
        }
        
        all_model_results[name] = model_result
        
        if f1_macro > best_score:
            best_score = f1_macro
            best_name = name
            best_model = clf
            best_metrics = model_result.copy()
            logger.info(f"*** New best model: {name} (F1-macro: {f1_macro:.4f}) ***")

    # Ensemble voting using the same base estimators
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING ENSEMBLE MODEL")
    logger.info("=" * 80)
    
    estimators = [(name, est) for name, est in models.items()]
    ensemble = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("voting", VotingClassifier(estimators=estimators, voting="soft", n_jobs=-1)),
        ]
    )
    
    train_start = time.time()
    ensemble.fit(X_train, y_train)
    train_time = time.time() - train_start
    logger.info(f"Ensemble training completed in {train_time:.2f} seconds")
    
    y_pred = ensemble.predict(X_test)
    pred_time = time.time() - train_start - train_time
    
    ensemble_acc = accuracy_score(y_test, y_pred)
    ensemble_prec_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
    ensemble_rec_macro = recall_score(y_test, y_pred, average="macro", zero_division=0)
    ensemble_f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
    ensemble_prec_weighted = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    ensemble_rec_weighted = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    ensemble_f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    ensemble_cm = confusion_matrix(y_test, y_pred)

    cm_path = RESULTS_DIR / "confusion_matrix_Ensemble.png"
    save_cm_heatmap(
        ensemble_cm,
        labels=le.classes_,
        title="Confusion Matrix - Ensemble",
        out_path=cm_path,
    )
    logger.info(f"Saved confusion matrix heatmap to {cm_path}")

        
    # Per-class metrics for ensemble
    ensemble_prec_per_class = precision_score(y_test, y_pred, average=None, zero_division=0)
    ensemble_rec_per_class = recall_score(y_test, y_pred, average=None, zero_division=0)
    ensemble_f1_per_class = f1_score(y_test, y_pred, average=None, zero_division=0)
    ensemble_class_report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True, zero_division=0)
    
    logger.info(f"Ensemble Accuracy: {ensemble_acc:.4f}")
    logger.info(f"Ensemble Precision (macro): {ensemble_prec_macro:.4f}")
    logger.info(f"Ensemble Recall (macro): {ensemble_rec_macro:.4f}")
    logger.info(f"Ensemble F1-score (macro): {ensemble_f1_macro:.4f}")
    logger.info(f"Ensemble Precision (weighted): {ensemble_prec_weighted:.4f}")
    logger.info(f"Ensemble Recall (weighted): {ensemble_rec_weighted:.4f}")
    logger.info(f"Ensemble F1-score (weighted): {ensemble_f1_weighted:.4f}")
    logger.info(f"Ensemble Confusion Matrix:\n{ensemble_cm}")
    
    logger.info("Ensemble per-class metrics:")
    for idx, class_name in enumerate(le.classes_):
        logger.info(f"  {class_name}: Precision={ensemble_prec_per_class[idx]:.4f}, "
                   f"Recall={ensemble_rec_per_class[idx]:.4f}, F1={ensemble_f1_per_class[idx]:.4f}")
    
    ensemble_result = {
        "accuracy": float(ensemble_acc),
        "precision_macro": float(ensemble_prec_macro),
        "recall_macro": float(ensemble_rec_macro),
        "f1_macro": float(ensemble_f1_macro),
        "precision_weighted": float(ensemble_prec_weighted),
        "recall_weighted": float(ensemble_rec_weighted),
        "f1_weighted": float(ensemble_f1_weighted),
        "confusion_matrix": ensemble_cm.tolist(),
        "per_class_metrics": {
            str(le.classes_[idx]): {
                "precision": float(ensemble_prec_per_class[idx]),
                "recall": float(ensemble_rec_per_class[idx]),
                "f1_score": float(ensemble_f1_per_class[idx]),
            }
            for idx in range(len(le.classes_))
        },
        "classification_report": ensemble_class_report,
        "training_time_seconds": float(train_time),
        "prediction_time_seconds": float(pred_time),
    }
    
    all_model_results["Ensemble"] = ensemble_result
    
    if ensemble_f1_macro > best_score:
        best_score = ensemble_f1_macro
        best_name = "Ensemble"
        best_model = ensemble
        best_metrics = ensemble_result.copy()
        logger.info(f"*** New best model: Ensemble (F1-macro: {ensemble_f1_macro:.4f}) ***")

    logger.info("\n" + "=" * 80)
    logger.info(f"SELECTED BEST MODEL: {best_name} (F1-macro: {best_score:.4f})")
    logger.info("=" * 80)

    # Save feature importance plot for best model
        # Feature importance (thesis Figure 4.5)
    fi_path = RESULTS_DIR / f"feature_importance_{best_name.replace(' ', '_')}.png"
    ok = save_feature_importance_plot(best_model, fi_path, top_n=20, model_name=best_name)
    if ok:
        logger.info(f"Saved feature importance plot to {fi_path}")
    else:
        logger.warning("Feature importance plot not available for selected model/pipeline.")


    # Save results
    results["model_results"] = all_model_results
    results["best_model"] = {
        "name": best_name,
        "f1_macro": float(best_score),
        "metrics": best_metrics,
    }
    
    total_time = time.time() - start_time
    results["training_summary"] = {
        "total_training_time_seconds": float(total_time),
        "total_training_time_minutes": float(total_time / 60),
        "models_trained": len(all_model_results),
        "best_model_name": best_name,
        "best_f1_macro": float(best_score),
    }
    
    logger.info(f"\nTotal training time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")

    model_path = MODEL_DIR / "connection_classifier.pkl"
    meta_path = MODEL_DIR / "connection_classifier_meta.pkl"
    results_path = RESULTS_DIR / f"training_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    joblib.dump(best_model, model_path)
    logger.info(f"Saved best model ({best_name}) to {model_path}")
    
    joblib.dump(
        {
            "features": features,
            "numeric": FEATURE_NUMERIC,
            "categorical": CATEGORICAL,
            "range": {"shaft_diameter": (6, 230)},
            "best_model": best_name,
            "best_metrics": {
                "accuracy": best_metrics["accuracy"],
                "precision_macro": best_metrics["precision_macro"],
                "recall_macro": best_metrics["recall_macro"],
                "f1_macro": best_metrics["f1_macro"],
                "confusion_matrix": best_metrics["confusion_matrix"],
            },
            "classes": le.classes_.tolist(),
            "label_mapping": label_mapping,
        },
        meta_path,
    )
    logger.info(f"Saved metadata to {meta_path}")
    
    # Save detailed results to JSON
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved detailed results to {results_path}")
    
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"Log file: {log_file}")
    logger.info(f"Results file: {results_path}")
    logger.info(f"Model file: {model_path}")
    logger.info(f"Metadata file: {meta_path}")


if __name__ == "__main__":
    main()