# Sales Forecasting with Rolling-Origin Backtesting

**Question:** a UK wholesaler needs a daily sales forecast for the next ~4 weeks. Which method should it use, and how far can it be trusted?

**Data:** daily gross sales built from the real, public UCI *Online Retail* transactions (304 trading days, Dec 2010 - 8 Dec 2011). The ready-made series is `data/daily_sales.csv`;
`src/make_daily_series.py` rebuilds it from the raw data with documented cleaning rules.

## Method
- **Rolling-origin backtest**: 13 forecast dates (every ~2 weeks), 24-trading-day horizon, each model sees only data up to its forecast date.
- **Baselines first**: naive, seasonal naive, trailing weekday mean, level x weekday profile; then ETS (Holt-Winters) and a pooled gradient-boosting model.
- **Metrics**: WAPE, bias, 4-week total error (not just one RMSE number), plus per-origin spread and win counts.
- **80% prediction intervals** from earlier errors only (no leakage), with measured coverage.

## Results (from the notebook)
| Model | Mean WAPE | Bias |
|---|---|---|
| Level x weekday profile | 30.9% | -8.0% |
| ETS (Holt-Winters) | 31.0% | -7.4% |
| Trailing weekday mean | 33.6% | -7.8% |
| Gradient boosting | 33.8% | +2.8% |
| Seasonal naive | 39.5% | -4.1% |
| Naive | 42.7% | +8.0% |

**Takeaways:** a simple profile beats naive methods clearly and ties with the more advanced models, so the simple one is recommended. The bigger risk is **bias**: forecasts are about +4% off before August
and about -16% from August on, because sales ramp up into the Sep-Nov peak. The 80% interval covered 81% of later days but is very wide (about 119% of the forecast), so day-level forecasts are a rough guide.

## Run it
```bash
pip install -r requirements.txt
jupyter notebook notebooks/06_sales_forecasting_backtesting.ipynb      # uses data/daily_sales.csv
python src/make_daily_series.py                                         # optional: rebuild the series from the raw UCI data
```

## Limitations
One year of data: annual seasonality can neither be learned nor validated. Only 13 origins with overlapping target windows, so gaps of a point or two are ties.
Total-company series only, no promotions/prices. Closed days are excluded, not forecast. Two mistaken wholesale orders were removed by rule.

*Data: UCI Machine Learning Repository, "Online Retail" (Chen, 2015, CC BY 4.0). Check the licence terms there before redistributing.*
