from pathlib import Path
import sys

import joblib
import sklearn.preprocessing
from sklearn.linear_model import LinearRegression

# compatibility patches for old sklearn pickle files
sys.modules["sklearn.preprocessing.data"] = sklearn.preprocessing
sys.modules["sklearn.externals.joblib"] = joblib
sys.modules["sklearn.linear_model.base"] = sklearn.linear_model
sys.modules["sklearn.svm.classes"] = sklearn.svm
sys.modules["sklearn.ensemble.forest"] = sklearn.ensemble
sys.modules["sklearn.tree.tree"] = sklearn.tree

# compatibility patch for old LinearRegression pickles
if not hasattr(LinearRegression, "positive"):
    LinearRegression.positive = False

class ModelLoader:
    @staticmethod
    def load_model(model_path: str):
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Model artifact not found: {model_path}")

        return joblib.load(path)