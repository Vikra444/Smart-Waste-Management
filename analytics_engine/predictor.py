import random

class OverflowPredictor:
    """
    Industrial Predictive Analytics Engine for CleanCity AI.
    Forecasts when a bin will reach critical levels.
    """
    
    def predict_overflow_time(self, current_level, fill_rate_per_hour=5):
        """
        Calculates estimated time until overflow.
        Formula: (Threshold - Current) / FillRate
        """
        threshold = 95
        if current_level >= threshold:
            return 0  # Already critical
        
        remaining_capacity = threshold - current_level
        hours_remaining = remaining_capacity / fill_rate_per_hour
        
        return round(hours_remaining, 1)

    def get_forecast(self, bin_id, historical_data=None):
        # Placeholder for complex ML forecasting
        # For demo, we use a simple linear regression simulation
        return {
            "bin_id": bin_id,
            "trend": "Rising" if random.random() > 0.3 else "Stable",
            "est_hours_to_full": random.randint(2, 8)
        }

predictor = OverflowPredictor()
