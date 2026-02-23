import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from datetime import date, timedelta
from typing import List, Dict
from app.services.stress_calculator import get_severity, get_tankers_needed


def prepare_features(rainfall_data: List[Dict], groundwater_data: List[Dict]) -> pd.DataFrame:
    """
    Convert raw DB data into a feature matrix for ML.
    
    Features per day:
    - rainfall_mm         : actual rainfall
    - normal_rainfall_mm  : expected normal rainfall
    - deviation           : how much below normal (key drought indicator)
    - gw_level            : groundwater level
    - gw_danger_ratio     : level vs safe threshold
    - rolling_avg_rain_7  : 7-day rolling average of rainfall
    """

    # Build rainfall dataframe
    rain_df = pd.DataFrame(rainfall_data)
    rain_df['recorded_date'] = pd.to_datetime(rain_df['recorded_date'])
    rain_df = rain_df.sort_values('recorded_date').reset_index(drop=True)
    rain_df['deviation'] = (
        (rain_df['normal_rainfall_mm'] - rain_df['rainfall_mm']) /
        rain_df['normal_rainfall_mm'].replace(0, 1)
    ).clip(0, 1)
    rain_df['rolling_avg_rain_7'] = rain_df['rainfall_mm'].rolling(7, min_periods=1).mean()

    # Build groundwater dataframe
    gw_df = pd.DataFrame(groundwater_data)
    gw_df['recorded_date'] = pd.to_datetime(gw_df['recorded_date'])
    gw_df = gw_df.sort_values('recorded_date').reset_index(drop=True)
    gw_df['gw_danger_ratio'] = (
        gw_df['safe_threshold_meters'] / gw_df['level_meters'].replace(0, 0.1)
    ).clip(0, 3)

    # Merge on date
    merged = pd.merge(
        rain_df[['recorded_date', 'rainfall_mm', 'normal_rainfall_mm', 'deviation', 'rolling_avg_rain_7']],
        gw_df[['recorded_date', 'level_meters', 'gw_danger_ratio']],
        on='recorded_date',
        how='inner'
    )

    # Add day index as a time feature (trend over time)
    merged['day_index'] = range(len(merged))

    return merged


def train_and_predict(
    rainfall_data: List[Dict],
    groundwater_data: List[Dict],
    population: int,
    forecast_days: int = 7
) -> List[Dict]:
    """
    Train Linear Regression model and predict stress for next N days.
    Returns list of daily predictions.
    """

    if len(rainfall_data) < 5 or len(groundwater_data) < 3:
        return []  # Not enough data to train

    df = prepare_features(rainfall_data, groundwater_data)

    if len(df) < 5:
        return []

    # Feature columns used for training
    feature_cols = ['day_index', 'deviation', 'rolling_avg_rain_7', 'gw_danger_ratio']

    # Target: stress score (calculated from existing formula)
    # We compute this from the training data itself as labels
    from app.services.stress_calculator import calculate_stress_score

    # Build per-row target scores as labels
    labels = []
    for _, row in df.iterrows():
        row_rain = [{
            'rainfall_mm': row['rainfall_mm'],
            'normal_rainfall_mm': row['normal_rainfall_mm']
        }]
        row_gw = [{
            'level_meters': row['level_meters'],
            'safe_threshold_meters': 5.0
        }]
        score = calculate_stress_score(row_rain, row_gw)
        labels.append(score)

    df['stress_score'] = labels

    X = df[feature_cols].values
    y = df['stress_score'].values

    # Scale features for better regression
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Train
    model = LinearRegression()
    model.fit(X_scaled, y)

    # Project future features for next N days
    predictions = []
    last_day_idx = df['day_index'].max()
    last_rain_avg = df['rolling_avg_rain_7'].iloc[-1]
    last_deviation = df['deviation'].iloc[-1]
    last_gw_danger = df['gw_danger_ratio'].iloc[-1]

    # Simulate slight worsening trend (drought conditions continue)
    # deviation increases slightly, gw danger increases slightly
    for i in range(1, forecast_days + 1):
        future_day_idx = last_day_idx + i

        # Gradual worsening simulation (drought rarely resolves in 7 days)
        future_deviation = min(last_deviation * (1 + 0.02 * i), 1.0)
        future_rain_avg  = max(last_rain_avg * (1 - 0.03 * i), 0)
        future_gw_danger = min(last_gw_danger * (1 + 0.015 * i), 3.0)

        X_future = np.array([[future_day_idx, future_deviation, future_rain_avg, future_gw_danger]])
        X_future_scaled = scaler.transform(X_future)

        predicted_score = float(model.predict(X_future_scaled)[0])
        predicted_score = round(min(max(predicted_score, 0), 10), 2)  # clamp to 0-10

        future_date = (date.today() + timedelta(days=i)).isoformat()
        severity    = get_severity(predicted_score)
        tankers     = get_tankers_needed(predicted_score, population)

        predictions.append({
            "date": future_date,
            "day": f"Day +{i}",
            "predicted_stress_score": predicted_score,
            "severity": severity,
            "tankers_needed": tankers,
            "confidence": round(max(0.95 - (i * 0.04), 0.65), 2)  # confidence drops with time
        })

    return predictions


def get_model_accuracy(rainfall_data: List[Dict], groundwater_data: List[Dict]) -> Dict:
    """
    Cross-validate the model and return accuracy metrics.
    Used to show judges how the ML model performs.
    """
    from sklearn.model_selection import cross_val_score
    from app.services.stress_calculator import calculate_stress_score

    if len(rainfall_data) < 8 or len(groundwater_data) < 5:
        return {"error": "Not enough data for accuracy evaluation"}

    df = prepare_features(rainfall_data, groundwater_data)
    if len(df) < 8:
        return {"error": "Insufficient merged data"}

    feature_cols = ['day_index', 'deviation', 'rolling_avg_rain_7', 'gw_danger_ratio']

    labels = []
    for _, row in df.iterrows():
        score = calculate_stress_score(
            [{'rainfall_mm': row['rainfall_mm'], 'normal_rainfall_mm': row['normal_rainfall_mm']}],
            [{'level_meters': row['level_meters'], 'safe_threshold_meters': 5.0}]
        )
        labels.append(score)

    df['stress_score'] = labels
    X = df[feature_cols].values
    y = df['stress_score'].values

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    model = LinearRegression()
    cv_scores = cross_val_score(model, X_scaled, y, cv=min(3, len(df)//2), scoring='r2')

    return {
        "r2_score": round(float(np.mean(cv_scores)), 3),
        "r2_std": round(float(np.std(cv_scores)), 3),
        "training_samples": len(df),
        "model": "Linear Regression",
        "features_used": feature_cols,
        "interpretation": "R² closer to 1.0 = better fit"
    }