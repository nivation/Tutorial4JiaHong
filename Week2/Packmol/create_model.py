import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("KEMA", type = int, help = "Number of KEMA")
parser.add_argument("GCMA", type = int, help = "Number of GCMA")
parser.add_argument("Boxsize", type = int, help = "Boxsize(A)")
args = parser.parse_args()

def main(KEMA,GCMA,boxsize):
    pdbfile = packmol(KEMA,GCMA,boxsize)
    print(pdbfile)
    return

def packmol(KEMA,GCMA,boxsize):

    print("\nnumber of KEMA:",KEMA)
    print("number of GCMA:",GCMA)
    print("Boxsize:",boxsize)
    
    file_name = "KEMA_"+str(KEMA)+"_GCMA_"+str(GCMA)+ "_Boxsize_"+str(boxsize)+".inp"
    with open(file_name,'w') as f:
        f.writelines("                                          \n")
        f.writelines("tolerance 2.0                             \n")
        f.writelines("                                          \n")
        f.writelines("filetype pdb                              \n")
        f.writelines("                                          \n")
        line = "output KEMA_"+str(KEMA)+"_GCMA_"+str(GCMA)+ "_Boxsize_"+str(boxsize)+".pdb\n"
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
    
    cmd = "packmol < " + file_name + " > packmol.log"
    os.system(cmd)
    return pdb_file

if __name__ == '__main__':
    main(args.KEMA,args.GCMA,args.Boxsize)  