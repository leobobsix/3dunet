import numpy as np
from scipy.ndimage import gaussian_filter
from augmentation import data_augmentation


def load_data(path):

    '''read data in shapes of (height ,width, n_samples)'''

    return np.load(path)

def normalize(image):

    '''HU=(-1000,0), then normalize the data range(0,1)'''

    return (np.clip(image, -1000, 0) + 1000) / 1000


def smooth(image, size):

    '''gaussian filter'''

    for i in range(0, image.shape[2], size):

        sigma = np.random.uniform(0.6, 1.3)
        end = min(image.shape[2], i+size)
        image[:,:,i:end] = gaussian_filter(image[:,:,i:end], sigma=sigma)

    return image


def crop_data(images, size=64):

    '''reshape images into (64, 64, n_samples*64)'''

    keep_z = int(images.shape[-1]/size)*size
    img = images[:64,:64,:1]

    for i in range(0,images.shape[0],size):
        for j in range(0,images.shape[1],size):
            img = np.concatenate((img, images[i:i+size,j:j+size,:keep_z]),axis=-1)

    return img


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

def valid_data(image_path, mask_path, size=64):

    image = load_data(image_path)
    mask = load_data(mask_path)

    image = smooth(image, size)
    image = normalize(image)

    image = crop_data(image,size)
    image = reshape_data(image)
    image = get_batches(image, size)

    mask = crop_data(mask, size)
    mask = reshape_data(mask)
    mask = get_batches(mask, size)

    return image, mask

def preprocess_data_train(image_path, mask_path, size=64, replica=None):

    image = load_data(image_path)
    mask = load_data(mask_path)

    image = smooth(image, size)
    image = normalize(image)

    img, msk = data_augmentation(image, mask, size)

    if replica:

        for i in range(replica):

            img_re = np.copy(image)
            msk_re = np.copy(mask)

            img_re, msk_re = data_augmentation(img_re, msk_re, size)
            img = np.concatenate((img, img_re), axis=-1)
            msk = np.concatenate((msk, msk_re), axis=-1)

    else:

        pass

    image = crop_data(img,size)
    image = reshape_data(image)
    image = get_batches(image, size)

    mask = crop_data(msk, size)
    mask = reshape_data(mask)
    mask = get_batches(mask, size)


    np.save('./preprocessed_image.npy', image)
    np.save('./preprocessed_mask.npy', mask)


def recover(images, size):

    images = images.reshape(-1, size, size, 1)
    images = images.reshape(-1, size, size)
    images = np.transpose(images, (2,1,0))
    images = images.reshape((size, 512, -1)).reshape((512, 512, -1), order='F')

    return images

