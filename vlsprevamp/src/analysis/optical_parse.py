from src.analysis.extract import Colour_Tag, Matlike, NamedTuple, np, ChannelBound, get_nonblack_all, count, remove_outliers_iqr
from src.config import *

"""
The idea is such:
1. Test colour channels for best usage based on distance between the two distributions.
"""


# Taking a matrix of size 5 as the kernel 
KERNEL = np.ones((5, 5), np.uint8) 

def __colourspace_similarity_test(cam: Camera, colours: List[Colour_Tag]) -> None:
    result = {ctag.value['tag']: {
                        ctag.value['components'][0]: None,
                        ctag.value['components'][1]: None,
                        ctag.value['components'][2]: None
                            } for ctag in colours}

    for tag in colours:
        cloud = get_nonblack_all(cam.cloud_images_folder, tag)
        sky = get_nonblack_all(cam.sky_images_folder, tag)

        data_cloud = remove_outliers_iqr(cloud)
        data_sky = remove_outliers_iqr(sky)

        #del cloud, sky
        
        x_cloud_freq = count(np.array(data_cloud[:, 0]))
        y_cloud_freq = count(np.array(data_cloud[:, 1]))
        z_cloud_freq = count(np.array(data_cloud[:, 2]))

        #del data_cloud
        
        x_sky_freq = count(np.array(data_sky[:, 0]))
        y_sky_freq = count(np.array(data_sky[:, 1]))
        z_sky_freq = count(np.array(data_sky[:, 2]))
        
        #del data_sky

        x_cloud_set = set(x_cloud_freq[:, 0])
        y_cloud_set = set(y_cloud_freq[:, 0])
        z_cloud_set = set(z_cloud_freq[:, 0])

        x_sky_set = set(x_sky_freq[:, 0])
        y_sky_set = set(y_sky_freq[:, 0])
        z_sky_set = set(z_sky_freq[:, 0])

        # Calculate Jaccard similarity for each component
        x_similarity = __jaccard(x_cloud_set, x_sky_set)
        y_similarity = __jaccard(y_cloud_set, y_sky_set)
        z_similarity = __jaccard(z_cloud_set, z_sky_set)

        tag = tag.value
        result[tag['tag']][tag['components'][0]] = x_similarity
        result[tag['tag']][tag['components'][1]] = y_similarity
        result[tag['tag']][tag['components'][2]] = z_similarity
    
    return result


def __jaccard(array1: NDArray, array2: NDArray) -> float:
    """
    We want to quantify the distance between two frequency distributions.
    We do this via the Jaccard similarity index.
    """
    set1 = set(array1)
    set2 = set(array2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union



def generate_mask(image: Matlike, bounds: List[ChannelBound]) -> Matlike:
    """
    Given an image and a number of channel boundaries, generate a composite mask.
    """
    masks: Tuple[Matlike] = tuple(cv2.inRange(cv2.cvtColor(image, bound.tag['converter'], bound.lower_bound, bound.upper_bound))
                  for bound in bounds)

    fullmask = masks[0]
    if len(masks > 1):
        for i in range(1, len(masks)):
            fullmask = cv2.bitwise_and(masks[i], fullmask)

    # fullmask = cv2.erode(fullmask, KERNEL, iterations = 2)
    # fullmask = cv2.dilate(fullmask, KERNEL, iterations = 3)
    return cv2.bitwise_and(image, image, mask=fullmask)


if __name__ == "__main__":
    tag = Colour_Tag.YCRCB
    cam = Camera(camera_model.OV5640)

    result = __colourspace_similarity_test(cam, [Colour_Tag.HSV, Colour_Tag.YCRCB, Colour_Tag.RGB])
    for cspace in result:
        debug(result[cspace])