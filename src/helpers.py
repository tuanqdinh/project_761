import matplotlib
matplotlib.use('Agg')
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import random
import Reader

from sklearn import datasets

# Dataset iterator
def inf_train_gen(DATASET, BATCH_SIZE):
    if DATASET == '25gaussians':
        dataset = []
        for i in range(int(100000/25)):
            for x in range(-2, 3):
                for y in range(-2, 3):
                    point = np.random.randn(2)*0.05
                    point[0] += 2*x
                    point[1] += 2*y
                    dataset.append(point)
        dataset = np.array(dataset, dtype='float32')
        np.random.shuffle(dataset)
        dataset /= 2.828 # stdev
        while True:
            for i in range(int(len(dataset)/BATCH_SIZE)):
                yield dataset[i*BATCH_SIZE:(i+1)*BATCH_SIZE]

    elif DATASET == 'stacked_mnist':
        ds = Reader.DS('stacked_train.npy')
        np.save('../dataset/Stacked_MNIST/dist_info.npy', ds.labels)
        while True:
            # p = np.random.permutation(a.size)
            # dd = ds.data[p]
            # ll = ds.labels[p]
            for i in range(int(ds.size / BATCH_SIZE)):
                start = i * BATCH_SIZE
                end = (i + 1) * BATCH_SIZE
                yield ds.images[start:end], ds.labels[start:end]

    elif DATASET == '1200D':
        ds = np.load('../dataset/1200D/1200D_train.npy')
        ds = ds.item()
        ds_images = ds['images']
        ds_dist = ds['y_dist']
        means = ds['means']
        ds_size = ds_images.shape[0]
        np.save('../dataset/1200D/dist_ydist.npy', ds_dist)
        np.save('../dataset/1200D/dist_means.npy', means)
        while True:
            for i in range(int(ds_size / BATCH_SIZE)):
                start = i * BATCH_SIZE
                end = (i + 1) * BATCH_SIZE
                yield ds_images[start:end], -1


    elif DATASET == 'swissroll':
        while True:
            data = datasets.make_swiss_roll(
                n_samples=BATCH_SIZE,
                noise=0.25
            )[0]
            data = data.astype('float32')[:, [0, 2]]
            data /= 7.5 # stdev plus a little
            yield data

    elif DATASET == '8gaussians':
        scale = 2.
        centers = [
            (1,0),
            (-1,0),
            (0,1),
            (0,-1),
            (1./np.sqrt(2), 1./np.sqrt(2)),
            (1./np.sqrt(2), -1./np.sqrt(2)),
            (-1./np.sqrt(2), 1./np.sqrt(2)),
            (-1./np.sqrt(2), -1./np.sqrt(2))
        ]
        centers = [(scale*x,scale*y) for x,y in centers]
        while True:
            dataset = []
            for i in range(BATCH_SIZE):
                point = np.random.randn(2)*.02
                center = random.choice(centers)
                point[0] += center[0]
                point[1] += center[1]
                dataset.append(point)
            dataset = np.array(dataset, dtype='float32')
            dataset /= 1.414 # stdev
            yield dataset

def generate_image(N_POINTS, RANGE):
    """
    Generates and saves a plot of the true distribution, the generator, and the
    critic.
    """
    points = np.zeros((N_POINTS, N_POINTS, 2), dtype='float32')
    points[:,:,0] = np.linspace(-RANGE, RANGE, N_POINTS)[:,None]
    points[:,:,1] = np.linspace(-RANGE, RANGE, N_POINTS)[None,:]
    points = points.reshape((-1,2))
    return points

def plot(N_POINTS, RANGE, disc_map, true_dist, samples, idx, out_path):
    plt.clf()
    x = y = np.linspace(-RANGE, RANGE, N_POINTS)
    plt.contour(x,y,disc_map.reshape((len(x), len(y))).transpose())

    plt.scatter(true_dist[:, 0], true_dist[:, 1], c='orange',  marker='+')
    plt.scatter(samples[:, 0], samples[:, 1], c='green', marker='+')

    plt.savefig(out_path + '/frame'+str(idx)+'.jpg')


def save_fig_mnist(samples, out_path, idx):
    fig = plt.figure(figsize=(5, 5))
    gs = gridspec.GridSpec(5, 5)
    gs.update(wspace=0.05, hspace=0.05)

    for i, sample in enumerate(samples):
        ax = plt.subplot(gs[i])
        plt.axis('off')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        plt.imshow(sample.reshape(28, 28), cmap='Greys_r')

    plt.savefig(out_path + '/{}.png'.format(str(idx).zfill(3)), bbox_inches='tight')
    plt.close(fig)

def save_fig_color(samples, out_path, idx):
    fig = plt.figure(figsize=(5, 5))
    gs = gridspec.GridSpec(5, 5)
    gs.update(wspace=0.05, hspace=0.05)

    for i, sample in enumerate(samples):
        ax = plt.subplot(gs[i])
        plt.axis('off')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        s = sample.reshape(3, 28, 28)
        s = s.transpose(1, 2, 0)
        plt.imshow(s, cmap='Greys_r')


    plt.savefig(out_path + '/{}.png'.format(str(idx).zfill(3)), bbox_inches='tight')
    plt.close(fig)

def get_dist(p, n):
    pk = np.zeros(n)
    for x in p:
        pk[x] += 1

    _dsize = len(p)
    for i in range(n):
        pk[i] = pk[i] * 1.0 / _dsize

    return pk

def classify_dist(x, means, std=100):
    n_modes = 10
    dim_k = 700
    dim_n = 1200
    nearest_mode = -1
    min_distance = 1000000
    for i in range(n_modes):
        d = np.linalg.norm(x - means[i])
        if d < min_distance and d < 100 * std: #* np.sqrt(dim_k):
            # high quality
            min_distance = d
            nearest_mode = i

    return nearest_mode
