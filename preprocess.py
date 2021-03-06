import numpy as np
from augmentation import data_augmentation


def load_data(path):

    '''read data in shapes of (height ,width, n_samples)'''

    return np.load(path)

def normalize(image):

    '''HU=(-1000,0), then normalize the data range(0,1)'''

    return (np.clip(image, -1000, 0) + 1000) / 1000


def crop_data(images, size=64):

    '''reshape images into (64, 64, n_samples*64)'''

    return images.reshape((size, images.shape[1], -1), order='F').reshape((size, size, -1))


def reshape_data(images):

    '''transform data into shapes of (n_samples*64, 64, 64, 1)'''

    return np.transpose(images, (2, 1, 0))[..., None]


def get_batches(images, size):

    '''return batches in shapes of (batches, 64, 64, 64, 1)'''

    return np.array(np.split(images, int(images.shape[0]/size), axis=0))

def get_split(data_train):

    x = int(data_train.shape[0] * 0.9)

    images_train = data_train[:x]
    images_valid = data_train[x:]

    return images_train, images_valid

# def preprocess_data(path, size=64, replica=None, split=True):
#
#     images = load_data(path)
#     images = crop_data(images, size)
#
#     if replica != None:
#         images_re = np.copy(images)
#         for i in range(1,replica):
#             images = np.concatenate((images, images_re), axis=-1)
#     else:
#         pass
#
#     images = reshape_data(images)
#     images = get_batches(images, size)
#
#     if split:
#         images_train, images_valid = get_split(images)
#
#         return images_train, images_valid
#     else:
#
#         return images

def preprocess_data_train(image_path, mask_path, size=64, replica=None, split=True):

    image = load_data(image_path)
    mask = load_data(mask_path)

    image = normalize(image)

    if replica != None:

        img_re = np.copy(image)
        msk_re = np.copy(mask)

        for i in range(1,replica):
            img_re, msk_re = data_augmentation(img_re, msk_re, size)
            image = np.concatenate((image, img_re), axis=-1)
            mask = np.concatenate((mask, msk_re), axis=-1)
    else:
        pass

    image = crop_data(image,size)
    image = reshape_data(image)
    image = get_batches(image, size)

    mask = crop_data(mask, size)
    mask = reshape_data(mask)
    mask = get_batches(mask, size)

    if split:
        image_train, image_valid = get_split(image)
        mask_train, mask_valid = get_split(mask)

        return image_train, image_valid, mask_train, mask_valid
    else:

        return image, mask


def recover(images, size):

    images = images.reshape(-1, size, size, 1)
    images = images.reshape(-1, size, size)
    images = np.transpose(images, (2,1,0))
    images = images.reshape((size, 512, -1)).reshape((512, 512, -1), order='F')

    return images

