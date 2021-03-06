import constants
import glob
import numpy as np
from util import read_vol


def crop(vol):
    if (vol.shape[0] < constants.TARGET_SHAPE[0] or
        vol.shape[1] < constants.TARGET_SHAPE[1] or
        vol.shape[2] < constants.TARGET_SHAPE[2]):
        raise ValueError('The input shape {shape} is not supported.'.format(shape=vol.shape))

    # convert to target shape
    dx = abs(constants.TARGET_SHAPE[0] - vol.shape[0]) // 2
    dy = abs(constants.TARGET_SHAPE[1] - vol.shape[1]) // 2
    dz = abs(constants.TARGET_SHAPE[2] - vol.shape[2]) // 2
    
    resized = vol[dx:-dx, dy:-dy, dz:-dz]
    if resized.shape != constants.TARGET_SHAPE:
        raise ValueError('The resized shape {shape} '
                         'does not match the target '
                         'shape {target}'.format(shape=resized.shape,
                                                 target=constants.TARGET_SHAPE))
    return resized


def scale(vol):
    return vol / constants.MAX_VALUE


PRE_FUNCTIONS = {
    'resize': crop,
    'rescale': scale,
}


def preprocess(file, funcs=['rescale', 'resize']):
    vol = read_vol(file)
    for f in funcs:
        vol = PRE_FUNCTIONS[f](vol)
    return vol


def uncrop(vol, shape):
    if vol.shape != constants.TARGET_SHAPE:
        raise ValueError('The input shape {shape} is not supported.'.format(shape=vol.shape))
    if (shape[0] < constants.TARGET_SHAPE[0] or
        shape[1] < constants.TARGET_SHAPE[1] or
        shape[2] < constants.TARGET_SHAPE[2]):
        raise ValueError('The target shape {shape} is not supported.'.format(shape=shape))

    # convert to original shape
    dx = abs(shape[0] - constants.TARGET_SHAPE[0]) // 2
    dy = abs(shape[1] - constants.TARGET_SHAPE[1]) // 2
    dz = abs(shape[2] - constants.TARGET_SHAPE[2]) // 2

    resized = np.pad(vol, ((dx, dx), (dy, dy), (dz, dz), (0, 0)), 'constant')
    if resized.shape != shape:
        raise ValueError('The resized shape {shape} '
                         'does not match the target '
                         'shape {target}'.format(shape=resized.shape,
                                                 target=shape))
    return resized
