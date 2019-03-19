# Blender add-on to assign shape keys<br>
This add-on lets you assign one or more Bezier curve(s) as shape keys to other curve<br>
Supported Blender version: 2.8 beta <br>
Script File: assignshapekey_2_8.py <br>

# Installation
- Download assignshapekey_2_8.py
- In Blender select File->User Preferences
- Click install Add-ons tab and then Install Add-on from File
- Select the downloaded file
- Check the 'Assign Shape Keys' option in the add-ons dialog <br>
  
After installation, a new 'Assign Shape Keys' panel shows up in 'Active Tool and Workspace settings' tab when application is in object mode. <br><br>

# Quick start
Select the target and shape key Bezier curve objects. Make sure the target is the active object; you can do this by right-clicking the target curve while holding the shift key after the other selections are made. Go to the 'Assign Shape Keys' tab and click 'Assign Shape Keys' button. Now a copy of the active object curve will be created, which will have the other selected curves as its target. If the 'Remove Original Objects' option is checked, the selected curve objects will be deleted and only the target is kept. <br><br>
There are a number of option to align the closed (cyclic spline) target and shape-key curves. Also it's possible to match individual parts from a multi-part (multi-spline) of target and shape key curves (e.g. text object converted to curve) based on various criteria.<br><br>
For smoother transition, you can subdivide the segments of one of the curves in the selection group.<br><br>

<b><a href= https://youtu.be/1pDd_GgsfSM> This video</a> provides a detailed overview of the add-on functionality and various options available.<br><br></b>

# Limitations
Exercise caution when using this add-on in production as it's in beta stage<br>
Keep watching this space, as there will be enhancements and bug-fixes included in future.<br>

# License
<a href=https://github.com/Shriinivas/assignshapekey/blob/master/LICENSE>MIT</a>
