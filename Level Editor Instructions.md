5# Instructions to operate the level editor  
## Structure of the editor  
The Level is split into 5 different layers: Background, 
Decorations, Terrain, Entities and Starting_Position. 
Background, Decorations and Terrain alter the game map, 
Entities alters the enemies present in the game, and 
Starting_Position alters the starting position of the Player.  
  
## Loading a level  
Click on "load file" at the top left hand corner to load a 
level from a JSON file. When clicked, a pop-up window will 
prompt you to enter the filepath. By default, the first part 
of the filepath will be pre-entered, and all you have to do 
is to specify the file name.  

## Creating a level  
Click on "new file" at the top left hand corner to create a 
new empty level. When clicked, a pop-up window will prompt 
you to enter the dimensions of the map. Do note that 
the minimum dimensions are 16 by 12 (that is, 16 blocks wide 
by 12 blocks high). This limitation is not strictly enforced, 
but having maps smaller than this size will cause problems 
with the camera in the game.  

## Editing a level  
Edits can only be made to one layer at a time. Additionally, 
safeguards have been put in place to avoid the placement of 
blocks and entities in places where they should not be placed.  
  
### Layer selection  
To select a layer for editing, press a number from 1 to 5 on the 
number row.  
1 = Background  
2 = Decorations  
3 = Terrain  
4 = Entities  
5 = Starting_Position

To toggle the visibility of the layer, hold down shift while 
pressing the number. This facilitates easier editing for the user.  

### Controlling the Map  
You can move the view of the map around using the arrow keys. 
The view, however, is bound by the dimensions of the map  

### Controlling the Palette  
The left panel of the editor contains a palette of all the 
available Blocks and Enemies available. By default, the 
panel displays the list of Blocks. To scroll down to see 
more Blocks, press and hold S. To scroll up the list, press 
W.  

Pressing E will bring up the list of Enemies. Press Q again 
to go back to the list of Blocks.
### Placing Blocks/Entities on the Map  
By default, the Editor is placed in Add mode. Alternatively, 
you can press A to enter Add mode. When you click 
on the map in Add mode, the current active object will be 
placed on the current active layer, at the place where you 
clicked.  

On the left panel of the screen, click on a Block/Entity to set 
it as the current active object. When you click on the map again, 
the block at the position of your cursor will be replaced 
by the current active object. If you are placing blocks (i.e. 
your current layer is Background, Decorations or Terrain), 
the Block will automatically snap to the grid.  
  
Do note that the properties of the different types of 
blocks do not carry over - interactive objects will not stay 
interactive if they are placed in the Background or Decorations 
layer.  
  
### Deleting Blocks/Entities on the Map  
To enter Delete mode, press D. When you click on the map 
in Delete mode, the object your cursor is hovering over 
at the corresponding Layer will be deleted.  

**Important Note:** When deleting large blocks (i.e. blocks 
that are larger than the standard 1x1 blocks), the blocks 
may not be properly deleted even though they disappear 
from the screen. This is a known bug that will (hopefully) 
be addressed in future updates. The current workaround 
is to click on the block at the original place where the 
cursor is when the block is placed.  

For banners, the origin is slightly to the right of the 
top-left corner of the banner, at the area which occupies 
a full-sized block. For windows, the origin is slightly 
to the right of the bottom-left corner, also at the area 
which occupies a full-sized block.

## Saving the Level  
Click on the "save file" button at the top left of the 
editor to save the file. When clicked, a pop-up window 
will prompt you to enter the name of the file which the 
level will be saved to. The file must have a .json file 
extension, otherwise it will not be loaded by the game.

## Summary of Controls  
|Key      |Action   |
|---------|---------|
|Up       |Scrolls the map upwards|
|Down     |Scrolls the map downwards|
|Left     |Scrolls the map to the left|
|Right    |Scrolls the map to the right|
|W        |Scrolls the texture/enemy panel upwards|
|S        |Scrolls the texture/enemy panel downwards|
|Q        |Switches to the texture selection panel|
|E        |Switches to the enemy selection panel|
|A        |Switches to Add mode|
|D        |Switches to Delete mode|
|1        |Sets the Background layer as the focus|
|2        |Sets the Decorations layer as the focus|
|3        |Sets the Terrain layer as the focus|
|4        |Sets the Enemies layer as the focus|
|5        |Sets the Starting_Position layer as the focus|
|Shift + 1||
|Shift + 2||
|Shift + 3||
|Shift + 4||
|Shift + 5||


