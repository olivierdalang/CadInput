# CadInput

CadInput is an _EXPERIMENTAL_ [QGIS](http://www.qgis.org) [Python](http://www.python.org) plugin that allows to numerically constrain the cursor.

It allows for efficient and flexible numeric digitizing, as possible in CAD packages (it is heavily inspired by archicad's input).

One main benefit is that it works with all editing tools.

## Technical notes

The plugin relies on several hacks to work, since the current QGIS API does not allow to hook into MapCanvas mouse events nor to input numerical coordinates to tools (please tell me if I'm wrong).

### MapCanvas mouseEvents hacks

To be able to capture the mouseEvents of the MapCanvas, the plugin adds a QWidget as child of the mapCanvas.
That QWidget will recieve all mouseEvents, process them (constraining cursor position), and finally send them to the mapCanvas.

### Tools numeric input

Capture the mouseEvents is fine for graphical feedback, but does not allow for precise input (since mouseEvents are in pixels, and not in map units).
To workaround this limitation, the plugin creates a memory layer, in which a point is created each time a precise coordinate input is needed, to which the native tool will snap.
A main drawback for this workaround is the presence of that technical layer in the list as well as possible interferences from regular layers with enabled settings.

### What API improvements would help improve the plugin ? 

## How to use

How to use...

## Feedback / Bzgs

Feedback...

## Changelog

Changelog...

## Contribute

Contribute...

## Note for developpers

Notes...