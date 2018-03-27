'''
This code downloads images from imagenet 
'''

import requests
import os
import shutil

### PARAMS ###
# page contains a url list of images of people : from imagenet
image_list_url = r"http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n10529231"

# this is where we will store the images
image_folder = "/data/images"
assert os.path.exists(image_folder), "Image folder does not exist. Make sure {} is created".format(image_folder)

# how many files do we want to download?
n_images = 10

### CODE ### 
# get the list of image URLS
response = requests.get(image_list_url)
image_urls = response.text.replace('\r', '').split('\n')

print("images already in folder %i" % len(os.listdir(image_folder))) 

# select n_images and download
failed_attempts = 0
for url in image_urls:
  # exit early if we have collected enough photos
  if len(os.listdir(image_folder)) >= n_images: break

  if failed_attempts > 3:
    print("too many failed attempts, exiting")
    break

  # download image. This method of downloading was described here:
  # 
  try:
    name = url.split('/')[-1]
    response = requests.get(url, stream=True)
    save_path = os.path.join(image_folder, name)
    with open(save_path, 'wb') as f:
      for chunk in response.iter_content(1024):
        f.write(chunk)
    print("Succesffully pulled image from {}".format(url))
  except:
    failed_attempts += 1
    print("Failed to download image from {}".format(url))

# alert done
print("done!")
