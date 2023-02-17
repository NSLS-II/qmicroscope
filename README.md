Early stage Qt widget for monitoring cameras at NSLS-II
=======================================================

This is a simple Qt-based widget for monitoring a camera on the network, and
performing some overdrawing of the images. It is still subject to change.

It depends upon qtpy which needs PySide2 or PyQt5 in order to show anything.

This currently expects a network endpoint that offers a single JPEG file, which
it will use to download from periodically. Things like the FFMPEG plugin for the
area detector and the AXIS webcams support this. Likely soon I will add support
for the MJPEG stream that is offered by some of the cameras for more efficient
data streaming from the cameras.

Expected camera urls/endpoints:
- Endpoints that offer single JPEG files that are downloaded periodically based on frame rate
- MJPEG stream (URL must end with `mjpg` or `cgi`)

## Installation and usage
As of v0.0.2 the widget is not pip installable. 

To use clone the repo and run either of the 2 apps developed that use the widget
`python main.py` - Shows a grid of camera feeds 
`python monitor.py` - Shows a grid of camera feeds as thumnails which can be clicked to shown on the "main" camera feed. Sort of like a [Master Control](https://en.wikipedia.org/wiki/Master_control) in TV stations

## Plugins API
A number of plugins have been developed to allow each instance of the QMicroscope camera to have it's own set of features as defined by the application. Plugins defined for the two implemented apps are as follows:

### main.py
- Record plugin (alpha testing)
    - Allows user to record video feed into MJPG format

### monitor.py
#### Main camera feed
- Crosshair plugin
    - Draws a crosshair with a specific color and position
    - Option available to always center the crosshair regardless of size of image
- Grid plugin
    - Draws a grid with specified number of rows and columns
    - Options to change color, hide or show grid and selector
- Scale plugin
    - Draws a scale in the x-y direction
    - Options to change color, location, text shown on each axis and toggle visibility
- Crop plugin
    - Crop the video feed to a specific area
- Preset plugin
    - Allows settings of other plugins to be named and saved
    - Settings can be restored at any point

#### Thumbnail camera feed
- Toggle plugin
    - Adds a checkbox to the camera feed that will pause or resume the video feed

## Plugin API
Instructions to write your own plugin, coming soon (checkout the plugins folder)
