# Opencv Docker Image Base

This is a base image to use for other docker files. It contains:

- OpenCV 3.2
- Python 3.5 
  - numpy 
  - pil

# Usage

To use the image, one can load it with `docker load` ([docs](https://docs.docker.com/engine/reference/commandline/save/))

```
docker load < myimg.tar
# or
docker load --input myimg.tar
```

And then include it in a new `Dockerfile` by adding this line to the start:

```
FROM myimg
...
CMD echo "hello world"
```



