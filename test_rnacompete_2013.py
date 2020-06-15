import os
import numpy as np
from tensorflow.keras import backend as K
from residualbind import ResidualBind
import helper

#---------------------------------------------------------------------------------------

# different deep learning models to try out
normalization = 'clip_norm'   # 'log_norm' or 'clip_norm'
ss_type = 'seq'                  # 'seq', 'pu', or 'struct'
data_path = '../data/RNAcompete_2013/rnacompete2013.h5'
results_path = helper.make_directory('../results', 'rnacompete_2013')
save_path = helper.make_directory(results_path, normalization+'_'+ss_type)

#---------------------------------------------------------------------------------------

# loop over different RNA binding proteins
pearsonr_scores = []
experiments = helper.get_experiment_names(data_path)
for rbp_index, experiment in enumerate(experiments):
    experiment = experiment.decode('UTF-8')
    print('Analyzing: '+ experiment)

    # load rbp dataset
    train, valid, test = helper.load_rnacompete_data(data_path, 
                                                     ss_type=ss_type, 
                                                     normalization=normalization, 
                                                     rbp_index=rbp_index)

    # load residualbind model
    input_shape = list(train['inputs'].shape)[1:]
    weights_path = os.path.join(save_path, experiment + '_weights.hdf5')    
    model = ResidualBind(input_shape, weights_path)
    
    # evaluate model
    corr = model.test_model(test, batch_size=100, weights='best')
    print("  Test: "+str(np.mean(corr)))

    pearsonr_scores.append(corr)
pearsonr_scores = np.array(pearsonr_scores)

print('FINAL RESULTS: %.4f+/-%.4f'%(np.mean(pearsonr_scores), np.std(pearsonr_scores)))

# save results to table
file_path = os.path.join(results_path, normalization+'_'+ss_type+'_performance.tsv')
f.write('%s\t%s\n'%('Experiment', 'Pearson score'))
with open(file_path, 'w') as f:
    for experiment, score in zip(experiments, pearsonr_scores):
        f.write('%s\t%.4f\n'%(experiment, score))