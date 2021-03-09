*Currently on hold, see [here](https://riedler.wien/coding/).*

This project is aimed to provide the user with as much information about Sorting algorithms as possible.I always value amount and quality of information over how pretty it is to look at.
This being said, this project is a visualizer of sorting algorithms. You can see when new buckets are created, reads are displayed in green, writes in red. Stats are displayed for reads, swaps, inserts, bucket creation/deletion, and passing cycles.
All Algorithms work via a sort-of-API that consists of 8 different statements. One statement per cycle can be returned.

- READ can read an item in a bucket
- SWAP swaps two items in the same bucket
- INSERT inserts an items at a index in the same bucket
- NEW_BUCK creates a new bucket and CAN transfer one item from another bucket to it
- BUCKSWAP swaps an item from one bucket to another item from another bucket
- BUCKINSERT inserts an item from one bucket to an index in another bucket
- DEL_BUCK deletes a bucket. If the bucket is not empty, nothing happens
- PULL pulls an item from the end of a bucket into the variable space
- PUSH pushes an item from the variable space onto a bucket
- PULSH pulls an item from one bucket and onto another one
- FIN ends the sorting

The Algorithms only have access to unlimited variable space, the length of the initial array and these statements.
There may exist some sort of pseudo-multithreading support in the future, where an algorithm can return multiple statements that will get processed in random order, but count as one cycle.
4 different shufflers and a reverser are implemented with this 'API' and can be accessed through the 'Reverse' and 'Shuffle' buttons. The Randomness can be determined with the 'Randomness' Button.
The user can also set the cycles per frame and maximum fps/ups with the buttons 'Speed' and 'FPS/UPS', respectively.
There will be a description for each Algorithm in the future.

Even though this is made with Python, I will always make sure even very weak machines can run this at 60fps.
All known bugs will be fixed until a release is issued, except for minor and very specific ones.
Only Linux is officially supported, but other ones should work too. If they don't, please file an issue.
Depending on the severity of the issue, and the accessibility of the OS, it will get fixed more or less quickly.

### How to Install
Currently, no installation packages exist, so you have to run it from source. This will be changed before 1.0 and maybe even before 0.1.

#### Dependencies
Of course, python 3 ist required. The project is aimed at Python 3.8, but it should work for older versions too. Please file an issue if it doesn't.
Dependencies installable through pip include:

- pyglet

#### running
In order to start the program, you have to run main.py with python. This opens the game in borderless window mode. You can close the program by pressing ESC.

### Videos
- [Coding logs](https://www.youtube.com/playlist?list=PLS2fPT7ug4bX_t_mjvWyx_KoADLQWTrnq)
- [Visualisations](https://www.youtube.com/playlist?list=PLS2fPT7ug4bW6Bbb7uuKZ0PDuBq_AnDNn)

### Screenshots
#### TODO
