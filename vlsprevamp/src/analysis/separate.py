from src.config import *

def __separate(b_img: Matlike, r_img: Matlike, count:str) -> list[Matlike, Matlike]:
    """
    Separate a single image of the sky into two images,
    One of the clouds and one of the rest of the sky.
    """

    b_img = cv2.resize(b_img,(400, 300))
    r_img = cv2.resize(r_img,(400, 300))

    b_img = cv2.cvtColor(b_img, cv2.COLOR_BGR2HSV)
    r_img = cv2.cvtColor(r_img, cv2.COLOR_BGR2HSV)

    
    """
    First we make a mask for red colours
    We'll use Red to represent Clouds
    Red can have hue values between 0-10, but also 170-180
    """

    u_b_red1HSV = np.array([10, 255, 255])
    l_b_red1HSV = np.array([0, 30, 30])

    u_b_red2HSV = np.array([180, 255, 255])
    l_b_red2HSV = np.array([170, 50, 50])

    maskOneRedHSV = cv2.inRange(b_img,l_b_red1HSV,u_b_red1HSV)
    maskTwoRedHSV = cv2.inRange(b_img,l_b_red2HSV,u_b_red2HSV)

    redMask = cv2.bitwise_or(maskOneRedHSV,maskTwoRedHSV)

    """
    Now we do the same for Black.
    We'll use a range of black to represent The Sky
    """

    u_b_blackHSV = np.array([180, 255,30])
    l_b_blackHSV = np.array([0, 0, 0])

    blackMask = cv2.inRange(b_img, l_b_blackHSV, u_b_blackHSV)


    """
    Apply masks and create HSV versions of our images.
    """

    cloud_img = cv2.bitwise_and(r_img, r_img, mask = redMask)
    sky_img = cv2.bitwise_and(r_img, r_img, mask = blackMask)
    c_img = cv2.cvtColor(cloud_img, cv2.COLOR_HSV2BGR)
    s_img = cv2.cvtColor(sky_img, cv2.COLOR_HSV2BGR)

    return c_img, s_img


def separate_datasets(cam: Camera) -> None:
    """
    This iterates through colour-blocked images and separates them into two images, one sky and one cloud

    An assumption of this function is that all images are of the same size.
    As to not raise an error
    """

    if not os.path.exists(cam.blocked_images_folder):
        debug(f"Bad path: {cam.blocked_images_folder} does not exist.")
        return None

    if not os.path.exists(cam.reference_images_folder):
        debug(f"Bad path: {cam.reference_images_folder} does not exist.")
        return None

    count = 1
    for (ref_root, _, referenceImages), (blc_root, _, blockedImages) in zip(os.walk(cam.reference_images_folder), os.walk(cam.blocked_images_folder)):
        for ref, blc in zip(referenceImages, blockedImages):
            refPath = os.path.join(ref_root, ref)
            blockPath = os.path.join(blc_root, blc)
            debug(f"Block Path: {blockPath}")
            c_img, s_img = __separate(cv2.imread(blockPath), cv2.imread(refPath), count)
            cv2.imwrite(os.path.join( cam.cloud_images_folder,f"{ref}"), c_img)
            cv2.imwrite(os.path.join( cam.sky_images_folder,f"{ref}"), s_img)
            count+=1


def filesync(cam: Camera) -> bool:
    """
    Check filenames are synced.
    """

    blc = cam.blocked_images_folder
    ref = cam.reference_images_folder
    cld = cam.cloud_images_folder
    sky = cam.sky_images_folder

    if not os.path.exists(blc):
        debug(f"Bad path: {blc} does not exist.")
        return False

    if not os.path.exists(ref):
        debug(f"Bad path: {ref} does not exist.")
        return False
    
    if not os.path.exists(cld):
        debug(f"Bad path: {cld} does not exist.")
        return False
    
    if not os.path.exists(sky):
        debug(f"Bad path: {sky} does not exist.")
        return False

    for (_, _, b_imgs), (_, _, r_imgs),(_, _, c_imgs),(_, _, s_imgs) in zip (os.walk(blc),os.walk(ref),os.walk(cld),os.walk(sky)):
        for b_img, r_img, c_img, s_img in zip(b_imgs, r_imgs, c_imgs, s_imgs):
            if not (b_img == r_img == c_img == s_img):
                debug(f"Image Desync!\nRef: {r_img}\nBlocked: {b_img}\nCloud: {c_img}\nSky: {s_img}")
                return False 
    debug("Files Synced")
    return True 


if __name__ == '__main__':
    start = datetime.now()

    cam = Camera(camera_model.OV5640)
    
    separate_datasets(cam)
    synced = filesync(cam)
    if (not synced):
        debug("File Desync")
        os._exit(1)