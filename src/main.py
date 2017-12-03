import numpy as np
import os
from vgan import VGAN
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from helpers import save_fig_mnist25
from mnist_deep import MNIST

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

if __name__ == '__main__':
    # generate and dump graphs
    trainning = True
    testing = False

    model_folder = '../models'
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)

    gg = VGAN(model_folder)
    if trainning:
        batch_size = 50
        n_iters = 30000
        print_counter = 500
        # inp_path = os.path.abspath('../out_samples/inp_training')
        out_path = os.path.abspath('../outputs/')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        data = input_data.read_data_sets('../dataset/MNIST_data', one_hot=True)
        gg.train(data, batch_size, n_iters, print_counter, out_path)
    # Generate
    if testing:
        n_samples = 100
        # out_path = os.path.abspath('../out_mnist/')
        # if not os.path.exists(out_path):
            # os.makedirs(out_path)

        samples = gg.generate_sample(n_samples) # yields
        # all_samples = []
        # save_fig_mnist25(samples, out_path, 1)

        tf.reset_default_graph() # important

        nnet = MNIST()
        y_pred = nnet.classify(samples)
        x = np.unique(y_pred)
        print("#Modes = %d on \d samples \n", len(x), n_samples)
        # from IPython import embed; embed()
        # count # of distinct values
        # calculate KL
