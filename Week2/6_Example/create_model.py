import argparse
import os, subprocess, shutil
import numpy as np
import random

parser = argparse.ArgumentParser()
parser.add_argument("KEMA", type = int, help = "Number of KEMA")
parser.add_argument("GCMA", type = int, help = "Number of GCMA")
parser.add_argument("Boxsize", type = int, help = "Boxsize(A)")
parser.add_argument("water", type = int, help = "number of water")
parser.add_argument("nacl", type = int, help = "pair of nacl")
args = parser.parse_args()

def main(KEMA,GCMA,boxsize,water,nacl):
    filename = "KEMA_"+str(KEMA)+"_GCMA_"+str(GCMA)+"_Boxsize_"+str(boxsize)+"_water_"+str(water)+"_nacl_"+str(nacl)
    if not os.path.isdir(filename):
        os.makedirs(filename)
    packmol(KEMA,GCMA,boxsize)
    autopsf()
    solute(KEMA,GCMA,water,boxsize)
    ionize(nacl)
    
    file = filename+"/5_ionzied.pdb"
    shutil.copy("5_ionzied.pdb",file)
    file = filename+"/5_ionzied.psf"
    shutil.copy("5_ionzied.psf",file)
    return

def packmol(KEMA,GCMA,boxsize):

    print("\nnumber of KEMA:",KEMA)
    print("number of GCMA:",GCMA)
    print("Boxsize:",boxsize)
    
    file_name = "1_packmol.inp"
    with open(file_name,'w') as f:
        f.writelines("                                          \n")
        f.writelines("tolerance 2.0                             \n")
        f.writelines("                                          \n")
        f.writelines("filetype pdb                              \n")
        f.writelines("                                          \n")
        line = "output 1_packmol.pdb\n"
        pdb_file = line
        f.writelines(line)
        f.writelines("                                          \n")
        f.writelines("add_box_sides 2.0                         \n")
        f.writelines("                                          \n")
        f.writelines("structure ./input_pdb/98_132_1A.pdb       \n")
        line = "  number " + str(KEMA)+"                                \n"
        f.writelines(line)
        f.writelines("  inside box 0. 0. 0. 100. 100. 100.      \n")
        f.writelines("end structure                             \n")
        f.writelines("                                          \n")
        f.writelines("structure ./input_pdb/20mer_7GCMA_3GC.pdb \n")
        line = "  number " + str(GCMA)+"                                \n"
        f.writelines(line)
        f.writelines("  inside box 0. 0. 0. 100. 100. 100.      \n")
        f.writelines("end structure                             \n")
        f.writelines("                                          \n")
    
    cmd = "packmol < " + file_name + " > 1_packmol.log"
    n = os.system(cmd)
    if n == 0:
        print('\nPackmol finished\n')
    return 

def autopsf():
    cmd = "vmd -dispdev text -e psfgen.tcl"
    log = "2_autopsf.log"
    ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))
    if ode == 0:
        print("\nPsfgen finished\n")
    return
    
def solute(KEMA,GCMA,water,boxsize):
    with open("3_solvate.tcl","w") as f:
        f.writelines("package require solvate \n")  
        boxmax = str(boxsize)+" "+str(boxsize)+" "+str(boxsize)
        line = "solvate 2_autopsf.psf 2_autopsf.pdb -minmax {{-10 -10 -10} {"+boxmax+" }} -o 3_solvate\n"
        f.writelines(line)
        f.writelines("exit")
    cmd = "vmd -dispdev text -e 3_solvate.tcl"
    log = "3_solvate.log"
    ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))
    if ode == 0:
        print("\nSolvate finished\n")
    
    with open(log,"r") as f:
        for line in f.readlines():
            if 'Waters' in line:
                total_num = int(line.split()[-1])
    
    start = KEMA+GCMA
    water_end = start + water
    water_list = np.arange(start,total_num)
    random.Random(0).shuffle(water_list)
    water_list = water_list[0:water]
    random_line = 'set a [atomselect top " fragment 0 to ' + str(start-1) + ' or fragment ' 
    for i in range(len(water_list)):
        random_line = random_line + str(i) + " "
    random_line = random_line + '"]\n'
    
    with open("4_delete.tcl","w") as f:
        f.writelines("mol load psf 3_solvate.psf pdb 3_solvate.pdb\n")
        f.writelines(random_line)
        f.writelines("$a writepdb 4_delete.pdb          \n")
        f.writelines("$a writepsf 4_delete.psf          \n") 
        f.writelines("exit")
        
    cmd = "vmd -dispdev text -e 4_delete.tcl"
    log = "4_delete.log"
    ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))
    if ode == 0:
        print("\nDelete finished\n")
    return
     
def ionize(nacl):
    with open("5_ionized.tcl","w") as f:
        f.writelines("package require autoionize                                               \n")
        f.writelines("resetpsf                                                                 \n")
        line = "autoionize -psf 4_delete.psf -pdb 4_delete.pdb -o 5_ionzied -nions {{SOD " + str(nacl) +"} {CLA "+str(nacl)+"}}   \n"
        f.writelines(line)
        f.writelines("exit")
    cmd = "vmd -dispdev text -e 5_ionized.tcl"
    log = "5_ionized.log"
    ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))
    if ode == 0:
        print("\nIonized finished\n")
    return

if __name__ == '__main__':
    main(args.KEMA,args.GCMA,args.Boxsize,args.water,args.nacl)  