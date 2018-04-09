import numpy as np
from image3d import ImageTransformer, VolumeIterator
from keras.utils.data_utils import Sequence
from process import preprocess
from util import shape


class AugmentGenerator(VolumeIterator):
    def __init__(self,
                 input_files,
                 label_files=None,
                 batch_size=1,
                 rotation_range=90.,
                 shift_range=0.1,
                 shear_range=0.2,
                 zoom_range=0.2,
                 fill_mode='nearest',
                 cval=0.,
                 flip=True):
        self.inputs = np.array([preprocess(file) for file in input_files])

        if label_files is not None:
            self.labels = np.array([preprocess(file, funcs=['resize']) for file in label_files])
        else:
            self.labels = None

        image_transformer = ImageTransformer(rotation_range=rotation_range,
                                             shift_range=shift_range,
                                             shear_range=shear_range,
                                             zoom_range=zoom_range,
                                             fill_mode=fill_mode,
                                             cval=cval,
                                             flip=flip)

        super().__init__(self.inputs, self.labels, image_transformer, batch_size=batch_size)


class VolSliceAugmentGenerator(AugmentGenerator):
    def _get_batches_of_transformed_samples(self, index_array):
        batch = super()._get_batches_of_transformed_samples(index_array)
        
        if self.labels is None:
            raise ValueError('No labels to generate slices.')
        batch_x, batch_y = batch
        
        new_batch_x = np.zeros(tuple(list(batch_x.shape[:-1]) + [batch_x.shape[-1] + 1]))
        for i, label in enumerate(batch_y):
            seed = np.zeros(batch_x[i].shape)
            r = np.random.choice(label.shape[0])
            while not np.any(label[r]):
                r = np.random.choice(label.shape[0])
            seed[r] = label[r]
            new_batch_x[i] = np.concatenate((batch_x[i], seed), axis=-1)
        return new_batch_x, batch_y


class VolumeGenerator(Sequence):
    def __init__(self, input_files, seed_files=None, label_files=None, batch_size=1, rescale=True):
        self.input_files = input_files
        self.seed_files = seed_files
        self.label_files = label_files
        self.shape = shape(self.input_files[0])
        self.batch_size = batch_size
        self.funcs = ['rescale', 'resize'] if rescale else ['resize']
        self.n = len(self.input_files)
        self.idx = 0

    def __len__(self):
        return (self.n + self.batch_size - 1) // self.batch_size

    def __getitem__(self, idx):
        batch = []
        for file in self.input_files[self.batch_size * idx:self.batch_size * (idx + 1)]:
            volume = preprocess(file, self.funcs)
            batch.append(volume)
        batch = np.array(batch)

        if self.seed_files is not None:
            seeds = []
            for file in self.seed_files[self.batch_size * idx:self.batch_size * (idx + 1)]:
                seed = preprocess(file, ['resize'])
                seeds.append(seed)
            batch = np.concatenate((batch, np.array(seeds)), axis=-1)

        if self.label_files is not None:
            labels = []
            for file in self.label_files[self.batch_size * idx:self.batch_size * (idx + 1)]:
                label = preprocess(file, ['resize'])
                labels.append(label)
            labels = np.array(labels)
            return (batch, labels)
        
        return batch

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.idx < len(self):
            batch = self[self.idx]
            self.idx += 1
            return batch
        else:
            raise StopIteration()

class VolSliceGenerator(VolumeGenerator):
    def __init__(self,
                 input_files,
                 seed_files=None,
                 label_files=None,
                 batch_size=1,
                 include_labels=True,
                 rescale=True):
        self.include_labels = include_labels
        super().__init__(input_files, seed_files, label_files, batch_size, rescale)

    def __getitem__(self, idx):
        if self.label_files is None:
            raise ValueError('No labels to generate slices.')
        if self.seed_files is not None:
            raise ValueError('Seeds already exist.')

        batch_x, batch_y = super().__getitem__(idx)

        new_batch_x = np.zeros(tuple(list(batch_x.shape[:-1]) + [batch_x.shape[-1] + 1]))
        for i, label in enumerate(batch_y):
            seed = np.zeros(batch_x[i].shape)
            r = np.random.choice(label.shape[0])
            while not np.any(label[r]):
                r = np.random.choice(label.shape[0])
            seed[r] = label[r]
            new_batch_x[i] = np.concatenate((batch_x[i], seed), axis=-1)
        return (new_batch_x, batch_y) if self.include_labels else new_batch_x
