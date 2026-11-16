# Kaggle

My Kaggle competitions and dataset projects. I build them in VS Code, version them here, and push the notebooks to Kaggle with the [Kaggle CLI](https://github.com/Kaggle/kaggle-cli).

Profile: [kaggle.com/felipeterrazas](https://www.kaggle.com/felipeterrazas)

## Layout

```
competitions/<competition-slug>/   one folder per competition
datasets/<dataset-slug>/           projects built on a public dataset
    notebook.ipynb                 runs locally and on Kaggle unchanged
    kernel-metadata.json           where `kaggle kernels push` publishes it
    data/                          downloaded data (git-ignored)
    submissions/                   local submission files (git-ignored)
tools/new_project.py               scaffolds a new project folder
```

Data is never committed. Every project can re-download it with the CLI, and competition rules usually forbid redistributing it.

## Setup

```bash
pip install -r requirements.txt
kaggle auth login          # opens the browser once; credentials are cached
```

## Workflow

```bash
# 1. Start a project (downloads data into data/)
python tools/new_project.py competition titanic
python tools/new_project.py dataset mlg-ulb/creditcardfraud --title "Credit Card Fraud EDA"

# 2. Work in notebook.ipynb in VS Code, commit to GitHub as usual

# 3. Push the notebook to Kaggle and run it there
kaggle kernels push -p competitions/titanic
kaggle kernels status felipeterrazas/titanic
kaggle kernels output felipeterrazas/titanic -p competitions/titanic/submissions

# 4. Submit to a competition
kaggle competitions submit -c titanic -f competitions/titanic/submissions/submission.csv -m "baseline"
kaggle competitions submissions -c titanic

# Bring a notebook you edited on the Kaggle website back here
# (pull saves it as <slug>.ipynb; rename over notebook.ipynb before committing)
kaggle kernels pull felipeterrazas/titanic -p competitions/titanic
```

For competitions you must accept the rules on the competition page before the CLI can download data or submit.
