from sklearn.neighbors import NearestNeighbors

import argparse as ag
import importlib.machinery as im
import numpy as np
import types


def nn_distance(args):
    """ Calculates the nearest neighbors distance """

    # Get data
    dataTransformer = _loadModule(
        'TransformData.py',
        'TransformData.py'
    )
    realData = dataTransformer.transform_data(
        'Real_Data/Zero/',  # args.trainDir,
        args.samRate,
        args.fileCount
    )
    genData = dataTransformer.transform_data(
        args.queryDir,
        args.samRate,
        args.fileCount
    )

    realData = np.reshape(realData, [realData.shape[0], -1])
    genData = np.reshape(genData, [genData.shape[0], -1])

    # Create models and calculate
    nn = NearestNeighbors(
        n_neighbors=1,
        algorithm='ball_tree'
    ).fit(realData)
    distances, _ = nn.kneighbors(genData)

    # Return results
    distances = distances[:, 0]

    # Print the results
    print('Mean          : ' + str(np.mean(distances)))
    print('Standard Error: ' + str(np.std(distances)))

    return


def _loadModule(modName, modPath):
    """ Loads the module containing the relevant networks """
    loader = im.SourceFileLoader(modName, modPath)
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    return mod


if __name__ == '__main__':

    parser = ag.ArgumentParser()
    parser.add_argument(
        '-trainDir',
        type=str,
        help='The training set for the KNN model.'
    )
    parser.add_argument(
        '-queryDir',
        type=str,
        help='The query set for the KNN model.'
    )
    parser.add_argument(
        '-samRate',
        type=int,
        help='The sample rate of the data to analyse.'
    )
    parser.add_argument(
        '-fileCount',
        type=int,
        help='The amount of real data to test.'
    )
    args = parser.parse_args()

    nn_distance(args)
