'''
This code downloads images from imagenet and saves them into a folder for later use
'''

import requests
import os

### PARAMS ###
# page contains a url list of images of people : from imagenet
def main():
    image_list_url = r"http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n10529231"

    # this is where we will store the images
    image_folder = "./imagenet/person"
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    # how many files do we want to download?
    n_images = 100

    ### CODE ###
    # get the list of image URLS
    response = requests.get(image_list_url)
    image_urls = response.text.replace('\r', '').split('\n')
    print("images already in folder %i" % len(os.listdir(image_folder)))

    # select n_images and download
    failed_attempts = 0
    for url in image_urls:
        # exit if too many failed attempts
        if failed_attempts > 3:
            print("too many failed attempts, exiting")
            break

        # get the image name
        name = url.split('/')[-1]

        # exit early if we have collected enough photos
        if len(os.listdir(image_folder)) >= n_images: break

        # skip files already downloaded
        if name in os.listdir(image_folder): continue

        # get image
        try:
            response = requests.get(url, stream=True)
            assert response.status_code == 200

            # save image
            save_path = os.path.join(image_folder, name)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print("Succesffully pulled image from {}".format(url))
        except:
            print("Failed to download image from {}".format(url))

    # alert done
    print("done!")
