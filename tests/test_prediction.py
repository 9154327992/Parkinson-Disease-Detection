"""
Unit Tests for Prediction Module
"""

import pytest

from app.ml.predict import ParkinsonPredictor
from app.ml.preprocessing import Preprocessor
from app.ml.feature_engineering import FeatureEngineering


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def predictor():
    return ParkinsonPredictor()


@pytest.fixture
def sample_features():
    """
    Sample Parkinson voice features (22 features).
    """

    return [

        119.992,
        157.302,
        74.997,
        0.00784,
        0.00007,
        0.00370,
        0.00554,
        0.01109,
        0.04374,
        0.426,
        0.02182,
        0.03130,
        0.02971,
        0.06545,
        0.02211,
        21.033,
        0.414783,
        0.815285,
        -4.813031,
        0.266482,
        2.301442,
        0.284654,

    ]


# ==========================================================
# Feature Validation
# ==========================================================

def test_feature_count(sample_features):

    assert len(sample_features) == 22


def test_feature_validation(sample_features):

    fe = FeatureEngineering()

    assert fe.validate_features(sample_features)


def test_invalid_feature_count():

    fe = FeatureEngineering()

    invalid = [1.0] * 20

    assert not fe.validate_features(invalid)


# ==========================================================
# Preprocessing
# ==========================================================

def test_preprocessor_transform(sample_features):

    pre = Preprocessor()

    transformed = pre.transform(sample_features)

    assert transformed is not None


def test_preprocessor_output_dimension(sample_features):

    pre = Preprocessor()

    transformed = pre.transform(sample_features)

    assert len(transformed[0]) == 22


# ==========================================================
# Prediction
# ==========================================================

def test_prediction_returns_dictionary(

    predictor,
    sample_features,

):

    result = predictor.predict(sample_features)

    assert isinstance(result, dict)


def test_prediction_contains_label(

    predictor,
    sample_features,

):

    result = predictor.predict(sample_features)

    assert "prediction" in result


def test_prediction_contains_probability(

    predictor,
    sample_features,

):

    result = predictor.predict(sample_features)

    assert "probability" in result


def test_prediction_contains_confidence(

    predictor,
    sample_features,

):

    result = predictor.predict(sample_features)

    assert "confidence" in result


def test_prediction_contains_risk_level(

    predictor,
    sample_features,

):

    result = predictor.predict(sample_features)

    assert "risk_level" in result


# ==========================================================
# Probability
# ==========================================================

def test_probability_range(

    predictor,
    sample_features,

):

    result = predictor.predict(sample_features)

    probability = result["probability"]

    assert 0 <= probability <= 1


def test_confidence_range(

    predictor,
    sample_features,

):

    result = predictor.predict(sample_features)

    confidence = result["confidence"]

    assert 0 <= confidence <= 100


# ==========================================================
# Risk Levels
# ==========================================================

def test_valid_risk_level(

    predictor,
    sample_features,

):

    result = predictor.predict(sample_features)

    assert result["risk_level"] in [

        "Minimal",
        "Low",
        "Moderate",
        "High",

    ]


# ==========================================================
# Batch Prediction
# ==========================================================

def test_batch_prediction(

    predictor,
    sample_features,

):

    batch = [

        sample_features,

        sample_features,

    ]

    results = predictor.batch_predict(batch)

    assert len(results) == 2


# ==========================================================
# Invalid Inputs
# ==========================================================

def test_empty_input(

    predictor,

):

    with pytest.raises(Exception):

        predictor.predict([])


def test_none_input(

    predictor,

):

    with pytest.raises(Exception):

        predictor.predict(None)


def test_string_input(

    predictor,

):

    with pytest.raises(Exception):

        predictor.predict("invalid")


# ==========================================================
# Health Check
# ==========================================================

def test_predictor_health(

    predictor,

):

    status = predictor.health_check()

    assert status["status"] == "Healthy"
