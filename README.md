![Demo](https://github.com/Shriinivas/etc/blob/master/assignshapekey/illustrations/assigndemo.gif)
# Blender add-on to assign shape keys<br>
This add-on lets you assign one or more Bezier curve(s) as shape keys to other curve<br><br>
Available in Blender version: <b>2.8<br></b>

# Installation
The add-on is available as part of the standard add-on repository of Blender 2.8. You just need to enable the add-on from the add-ons dialog.
  
After enabling the add-on, a new 'Assign Shape Keys' panel shows up in 'Active Tool and Workspace settings' tab when application is in object mode. <br><br>

# Quick start
Select the target and shape key Bezier curve objects. Make sure the target is the active object; you can do this by right-clicking the target curve while holding the shift key after the other selections are made. Go to the 'Assign Shape Keys' tab and click 'Assign Shape Keys' button. Now a copy of the active object curve will be created, which will have the other selected curves as its target. If the 'Remove Original Objects' option is checked, the selected curve objects will be deleted and only the target is kept. <br><br>
There are a number of option to align the closed (cyclic spline) target and shape-key curves. Also it's possible to match individual parts from a multi-part (multi-spline) of target and shape key curves (e.g. text object converted to curve) based on various criteria.<br><br>
![Demo](https://github.com/Shriinivas/etc/blob/master/assignshapekey/illustrations/assigndemo2.gif)

For smoother transition, you can subdivide the segments of one of the curves in the selection group.<br><br>

# Manual Alignment of Starting Vertices
In the edit mode the Assign Shape Keys panel shows a single button - Mark Starting Vertices. When Clicked, all the starting vertices of the closed splines (disconnected parts) of the selected curves are indicated by a marking point. Now if the user selects any vertex, the marker moves to this selected vertex, indicating the new starting vertex. You need to confirm the new positions by pressing enter. Pressing escape, reverts the positions to the earlier order.<br>
![Demo](https://github.com/Shriinivas/etc/blob/master/assignshapekey/illustrations/assigndemo3.gif)

Change of vertex order being a change in topology, this operation will distort the existing shape keys. (See the usage example for a fix.)

<b><a href=https://youtu.be/1pDd_GgsfSM> This video</a> provides a detailed overview of the add-on functionality and various options available.<br>
Manual vertex alignment is explained in more detail in <a href=https://youtu.be/z-H_T2GszvM>this video.</a> (the marker spheres are now replaced with marker points [of fixed size] and so the marker size change feature is removed from the latest version) <br>
And you will find a usage example with practical application of the tool (retaining shape key after change in topology) in <a href=https://youtu.be/Gt2C2Hlh8Sk>this video.</a> Finally the tutorial on creating a font morphing animation using this addon is <a href='https://youtu.be/2OwfAJhpz7Q'>here</a>.<br><br>
</b>

# Limitations
All vertex handle types are changed to FREE to make the shape key vertex mapping possible.<br>
Exercise caution when using this add-on in production as it's in beta stage<br>
Keep watching this space, as there will be enhancements and bug-fixes included in future.<br>

# License
<a href=https://github.com/Shriinivas/assignshapekey/blob/master/LICENSE>MIT</a>
