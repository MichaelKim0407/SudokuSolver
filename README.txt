SudokuSolver in Python
Author: MichaelKim0407 <jinzheng19930407@sina.com>

--- HOW TO SOLVE A SUDOKU PUZZLE ---
1. Terminology
a) A 'tile' is a single cell in the puzzle where a number can be filled.
b) A 'block' is a 3x3 cell in which nine numbers are required to be different from each other.
c) A 'house' is either a row, a column, or a block. The nine numbers in a house should be different from each other.
d) An 'intersection' is the shared tiles of two houses, one of which is a block, and the other is a row or a column. An intersection is either 1x3 or 3x1.
e) When talking about two intersecting houses, 'unique tiles' are the tiles in a house except the intersection.

2. Methods
a) Each tile belongs to three houses, and any number that has already been used in these three houses cannot be used in this tile. This can considerably reduce the number of possibilities for what can be filled in this tile. If eight different numbers are found in these three houses, we can immediately fill this tile with the remaining number.
b) In each house, sometimes a number or a group of numbers can only appear in one or several tiles. Example:
A house contains three unfilled tiles, two of them can be <1> or <2>, and the third one can be <1>, <2> or <3>. We then know that the third one must be <3> because it cannot appear anywhere else in the house.
    **A******
    456
    789
    3**
    *
    *
    *3*
    *
    *
c) In two intersecting houses, the three numbers in the intersection are used in both houses, so the six numbers in unique tiles are also the same. Thus, if a number cannot appear in the unique tiles of one house, it must not appear in the unique tiles in the other house either. Example:
    12****346
    *********
    34*****89
    **5******
    *
    *
    *
    *
    *
We mark some empty tiles with letters:
    12A***346
    DEBFGHIJK
    34C***L89
    **5******
    *
    *
    *
    *
    *
In the top-left block, <5> cannot be in ABC, thus it can only be in DE.
In the second row, since <5> must be in DE, it cannot be in F~K.
Now if we look at the top-right block, we can know that L must be <5>.

--- PROGRAMMATIC IMPLEMENTATION ---
1. The Sudoku puzzle
The puzzle is a 9x9 board and thus can be stored in an array of length 81 (index from 0~80). The tile on the i-th (i = 0~8) row and j-th (j = 0~8) column is indexed [i*9+j], i.e.
     0  1  2  3  4  5  6  7  8
     9 10 11 ...
    ...
    72 73 74 75 76 77 78 79 80

The i-th row is [i*9] ~ [i*9+8]; the j-th row is [j], [9+j], [18+j], ..., [72+j].
A block is a bit hard to describe, but with the help of this constant list:
    L = [0, 1, 2, 9, 10, 11, 18, 19, 20],
the k-th block is [3*L[i]+L[0]], [3*L[i]+L[1]], ..., [3*L[i]+L[8]].

Each tile is either settled or unsettled. Either way, we can store all the possibilities for one tile in an array. If the length of the array is one, the tile is settled; if it is more than one, the tile is unsettled.
Upon initialization, all provided tiles should be an array containing only the given number, and all empty tiles should contain <1> ~ <9>.

2. The methods
In the above section we provided three different methods. Now we need to implement them using a program.
a) There are two ways to implement this method. We can either iterate through each tile, and see what are used in the three houses containing it; or iterate through each house, and remove used numbers from unsettled tiles. Either one is not difficult to implement, but the latter one is probably quicker, so we will use it.
b) The key of this method is finding 'groups'. A group is defined as:
    In a house, N tiles where only N unsettled numbers can exist.
After we found a group, the N numbers used in that group cannot be used elsewhere in the house.
When trying to find groups, we should first look for small groups (e.g. only two tiles) and then for large groups. Iterate through all possible combinations and see if groups exist. If a group is found, remove those numbers in tiles outside of the group.
c) Though this method is probably the hardest one for Sudoku players, it is pretty straightforward for programmers. Find what number cannot be in the unique tiles of one house and remove the value from the unique tiles in the other house.

3. The procedure
It is not hard to see that the three methods are not of equal importance. The priority should be (a) > (b) > (c).
Whenever a tile is settled, we should go back to (a); whenever the possibilities for a tile are reduced, we should go back to (b) (in this case going back to (a) does not help). Only if (a) and (b) cannot provide further progress should we use (c).
    (a)
     ┞─ If any tile is settled, do (a) again.
    (b)
     ┞─ If any tile is settled, goto (a).
     ├─ If any tile's possibilities are reduced, do (b) again.
    (c)
     ┞─ If any tile is settled, goto (a).
     ├─ If any tile's possibilities are reduced, goto (b).
    Puzzle cannot be solved. (May contain multiple solutions.)
Of course, if every tile is settled, we've found the solution!
