from sklearn.cross_decomposition import PLSRegression

import pandas as pd
import numpy as np

_experiment_test = config['experiment_test']
_experiment_control = config['experiment_control']

plsr = PLSRegression(n_components=config['number_of_components'], scale=config['autoscale']) #, algorithm=self.config.get('algorithm'))

# We need classes to do the classification; should check and raise an error
class_idx = input_data.index.names.index('Class')
classes = list( input_data.index.levels[ class_idx ] )

Y = []
sample_filter_idx = []
for n, cv in enumerate(input_data.index.values):
    c = cv[class_idx]
    if c == _experiment_control:
        Y.append(0)
        sample_filter_idx.append(n)
    elif c == _experiment_test or _experiment_test == '*':
        Y.append(1)
        sample_filter_idx.append(n)


plsr.fit(input_data.values[sample_filter_idx,:], Y)

# Build scores into a dso no_of_samples x no_of_principal_components
scores = pd.DataFrame(plsr.x_scores_)  
scores.index = pd.MultiIndex.from_tuples([v for n, v in enumerate(input_data.index.values) if n in sample_filter_idx], names=list(input_data.index.names))

scoresl =[]
for n,s in enumerate(plsr.x_scores_.T):
    scoresl.append( 'Latent Variable %d' % (n+1) ) #, plsr.y_weights_[0][n])
scores.columns = scoresl


weights = pd.DataFrame( plsr.x_weights_.T )
weights.columns = input_data.columns

dso_lv = {}


# Generate simple result figure (using pathomx libs)
from pathomx.figures import spectra, scatterplot

weightsdc=[]
for n in range(0, plsr.x_weights_.shape[1] ):
    lvd =  pd.DataFrame( plsr.x_weights_[:,n:n+1].T )
    lvd.columns = input_data.columns

    vars()['LV%d' % (n+1)]  = spectra(lvd, styles=styles)

    #weightsdl.append("Weights on LV %s" % (n+1))
    weightsdc.append("LV %s" % (n+1))

weights.index = weightsdc

# Build scores plots for all combinations up to n
score_combinations = set([ (a,b) for a in range(0,n) for b in range(a+1, n+1)])

if config['plot_sample_numbers']:
    label_index = 'Sample'
else:
    label_index = None

for sc in score_combinations:
    vars()['Scores %dv%d' % (sc[0]+1, sc[1]+1)] = scatterplot(scores.iloc[:,sc], styles=styles, label_index=label_index)

weightsd = None;  # Clean up
lvd = None;  # Clean up
