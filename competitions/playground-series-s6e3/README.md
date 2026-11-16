# Playground Series S6E3: Predict Customer Churn

[Competition page](https://www.kaggle.com/competitions/playground-series-s6e3) · binary classification · metric: ROC-AUC · 594k train rows, 255k test rows (synthetic, generated from the IBM Telco Customer Churn dataset)

## Notebooks

| Notebook | Approach | 5-fold CV AUC | Public LB | Private LB |
|---|---|---|---|---|
| [python/notebook.ipynb](python/notebook.ipynb) · [on Kaggle](https://www.kaggle.com/code/felipeterrazas/s6e3-churn-gbdt-ensemble-python) | LightGBM + XGBoost + CatBoost, rank-averaged | **0.91677** | **0.91413** | **0.91547** |
| [r/notebook.ipynb](r/notebook.ipynb) | tidymodels recipe + XGBoost, tuned on a 100k sample | 0.91517 | 0.91230 | 0.91354 |
| first submission (March 2026, during the competition) | single XGBoost, label-encoded | n/a | 0.91223 | 0.91358 |

The Python ensemble's public score would rank about 1,218 of 4,143 on the final public leaderboard, against 2,895 for the March submission. The winning score was 0.91773. These scores come from late submissions made after the deadline (16 Nov 2026).

## What worked and what didn't

- **Native categorical handling** (LightGBM/XGBoost category dtype, CatBoost cat features) beat label encoding: +0.002 AUC over the first submission.
- **Three engineered features** (`avg_charge`, `charge_gap`, `n_services`) gave a small gain with a slower learning rate (0.02).
- **Blending three GBDTs** added +0.0002 over the best single model. The models agree strongly (Spearman 0.995 or higher), so there is little left to gain from blending.
- **Did not help:** treating the numeric columns as categoricals (overfits), target encoding from the original IBM dataset, and appending the original dataset to the training folds.

## Reproduce

```bash
python -m kaggle competitions download -c playground-series-s6e3 -p data   # then unzip into data/
# Python: open python/notebook.ipynb in VS Code (≈65 min on 12 cores, most of it CatBoost)
# R: open r/notebook.ipynb with the IRkernel "R" kernel (≈18 min)
kaggle kernels push -p python    # rerun the Python notebook on Kaggle
```

Kaggle no longer accepts R kernels, so the R notebook lives here only.
