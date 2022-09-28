package require solvate 
solvate 2_autopsf.psf 2_autopsf.pdb -minmax {{-10 -10 -10} {100 100 100 }} -o 3_solvate
exit