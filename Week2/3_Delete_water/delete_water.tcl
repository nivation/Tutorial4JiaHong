mol load psf solvate.psf pdb solvate.pdb
set a [atomselect top " fragment 0 to 8 or fragment 32147 21373 48544 22888 52984 4888 21090 21593 48734 51078 18584 50116 29270 7649 11726 27124 8395 24559 39366 5845 40736 11000 3481 25541 3473 43768 48267 1689 3640 42812 20666 44465 "]
$a writepdb solvate_delete.pdb
$a writepsf solvate_delete.psf                      
