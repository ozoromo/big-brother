
import numpy as np
import matplotlib.pyplot as plt
import pylab
import os

'''
    This package is to be used as a library. Please do not edit.
'''

def list_directory(path: str) -> list:
    """
    List subdirectories and files in path directory.

    Arguments:
    path: the path of the directory to list

    Return:
    list containing the names of the entries in the directory in ARBITRARY ORDER
    """
    return os.listdir(path)

def plot_singular_values_and_energy(sv: np.ndarray, k: int):
    """
    Plot singular values and accumulated magnitude of singular values.

    Arguments:
    sv: vector containing singular values
    k: index for threshold for magnitude of

    Side Effects:
    - Opens plotting window
    """

    en_cum = sv.cumsum()

    fig = pylab.figure(figsize=(15, 8))

    fig.add_subplot(1, 2, 2)
    plt.plot(sv)
    plt.vlines(k, 0.0, max(sv), colors='r', linestyles='solid')
    plt.xlim(0, len(sv))
    plt.ylim(0.0, max(sv))
    plt.xlabel('Index of singular value')
    plt.ylabel('Magnitude singular value')

    fig.add_subplot(1, 2, 1)
    plt.plot(en_cum)
    plt.vlines(k, 0.0, max(en_cum), colors='r', linestyles='solid')
    plt.xlim(0, len(en_cum))
    plt.ylim(0.0, max(en_cum))
    plt.ylabel('Accumulated singular values')
    plt.xlabel('Number of first singular value in accumulation.')

    plt.show()


def visualize_eigenfaces(n: int, pcs: np.ndarray, sv: np.ndarray, dim_x: int, dim_y: int):
    """
    Visualize eigenfaces.

    Arguments:
    n: number of eigenfaces to draw
    pcs: principal component matrix whose rows are the eigenfaces
    sv: singular values vector
    dim_x: x_dimension of the original images
    dim_y: y_dimension of the original images

    Side Effects:
    - Opens plotting window
    """
    fig = pylab.figure(figsize=(15, 8))
    m = int(np.ceil(n / 2))
    n = 2 * m

    for i in range(n):
        fig.add_subplot(2, m, i + 1)
        eface = pcs[i, :].reshape((dim_y, dim_x))
        plt.imshow(eface, cmap="Greys_r")
        plt.title('sigma = %.f' % sv[i])

    plt.show()


def plot_identified_faces(scores: np.ndarray, training_images: list, test_images: list, pcs: np.ndarray, coeffs_test: np.ndarray, mean_data: np.ndarray):
    # find best match, compute confidence and plot
    """
    Plot identified face and reconstructed face according to scores matrix.

    Arguments:
    scores: score matrix with correlation values between training and test images
    training_images: list of loaded training images (type: np.ndarray)
    test_images: list of loaded test images (type: np.ndarray)
    pcs: principal component matrix whose rows are the eigenfaces
    coeffs_test: the coefficients of the test images to reconstruct the with eigenfaces
    mean_data: the mean data vector to 'denormalize' the reconstructed images

    Side Effects:
    - Opens plotting window
    """
    for i in range(scores.shape[1]):
        j = np.argmin(scores[:, i])

        fig = pylab.figure()

        fig.add_subplot(1, 3, 2)
        plt.imshow(training_images[j], cmap="Greys_r")
        plt.xlabel('Identified person')

        fig.add_subplot(1, 3, 1)
        plt.imshow(test_images[i], cmap="Greys_r")
        plt.xlabel('Query image')

        img_reconst = pcs.transpose().dot(coeffs_test[i, :]) + mean_data
        try:

            img_reconst = img_reconst.reshape(test_images[i].shape)

        except ValueError:
            img_reconst = img_reconst.reshape((test_images[i].shape[0],test_images[i].shape[1]))

        """

        except ValueError:
            #img_reconst = img_reconst.reshape(test_images[i].shape)

            for row_index, row in enumerate(img_reconst):
                #c = row_index * im_s[1]
                #D[img_index][c] = img

                for val_index,val in enumerate(row):

                    data_offset = row_index * im_s[1]
                    data_index = data_offset + val_index
                    try:
                        img_reconst[img_index][data_index] = val
                    except Exception:
                        print(type(val))
                        img_reconst[img_index][data_index] = (val[0] + val[1] + val[2]) / 3
                        pass
            pass
        """



        fig.add_subplot(1, 3, 3)
        plt.imshow(img_reconst, cmap="Greys_r")
        plt.xlabel('Reconstructed image')

        plt.show()
