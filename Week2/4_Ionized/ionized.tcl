package require autoionize                                             
resetpsf                                                               
autoionize -psf delete.psf -pdb delete.pdb -o ionzied -nions {{SOD 1}} 
exit                                                                   