# Build
Build the image. Run from inside this directory

```
sudo docker build -t frontend-dev .
```

# RUN
Mount the src directory for the frontend
Setup port 8080

```
sudo docker run -p 8080:8080 --name frontend-dev --mount type=bind,source=~/src/frontend,target=~/frontend-source .
```
