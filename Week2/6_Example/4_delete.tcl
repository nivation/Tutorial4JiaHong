mol load psf 3_solvate.psf pdb 3_solvate.pdb
set a [atomselect top " fragment 0 to 1 or fragment 0 1 2 3 4 5 6 7 8 9 "]
$a writepdb 4_delete.pdb          
$a writepsf 4_delete.psf          
exit