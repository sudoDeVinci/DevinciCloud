from PIL import Image
from src.config import *
from typing import Callable
from scipy import stats

def process_RGB(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in RGB format.
    """
    red, green, blue = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < red) & (0 < green) & (0 < blue))
    non_black_data = np.column_stack((red[non_black_indices], green[non_black_indices], blue[non_black_indices]))
    return non_black_data

def process_HSV(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in HSV format.
    """
    h, s, v = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < v) & (0 < s) & (0 < h))
    non_black_data = np.column_stack((h[non_black_indices], s[non_black_indices], v[non_black_indices]))
    return non_black_data

def process_YBR(image: NDArray) -> NDArray:
    """
    Extract the non-black pixels from a colour-masked image in YcBcR format.
    """
    Y, b, r = image[:,:,0], image[:,:,1], image[:,:,2]
    non_black_indices = np.where((0 < Y))
    non_black_data = np.column_stack((Y[non_black_indices], b[non_black_indices], r[non_black_indices]))
    return non_black_data

class Colour_Tag(Enum):
    RGB = {
        'components' : ('Red', 'Green', 'Blue'),
        'tag' : 'RGB',
        'converter' : cv2.COLOR_BGR2RGB,
        'func' : process_RGB
           }
    HSV = {
        'components': ('Hue','Saturation','Value'),
        'tag' : 'HSV',
        'converter':cv2.COLOR_BGR2HSV,
        'func' : process_HSV
            }
    YCRCB = {
        'components' : ('Brightness','Chroma Red','Chroma Blue'), 
        'tag' : 'YCbCr',
        'converter' : cv2.COLOR_BGR2YCrCb,
        'func' : process_YBR
            }
    UNKNOWN = {
        'components' : None,
        'tag' : "UNKNOWN",
        'converter' : None,
        'func' : None}

    @classmethod
    @functools.lru_cache(maxsize=None)
    def match(cls, tag_str:str):
        """
        Match input string to camera model.
        """
        tag_str = tag_str.upper()
        for _, tagtype in cls.__members__.items():
            if tag_str == tagtype.value['tag'].upper(): return tagtype
        return cls.UNKNOWN


def count(xyz_sk: NDArray) -> NDArray:
    """
    Return a frequency table of the integers in an input array
    """
    unique, counts = np.unique(xyz_sk, return_counts=True)
    freq = np.asarray((unique, counts)).T
    return freq

def __is_image(name: str) -> bool:
    for filetype in IMAGE_TYPES:
        if name.endswith(f".{filetype}"): return True
    return False

def get_nonblack_all(folder_path:str, colour_tag: Colour_Tag) -> NDArray:
    """
    Iterate through the binary images of either cloud or sky. Filter through them after converting them to specified colour format via colour_index.
    default or 0: RGB, 1: HSV, 2: YCbCr
    """
    data = []
    for filename in os.listdir(folder_path):
        if not __is_image(filename): continue
    
        im = Image.open(os.path.join(folder_path, filename))
        tag = colour_tag.value['tag']

        __process = colour_tag.value['func']

        if tag != 'RGB': 
            im = im.convert(tag)
        im = np.array(im)
        non_black_data = __process(im)
            
        data.append(non_black_data)
        
    return np.vstack(data)

            
def remove_outliers_iqr(data: NDArray) -> NDArray:
    """
    Remove outliers from data using IQR.
    Data points that fall below Q1 - 1.5 IQR or above the third quartile Q3 + 1.5 IQR are outliers.
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return data[(data >= lower_bound) & (data <= upper_bound)]

def remove_outliers_z_score(data: NDArray, threshold: float = 3.0) -> NDArray:
    """
    Remove outliers from data using the Z-score method.
    Data points with a Z-score greater than the threshold will be considered as outliers.
    """
    z_scores = np.abs(stats.zscore(data))
    return data[(z_scores < threshold).all(axis=1)]

def __check_distribution(data: NDArray, label: str, significance_level: float = 0.05):
    distributions = {
        "Normal": {"func": stats.norm, "params": stats.norm.fit(data)},
        "Beta": {"func": stats.beta, "params": stats.beta.fit(data)},
        "Chi-Squared": {"func": stats.chi2, "params": stats.chi2.fit(data)}
        # Add more distributions here if needed
    }

    results = {}
    for dist_name, dist in distributions.items():
        _, p_value = stats.kstest(data, dist["func"].name, args=dist["params"])
        results[dist_name] = p_value

    # Print the results
    print(f"Distribution Test Results - {label}")
    for dist_name, p_value in results.items():
        print(f"{dist_name}: p-value = {p_value:.4f} {'<-- Good Fit' if p_value > significance_level else '<-- Poor Fit'}")

    return results

def identify_best_distribution(results):
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    print("\nDistribution ranking:")
    for i, (dist_name, p_value) in enumerate(sorted_results):
        print(f"{i+1}. {dist_name} (p-value = {p_value:.4f})")


if __name__ == "__main__":

    cam = Camera(camera_model.OV5640)

    tag:Colour_Tag = Colour_Tag.match('HSV')
    print(tag.value)

    sky = get_nonblack_all(cam.cloud_images_folder, tag)