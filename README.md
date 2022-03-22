<img src="https://github.com/outlander1701/BuoyCV/blob/main/buoy_image_crop_add_circ.png?raw=true" style="center">

# BuoyCV
## Table of Contents
* [Goal](#goal)
* [License](#license)
* [How it Works](#how-it-works)
  * [TLDR;](#tldr)
  * [Pre-Processing](#pre-processing)
  * [Masking](#masking)
  * [Blob Detection Filters](#blob-detection-filters)
  * [Extracting Keypoint Data](#extracting-keypoint-data)
* [Thank Yous](thank-yous)
* [Suggestions and Future Plans](#suggestions-and-future-plans)

## Goal
The goal of this repository is to create an easy to implement detection algorithm for colored buoys. Ultimately, the algorithm detects the location of the buoys in the frame and reports their size (a stand in for distance if the buoys are all of one size) and the angle of buoy from the camera based upon the bottom center of the frame. The main constraints for this project were to have the algorithm run quickly on a Raspberry Pi 4B that is also running other various interfacing operations. If more computing resources where available and updated data was not needed at an accelerated rate, a pair of two cameras would be used to better determine depth.

## License
All code in this repository is under the GNU General Public License v3.0. If you are unfamiliar with this license, here is part of the [GNU GPLv3 Quick Guide](https://www.gnu.org/licenses/quick-guide-gplv3.html) to give you an idea:

>Nobody should be restricted by the software they use. There are four freedoms that every user should have:
>* the freedom to use the software for any purpose,
>* the freedom to change the software to suit your needs,
>* the freedom to share the software with your friends and neighbors, and
>* the freedom to share the changes you make.

If you would like to learn more about GPLv3 please see the [license text](https://github.com/outlander1701/BuoyCV/blob/main/LICENSE) and the [FAQ](https://www.gnu.org/licenses/gpl-faq.html).

## How it Works
### TLDR;

Ultimately, this algorithm works by doing the following:
1. Taking a frame from a video
2. Pre-processing the video
3. Pulling parts out of the image from a certain color range
4. Filtering the objects reported in that color range
5. Returning data about those objects

### Pre-Processing
After capturing the frame, we want to process it in order to do the following:
1. Decrease its size (This decreases the amount of work the Raspberry Pi will need to do in later steps)
2. Change to the HSV color space

When thinking of an image, if we want to perform an operation such as pulling a region with a certain color out of an image, we need to find a trade off between the image resolution and the amount of accuracy we need. In my use case, we do not need too much accuracy, just a general sense of if you are driving a boat between to buoys and making sure that you are not about to hit one either. Feel free to play around with the scaling factor to get it to work as it suits you. This is called as part of the main function.

Now some of you might be asking what the HSV color format is and why should I care? Many of you are probably familiar with the RGB color format where you have a combination of values ranging from 0 to 255 for Red, Green, and Blue, respectively. This is all well and good, but we run into an issue when we want to try and catagorize something as "Blue" or "Green." While it might seem like a question from a questionable psychology professor or a physics professor trying to pull a "Gotcha Moment" on the class, we have to ask: what makes something blue? Well, in computer vision land, we can just loock at what the computer reports the color as and work from there. Sadly RGB (or BGR as OpenCV natively processes) is not the greatest for this since it is hard to measure the blueness of something. That's where HSV comes in. HSV stands for Hue Saturated Value. The following image by [Jacob Rus](https://commons.wikimedia.org/wiki/User:Jacobolus) on [Wikipedia](https://en.wikipedia.org/wiki/HSL_and_HSV) should help:


<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/HSV_color_solid_cone_chroma_gray.png/1024px-HSV_color_solid_cone_chroma_gray.png" align="center" height="500">

From this, we can say a given degree range of the Hue as well as percentages of the chroma and value that we can say are within a "Blue" range!

### Masking
This step is very important, but quite simple. Simply what needs to be done is we iterate through an array that stores our image data and if there is a pixel that has a HSV value that we like, we give that pixel a value of white (0, 0, 100). Otherwise it gets a value of black (0, 0, 0). For better compatibility with OpenCV's SimpleBlobDetection, we are going to negate the array to invert it so the blobs now appear as black.

### Blob Detection Filters
In my case, I want to detect rectangular objects. These will be used as an example in this section. 

The first filter to look at is threshold reporting. Simply, you do not want the program to record a blob if it doesn't think that there is a very high chance that it is actually a blob. You can make alterations with the followinf code:

```python
#Thresholds for reporting
params.minThreshold = 50
params.maxThreshold = 1000 #This is mostly unnecessary, but a nice to have just in case 
```

The second filter is area. Mainly, you want to filter out any little flickers of some color that come about. Recall, that you are looking for buoys of a decent size, so you can do a decent amount of filtering with the lower reporting threshold for area to remove these.

```python
#Area filtering. Make sure that the areas are of a reasonable size
params.filterByArea = True
params.minArea = 50
params.maxArea = 1000
```

The third filter is for circularity. This is a measure of how circular something is. Here is the equation:

<img src="https://latex2png.com/pngs/6d94027306e45d640052736356cfe723.png" height="35"> <img src="https://latex2png.com/pngs/9afbb0ddb4b5581be505d3c329fde86c.png" height="35"> 

Now in the case of my rectangle, it would be the following:

<img src="https://latex2png.com/pngs/886e264df75176086f7e89f54a404906.png" height="35"> <img src="https://latex2png.com/pngs/82f252567799bc964357b0b8af79ed3f.png" height="35">

From here, I would simply need to enter the dimensions of the cross-sectional area of the buoy that I was looking for and I can now filter for circularity! Personally, I like to add a 20% tolerance. In my case the red targets were of a different size than the others. If you would like to do some some filtering with this, please feel free.

```python
#Circularity
"""
f = (4 * np.pi * w * h) / (2 * w + 2 * h) ** 2
  = 0.78 +- 0.16 (20% tolerance) => [0.62, 0.93] (Blue/Yellow)
  = 0.65 +- 0.13 (20% tolerance) => [0.52, 0.78] (Red)
"""
params.filterByCircularity = True
if (color == "red" or color == "Red"):
    params.minCircularity = 0.52 #Red: 0.52, Blue/Yellow: 0.62
    params.maxCircularity = 0.78 #Red: 0.78, Blue/Yello: 0.93
else:
    params.minCircularity = 0.62 #Red: 0.52, Blue/Yellow: 0.62
    params.maxCircularity = 0.93 #Red: 0.78, Blue/Yellow: 0.93
```

### Extracting Keypoint Data
From this point we just need to extract the data from the detector. In this case, we want to access the size data and the position data from this we can use the size as a pseudo-depth camera. Think of it like this, seeing stuff in 2D is pretty hard to accurately judge distance if looking at a still frame. However, since we are moving, we can look at the relative change in the size as we move closer and further away. I apologize if some of you don't get this reference, but think of the video game Doom. The developers of this game cheated in a way to make a 2D game appear 3D. Allof the enemies in the game are 2D sprites that always face you and have no shadows. While it would be hard to identify exactly how far away the enemy is, you know their 'real' size when they are closer and you can notice that they are getting larger as you get closer to them, hence, you are getting closer to them. The same principal is being used in this case. Finally, we extract the position data to determine where on the screen, turning-wise, the buoy is.

## Thank Yous
Thank you to the creators of the OpenCV Docs for the great documentation and example code that was modified to achieve these results. Additionally, the script blob.py from the following [repository](https://github.com/makelove/OpenCV-Python-Tutorial/blob/master/ch25-%E6%96%91%E7%82%B9%E6%A3%80%E6%B5%8B/blob.py) was used as a reference to fill some of the holes in the OpenCV documentation. I would like to thank the author of this repository for sharing their knowledge and making their script open source.

## Suggestions and Future Plans
I hope this script and explanation is helpful to you. If you have issues with the script or would like to leave a suggestion please feel free to open an [Issue](https://github.com/outlander1701/BuoyCV/issues). I hope you have a great day!

Future Plans:
* Add a quick start guide
* Add a Unity Simulation/Game

-outlander1701





