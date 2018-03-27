# Table of Contents

[TOC]

# Targets 2018/03/24

## Part I

Do some performance/accuracy testing on Haarcascades person detection

- find a bunch of photos with people in them, see how it gets it right/wrong
- find a bunch of photos without people, see how often it gets it right/wrong
- try modifying the light/contrast in the photos and repeat (try to find best lighting/contrast for later)

## Part II

Hook haarcascades up to camera and do live feed. Test how many frames it can process per second on the raspi (average over a minute or so) 

## Part III 

Create docker installation for Part II

## Part IV

Create a detect motion part. Test how many frames it can do per second on raspi. 

# Targets 2018/03/17

1. Install OpenCV 3.3 on Raspberry Pi 3 (Raspbian Stretch).
   - Setup with Camera
   - Test Object Detection
2. Test image recognition with darknet/YOLO
3. Create Docker file to automate future installations
4. Use GPU to increase performance
5. Add GPU usage to Docker file

---

Ideal ML Setup

- Docker Cluster
- Spark2 (streaming)
- [DL4J](https://deeplearning4j.org/spark-gpus) (deep learning)
- NVidia GPUs

---

Dev environment

https://www.masterzendframework.com/docker-development-environment/

---



