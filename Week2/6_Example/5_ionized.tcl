package require autoionize                                               
resetpsf                                                                 
autoionize -psf 4_delete.psf -pdb 4_delete.pdb -o 5_ionzied -nions {{SOD 1} {CLA 1}}   
exit