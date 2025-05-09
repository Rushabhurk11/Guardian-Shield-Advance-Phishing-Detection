# predictor.py
import numpy as np
from feature import FeatureExtraction

def predict_url(url, model):
    try:
        obj = FeatureExtraction(url)
        features = np.array(obj.getFeaturesList()).reshape(1, 30)
        pred = model.predict(features)[0]
        proba = model.predict_proba(features)[0]
        return pred, proba
    except Exception as e:
        print(f"[Error] Failed to predict URL: {e}")
        return None, None
