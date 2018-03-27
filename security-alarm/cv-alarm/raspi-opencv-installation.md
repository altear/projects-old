# Table of Contents

[TOC]

# Installing OpenCV on Raspberry Pi 3 Manually

Notes:

- `make -j4` may cause freezing, `make -j1` is safest

---

1. Install the latest Raspberry Pi Lite OS. Current `Raspbian Stretch-Lite`

2. First, expand the root file system

   ```
   sudo raspi-config --expand-rootfs
   sudo reboot now
   ```

3. Run updates and upgrades

   ```
   sudo apt-get update -y && sudo apt-get upgrade -y
   sudo reboot now
   ```

4. Install tmux in order to separate the following steps from the current install. Install git to well, install other things.

   ```
   sudo apt-get install -y tmux git 
   new -s opencv_installation
   ```

5. Install CMake to configure opencv options

   ```
   sudo apt-get install -y build-essential cmake pkg-config
   ```

6. Download standard ffmpeg for converting and streaming audio/video [source](https://gist.github.com/jbienkowski311/ce12c83672fc7c519ed8586832145eb0). 

   - edit: `--enable-x11grab` option was deprecated in favor of `--enable-libxcb` [ref]

   - edit 2: to avoid `ERROR: libmp3lame >= 3.98.3 not found` we make a few more edits

     ​

   ```
   # ffmpeg dependencies
   sudo apt-get install -y libjack-jackd2-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libsdl1.2-dev libtheora-dev libva-dev libvdpau-dev libvorbis-dev libx11-dev libxfixes-dev libxvidcore-dev texi2html yasm zlib1g-dev libsdl1.2-dev libvpx-dev

   # extra codecs
   sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev v4l-utils
   sudo apt-get install -y libxvidcore-dev libx264-dev x264
   sudo apt-get install -y lyasm ibvpx-dev libx264-dev

   # get Lame dependency
   wget http://downloads.sourceforge.net/project/lame/lame/3.99/lame-3.99.5.tar.gz
   tar -xzf lame-3.99.5.tar.gz
   cd lame-3.99.5
   ./configure --enable-static --enable-shared
   make
   sudo make install  

   git clone https://github.com/FFmpeg/FFmpeg.git
   cd ~/FFmpeg/

   # edit 1
   # source: https://stackoverflow.com/questions/35937403/error-libmp3lame-3-98-3-not-found/46756012#46756012
   sed -i -e 's/\(3.98.3..lame.lame.h.lame.set.VBR.quality..lmp3lame\)/\1 -lm/' ./configure

   # try remsuming hereldsu
   # build ffmpeg
   # edit 2: https://github.com/google/ExoPlayer/issues/3117
   # edit 3: http://note.yangyang.cloud/blog/2017/10/24/solved-ffmpeg-build-libmp3lame-not-found/
   # edit 4: https://ffmpeg.org/pipermail/ffmpeg-user/2013-July/015979.html
   # edit 5: https://stackoverflow.com/questions/25079145/how-to-resolve-error-libx264-not-found/34137763#34137763
   ./configure --extra-cflags="/usr/local/include" --extra-libs="-lpthread -lm -ldl" --enable-gpl --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libxvid --enable-nonfree --enable-postproc --enable-version3 --enable-libxcb --enable-shared --enable-libvpx --enable-pic --enable-decoder=mp3 --disable-opencl
   make 
   sudo make install .
   sudo ldconfig -v
   ```

7. Download image I/O (ffmpeg seems to auto-install these, so may not be necessary)

   ```
   sudo apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
   ```

8. Download video I/O

   ```
   sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
   sudo apt-get install -y libxvidcore-dev libx264-dev
   ```

9. Install libraries that optimize opencv matrix operations

   ```
   sudo apt-get install -y libatlas-base-dev gfortran
   ```

10. Pull latest working version of opencv and opencv_contrib (working versions may take some guess work, and you may only find out after hours of frustration)

   ```
   opencv_version=3.3.0
   wget -O opencv.zip https://github.com/opencv/opencv/archive/$opencv_version.zip
   wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/$opencv_version.zip
   unzip opencv
   unzip opencv_contrib
   rm opencv*.zip

   ```

11. Python related setup blurb

    ```
    # get python 3.x
    sudo apt-get install -y python3-dev 

    # get pip 
    wget https://bootstrap.pypa.io/get-pip.py
    sudo python3 get-pip.py
    rm get-pip.py

    # get virtual env
    sudo pip3 install virtualenv virtualenvwrapper

    # add to source
    if $(grep --quiet "virtualenv and virtualenvwrapper" ~/.profile);
    then
    	echo "Virtual env already in place"
    else 
    	echo -e "\n# virtualenv and virtualenvwrapper" >> ~/.profile
    	echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.profile
    	echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.profile
    	echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.profile
    	echo "Added virtual env!"
    fi
    source ~/.profile

    # make cv virtual env
    mkvirtualenv cv -p python3
    workon cv

    # download numpy, takes about 10min
    # NOTE: sudo pip will install outside of virtual env
    pip install numpy
    ```

12. Cmake

    Note: OpenCL does not seem to work on the raspi. 

    ```
    opencv_version=3.4.0
    cd ~/opencv-$opencv_version/
    mkdir build
    cd build
    cmake \
    	-D CMAKE_BUILD_TYPE=RELEASE \
    	-D BUILD_opencv_python2=OFF \
        -D BUILD_opencv_python3=ON \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        -D INSTALL_PYTHON_EXAMPLES=ON \
        -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-$opencv_version/modules \
        -D INSTALL_C_EXAMPLES=OFF \
        -D BUILD_EXAMPLES=ON ..
    ```
    A note on selecting options, after you run cmake you can read the options and their values with the following:

    ```
    cmake ..
    cmake -L | awk '{if(f)print} /-- Cache values/{f=1}'
    ```

13. [Optional] Is using `make -j` - increase swap space, otherwise using `make -j4` may run out of space. 

    ```
    # increase swap space
    sudo sed -i 's/CONF_SWAPSIZE=100/# CONF_SWAPSIZE=100\nCONF_SWAPSIZE=1024/' /etc/dphys-swapfile

    # restart swap file
    sudo /etc/init.d/dphys-swapfile stop
    sudo /etc/init.d/dphys-swapfile start
    ```

14. Start compilation  (est: 1h30m)

    ```
    sudo make -j4
    ```

15. Install and ld

    ```
    sudo make install
    sudo ldconfig
    ```

16. Export python path
   ```
    if $(grep --quiet "\/usr\/local\/lib\/python3\.5\/site\-packages" ~/.profile);
    then
    	echo "Python path already setup"
    else 
    	echo export PYTHONPATH=/usr/local/lib/python3.5/site-packages:$PYTHONPATH >> ~/.profile
    	echo >> ~/.profile
    fi
    source ~/.profile

   ```

    ​


Additional Sources

- [rpi easy install](https://gist.github.com/jbienkowski311/ce12c83672fc7c519ed8586832145eb0)
- [opencv 3 on raspbian stretch](https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/)


# OpenCL on VideoCode IV

1. Download [VC4CLStdLib](https://github.com/doe300/VC4CLStdLib)
   ```
   # clone from git
   sudo apt-get install -y git
   git clone https://github.com/doe300/VC4CLStdLib

   # clean any existing builds
   cd ~/VC4CLStdLib
   git clean -fdx .

   # build 
   mkdir ~/VC4CLStdLib/build && cd ~/VC4CLStdLib/build
   cmake ..
   make -j1 # can do make j4, but j1 is safest
   sudo ldconfig -v
   ```



2. Download dependencies for VC4C (llvm and clang) and [VC4C](https://github.com/doe300/VC4C)

   ```
   # llvm dependency for compiling 
   #sudo apt-get install llvm

   # download llvm and clang
   cd ~
   git clone -b khronos/spirv-3.6.1 https://github.com/KhronosGroup/SPIRV-LLVM.git llvm
   cd llvm/tools
   git clone -b spirv-1.0 https://github.com/KhronosGroup/SPIR clang

   # build llvm and clang
   mkdir ~/llvm/build && cd ~/llvm/build
   cmake ..
   make -j4
   sudo ldconfig -v

   # get VC4C
   git clone https://github.com/doe300/VC4C
   cd ~/VC4C
   git clean -fdx .

   # clean VC4C
   git clone https://github.com/doe300/VC4C
   cd ~/VC4C
   git clean -fdx .

   # build VC4C
   mkdir ~/VC4C/build && cd ~/VC4C/build
   cmake ..
   make -j4
   sudo ldconfig -v
   ```


3. Download VC4CL

   ```
   # get VC4CL
   git clone https://github.com/doe300/VC4CL
   cd ~/VC4CL
   git clean -fdx .

   # clean VC4C
   git clone https://github.com/doe300/VC4CL
   cd ~/VC4CL
   git clean -fdx .

   mkdir ~/VC4CL/build && cd ~/VC4CL/build
   cmake ..
   make -j4
   sudo ldconfig -v

   cd ~/VC4C
   git clean -fdx .

   mkdir ~/VC4CL/build && cd ~/VC4CL/build
   cmake ..
   make -j4
   ```

Next get the 


    # llvm dependency for compiling 
    #sudo apt-get install llvm
    git clone -b khronos/spirv-3.6.1 https://github.com/KhronosGroup/SPIRV-LLVM.git llvm
    cd llvm/tools
    git clone -b spirv-1.0 https://github.com/KhronosGroup/SPIR clang
    
    git clone https://github.com/doe300/VC4C
    cd ~/VC4C
    git clean -fdx .
    
    mkdir ~/VC4C/build && cd ~/VC4C/build
    cmake ..
    make -j4
    
    git clone https://github.com/doe300/VC4CL



