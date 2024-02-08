# Setup Data Science Project in VSCode

--------

## Software 
1. Miniconda (for making a jupyter kernel)
2. Python version 3.11.7 or higher
3. Useful python packages:
    - Jupyter (required)
    - Pandas
    - Numpy
    - Scikit-learn
    - Seaborn
    - Matplotlib
4. VSCode extensions:
    - Jupyter
    - Python

## Online tutorial
https://code.visualstudio.com/docs/datascience/data-science-tutorial

## 1) Setup Miniconda
Miniconda allows user to create a python environment with all the packages the user needs.
- Download from: https://docs.anaconda.com/free/miniconda/
- Create environment:
`conda create -n <environment name> python=3.11 pandas jupyter seaborn scikit-learn numpy=1.26.0 matplotlib=3.8.0`

## 2) Setup VSCode
- Navigate to project folder
- `CTRL+SHIFT+P`, then select `Create: New Jupyter Notebook`
- Save the notebook and within the notebook select the kernel you made in step 1

------
If you have questions ask Jordi Vassallo.
Or read the online tutorial scrub.