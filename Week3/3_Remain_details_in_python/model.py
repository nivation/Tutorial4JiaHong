import argparse
import os, subprocess, shutil
import time
import random
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("KEMA"     ,type=int  ,help="Number of KEMA set")
parser.add_argument("GCMA"     ,type=int  ,help="Number of GCMA polymer")
parser.add_argument("Water"    ,type=int  ,help="Number of Water molecule (-1: will not delete water molecule after VMD solvate)")
parser.add_argument("Salt"     ,type=float,help="Neutralize and set salt concentration (g/L) (0 for not adding any salt)")
parser.add_argument("Boxsize"  ,type=int  ,help="Initial box size (A)")
parser.add_argument("Conjugate",type=int  ,help="Create conjugate system (1 yes, 0 no)")
parser.add_argument("Delete"   ,type=int  ,help="Delete working files or not (1 delete, 0 keep)")
args = parser.parse_args()

def main(KEMA,GCMA,water,salt,boxsize,conjugate,delete):
    model_list = ['Original','Conjugate']
    if KEMA == 0 and GCMA == 0:
        print('WTF are u doing here?')
        exit()

    # 修正conjugate避免亂打
    if conjugate == 1:
        pass
    else:
        conjugate = 0
        print("------------Skip Conjugate------------")

    for num in range(len(model_list[0:conjugate+1])):
        model_type = model_list[num]
        print('\n--------------',model_type,'--------------')
        print('Num of KEMA/KE set   :',KEMA)
        print('Num of Neutrlize SOD :',KEMA*22)
        print('Num of GCMA/GC       :',GCMA)

        water_num = water
        # 設定
        if num == 0:
            # MA系列
            KEMA_mass = 36732.978
            GCMA_mass = 5143.3864
            KEMA_atom = 5071
            GCMA_atom = 709
        else :
            # 沒有MA系列
            KEMA_mass = 32252.045
            GCMA_mass = 4122.2554
            KEMA_atom = 4492
            GCMA_atom = 583

            # 根據KEMA/GCMA模型盡量去對齊KE/GC和水的濃度
            if KEMA_weigth_percentage == 0:
                GC_water  = (GCMA*GCMA_mass/GCMA_weigth_percentage-KEMA*KEMA_mass-GCMA*GCMA_mass)/18.01/(1+salt/1000)
                KE_water  = GC_water
            elif GCMA_weigth_percentage == 0:
                KE_water  = (KEMA*KEMA_mass/KEMA_weigth_percentage-KEMA*KEMA_mass-GCMA*GCMA_mass)/18.01/(1+salt/1000)
                GC_water  = KE_water
            else:
                if type(KEMA_weigth_percentage) == str:
                    # 促使water_num算出來是負的
                    KE_water  = -1
                    GC_water  = -1
                else:
                    KE_water  = (KEMA*KEMA_mass/KEMA_weigth_percentage-KEMA*KEMA_mass-GCMA*GCMA_mass)/18.01/(1+salt/1000)
                    GC_water  = (GCMA*GCMA_mass/GCMA_weigth_percentage-KEMA*KEMA_mass-GCMA*GCMA_mass)/18.01/(1+salt/1000)

            water_num     = round((KE_water*(KEMA)+GC_water*(GCMA))/(KEMA+GCMA))

        # 鹽與濃度
        if water_num >=  0:
            water_mass = 18.01*water_num
            # PBS solution is water with NaCl(58.43977g/mol) concentration of 8g/L
            # 鑒於VMD加離子的特性，必須要補充多的水給VMD作替代，所以這邊的salt數量必須包在water裡面
            # 因為ARG(+1),LYS(+1),GLU(-1),ASP(-1)在PH=7的環境下會帶電，這邊直接將1組KE/KEMA的總帶電量(-22e)用鈉離子(Na+)中和
            neutralize_SOD = 22 * KEMA
            salt_num       = round(water_mass/1000*salt/58.43977)
            SOD_num        = neutralize_SOD + salt_num
            CLA_num        = salt_num

            KEMA_total = KEMA * KEMA_mass
            GCMA_total = GCMA * GCMA_mass
            Polymer    = KEMA_total + GCMA_total
            Total      = Polymer + water_mass + SOD_num*22.98977 + CLA_num*35.45
            
            KEMA_weigth_percentage = KEMA_total   / Total
            GCMA_weigth_percentage = GCMA_total   / Total
            weigth_percentage      = Polymer      / Total
            total_atom             = KEMA*KEMA_atom + GCMA*GCMA_atom + 3*water + SOD_num + CLA_num
        else:
            water_num= 'VMD_auto_solvate'
            salt     = '8.0'
            salt_num = 'VMD_auto_ionize'
            SOD_num  = 'Unknown'
            CLA_num  = 'Unknown'
            KEMA_weigth_percentage = 'Unknown'
            GCMA_weigth_percentage = 'Unknown'
            weigth_percentage      = 'Unknown'
            total_atom             = 'Unknown'
            
        print("Num of water         :",water_num)
        print("Add NaCl (g/L)       :",salt)
        print("Pair of NaCl         :",salt_num)
        print("Total SOD            :",SOD_num)
        print("Total CLA            :",CLA_num)
        print("\nKE/KEMA Weight percentage of this system ((KEMA)/(KEMA+GCMA+water+salt)))      (g/g) is:",KEMA_weigth_percentage)
        print("GC/GCMA Weight percentage of this system ((GCMA)/(KEMA+GCMA+water+salt)))      (g/g) is:"  ,GCMA_weigth_percentage)
        print("Polymer Weight percentage of this system ((KEMA+GCMA)/(KEMA+GCMA+water+salt))) (g/g) is:"  ,weigth_percentage,'\n')
        print("Total atoms          :",total_atom)
        
        # 紀錄一些東西
        if num == 0:
            water_original  = water_num
            SOD_original    = SOD_num
            CLA_original    = CLA_num
        else:
            water_conjugate = water_num
            SOD_conjugate   = SOD_num
            CLA_conjugate   = CLA_num

    # print(water_original,salt_num_original,water_conjugate,salt_num_conjugate)
    # 其他資訊
    print('\nPackMol Boxsize(A)   :',boxsize)
    if delete == 1:
        print("Delete               : Delete working file and script")
    else:
        delete = 0
        print("Delete               : Keep all file and script")
    input("\nPress Enter key if the Polymer weight percentage is correct, or please interrupt...")
    print("\nContinue")

    # 檔案夾
    if conjugate == 1:
        folder_name    = 'KEMA_'+str(KEMA)+'_GCMA_'+str(GCMA)+'_water_'+str(water_original) +'_NaCl_con_'+str(salt)+'_SOD_'+str(SOD_num)       + '_CLA_' + str(CLA_num)       +'_boxsize_'+str(boxsize)+'_conjugate'
        original_name  = 'KEMA_'+str(KEMA)+'_GCMA_'+str(GCMA)+'_water_'+str(water_original) +'_NaCl_con_'+str(salt)+'_SOD_'+str(SOD_original)  + '_CLA_' + str(CLA_original)  +'_boxsize_'+str(boxsize)
        conjugate_name = 'KE_'  +str(KEMA)+'_GC_'  +str(GCMA)+'_water_'+str(water_conjugate)+'_NaCl_con_'+str(salt)+'_SOD_'+str(SOD_conjugate) + '_CLA_' + str(CLA_conjugate) +'_boxsize_'+str(boxsize)
    else:
        folder_name    = 'KEMA_'+str(KEMA)+'_GCMA_'+str(GCMA)+'_water_'+str(water_original) +'_NaCl_con_'+str(salt)+'_SOD_'+str(SOD_num)       + '_CLA_' + str(CLA_num)       +'_boxsize_'+str(boxsize)   
        original_name  = 'KEMA_'+str(KEMA)+'_GCMA_'+str(GCMA)+'_water_'+str(water_original) +'_NaCl_con_'+str(salt)+'_SOD_'+str(SOD_num)       + '_CLA_' + str(CLA_num)       +'_boxsize_'+str(boxsize)
        conjugate_name = ''

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    
    packmol_list = packmol(KEMA,GCMA,boxsize,folder_name,original_name,conjugate_name)
    print("\nPackmol finished")
    
    for packmol_pdb_num in range(len(packmol_list)):
        # 因為VMD ionize時會拿掉與總離子等數量的水，拿掉濃度就跑掉了，所以要補上去
        if packmol_pdb_num == 0:
            vmd_water   = water_original + SOD_original + CLA_original
            VMD_SOD     = SOD_original
            VMD_CLA     = CLA_original
            packmol_pdb = packmol_list[packmol_pdb_num]
            name        = original_name

            # test
            #autopsf_output = ['KEMA_1_GCMA_0_water_1000_NaCl_con_8.0_SOD_24_CLA_2_boxsize_100_conjugate/KEMA_1_GCMA_0_water_1000_NaCl_con_8.0_SOD_24_CLA_2_boxsize_100_autopsf_solvate_ionzied.pdb', 'KEMA_1_GCMA_0_water_1000_NaCl_con_8.0_SOD_24_CLA_2_boxsize_100_conjugate/KEMA_1_GCMA_0_water_1000_NaCl_con_8.0_SOD_24_CLA_2_boxsize_100_autopsf_solvate_ionzied.psf']
        else:
            vmd_water   = water_conjugate + SOD_conjugate + CLA_conjugate
            VMD_SOD     = SOD_conjugate
            VMD_CLA     = CLA_conjugate
            packmol_pdb = packmol_list[packmol_pdb_num]
            name        = conjugate_name

            # test
            #autopsf_output = ['KEMA_1_GCMA_0_water_1000_NaCl_con_8.0_SOD_24_CLA_2_boxsize_100_conjugate/KE_1_GC_0_water_908_NaCl_con_8.0_SOD_24_CLA_2_boxsize_100_autopsf_solvate_ionzied.pdb', 'KEMA_1_GCMA_0_water_1000_NaCl_con_8.0_SOD_24_CLA_2_boxsize_100_conjugate/KE_1_GC_0_water_908_NaCl_con_8.0_SOD_24_CLA_2_boxsize_100_autopsf_solvate_ionzied.psf']

        autopsf_output  = autopsf(KEMA,GCMA,packmol_pdb_num,packmol_pdb,vmd_water,VMD_SOD,VMD_CLA,boxsize,folder_name,name)
        print("\nAutopsf finished")
        charmm2lmp_pdb = autopsf_output[0]
        charmm2lmp_psf = autopsf_output[1]
        charmm2lmp(charmm2lmp_pdb,charmm2lmp_psf,folder_name,name)
        print("\nCharmm2lmp finished")
        createTWCC(folder_name,name)
        print("\nCreateTWCC finished")

    # 刪除檔案用
    if delete == 1:
        files = [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name,f))]
        for f in files:
            if '_autopsf_solvate_ionzied_ctrl' in f:
                pass
            elif f.split('.')[0] == 'log':
                pass
            else:
                os.remove(os.path.join(folder_name,f))

def packmol(KEMA,GCMA,boxsize,folder_name,original_name,conjugate_name):
    original_packmol_pdb  = './'+folder_name+'/'+original_name +'.pdb'
    packmol_inp = './'+folder_name+'/'+original_name+'.inp'
    # 撰寫給packmol的inp檔
    with open(packmol_inp,'w') as f:
        f.writelines('\ntolerance 2.0\n')
        f.writelines('\nfiletype pdb\n')
        out = '\noutput '+original_packmol_pdb+'\n'
        f.writelines(out)
        out = '\nadd_box_sides 2.0\n'
        f.writelines(out)
        if KEMA!= 0:
            f.writelines('\nstructure ./input_pdb/98_132_1A.pdb    \n')
            f.writelines('  number '+str(KEMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')
            f.writelines('									     \n')
            f.writelines('structure ./input_pdb/144_177_1B_1.pdb \n')
            f.writelines('  number '+str(KEMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')
            f.writelines('									     \n')
            f.writelines('structure ./input_pdb/178_210_1B_2.pdb \n')
            f.writelines('  number '+str(KEMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')
            f.writelines('									     \n')
            f.writelines('structure ./input_pdb/211_244_1B_3.pdb \n')
            f.writelines('  number '+str(KEMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')
            f.writelines('									     \n')
            f.writelines('structure ./input_pdb/261_279_2A.pdb   \n')
            f.writelines('  number '+str(KEMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')
            f.writelines('									     \n')
            f.writelines('structure ./input_pdb/288_327_2B_1.pdb \n')
            f.writelines('  number '+str(KEMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')
            f.writelines('									     \n')
            f.writelines('structure ./input_pdb/328_369_2B_2.pdb \n')
            f.writelines('  number '+str(KEMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')
            f.writelines('									     \n')
            f.writelines('structure ./input_pdb/370_408_2B_3.pdb \n')
            f.writelines('  number '+str(KEMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')  
        if GCMA != 0:
            f.writelines('\nstructure ./input_pdb/20mer_7GCMA_3GC.pdb \n')
            f.writelines('  number '+str(GCMA)                   +'\n')
            f.writelines('  inside box 0. 0. 0. '+str(boxsize)+'. '+str(boxsize)+'. '+str(boxsize) +'.\n')
            f.writelines('end structure                          \n')  
    
    cmd = 'packmol < '+ packmol_inp +' > ./'+folder_name+'/log.packmol'
    os.system(cmd)

    # 根據KEMA下去改PACKMOL的結果，才能確保初始結構相似
    if conjugate_name != '': 
        conjugate_packmol_pdb = './'+folder_name+'/'+conjugate_name+'.pdb'
        with open(conjugate_packmol_pdb,'w') as f:
            with open(original_packmol_pdb,'r') as g:
                for line in g.readlines():
                    if 'HSP' in line:
                        temp_list = line.split('HSP')
                        out  = temp_list[0] + 'HSE' + temp_list[1]
                        f.writelines(out)
                    else:
                        f.writelines(line)
        return [original_packmol_pdb,conjugate_packmol_pdb]
    else:
        return [original_packmol_pdb]

def autopsf(KEMA,GCMA,packmol_pdb_num,packmol_pdb,vmd_water,VMD_SOD,VMD_CLA,boxsize,folder_name,name):
    # PSF Generator
    out_pdb         = folder_name+'/'+name +'_autopsf.pdb'
    out_psf         = folder_name+'/'+name +'_autopsf.psf'
    out_tcl         = folder_name+'/'+name+'.tcl'
    
    with open(out_tcl,'w') as f:
        f.writelines('package require psfgen                                   \n')
        f.writelines('resetpsf                                                 \n')
        # 第一次(正常情況)都只會有KEMA/GCMA
        if packmol_pdb_num == 0:
            f.writelines('topology top_1_25.rtf                       \n')
        else:
            f.writelines('topology top_all36m_prot.rtf                \n')
        f.writelines('mol new '+          packmol_pdb           +'\n')
        f.writelines('set all_atom [atomselect top "all"]                      \n')
        f.writelines('set chain_list [lsort -unique [$all_atom get fragment]]     \n')
        f.writelines('foreach chain_id $chain_list {                           \n')
        f.writelines('    puts $chain_id                                       \n')
        f.writelines('    set select_atoms [atomselect top "fragment ${chain_id}"]\n')
        f.writelines('    $select_atoms set segname $chain_id                  \n')
        f.writelines('    $select_atoms writepdb ${chain_id}.pdb               \n')
        f.writelines('    segment ${chain_id} {pdb ${chain_id}.pdb}            \n')
        f.writelines('    coordpdb ${chain_id}.pdb ${chain_id}                 \n')
        f.writelines('    guesscoord                                           \n')
        f.writelines('    regenerate angles dihedrals                          \n')
        f.writelines('    $select_atoms delete                                 \n')
        f.writelines('    file delete ${chain_id}.pdb                          \n')
        f.writelines('}                                                        \n')
        f.writelines('writepdb '+out_pdb +   '                                 \n')
        f.writelines('writepsf '+out_psf +   '                                 \n')
        f.writelines('resetpsf                                                 \n')
        f.writelines('exit                                                     \n')
    
    cmd = 'vmd -dispdev text -e '+out_tcl
    if packmol_pdb_num == 0:
        log = './'+folder_name+'/log.psf'
    else:
        log = './'+folder_name+'/log.psf_conjugate'
    ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))

    # Solvate if VMD water != 0
    if type(vmd_water) == int and vmd_water != 0:
        solvate_tcl     = folder_name+'/'+name +'_solvate.tcl'
        out_solvate     = folder_name+'/'+name +'_autopsf_solvate'
        out_solvate_pdb = folder_name+'/'+name +'_autopsf_solvate.pdb'
        out_solvate_psf = folder_name+'/'+name +'_autopsf_solvate.psf'

        with open(solvate_tcl,'w') as f:
            f.writelines('package require solvate                                  \n')
            out = "solvate " + out_psf +" "+ out_pdb+" -minmax {{"+str(-10)+' '+str(-10)+' '+str(-10)+"} {"+str(boxsize+10)+' '+str(boxsize+10)+' '+str(boxsize+10)+' }} -o '+out_solvate +'\n'
            f.writelines(out)
            f.writelines('exit                                                     \n')
        cmd = 'vmd -dispdev text -e '+solvate_tcl
        if packmol_pdb_num == 0:
            log = './'+folder_name+'/log.solvate'
        else:
            log = './'+folder_name+'/log.solvate_conjugate'
        ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))    

        # Delete additional water by VMD atomselect + random list
        with open(log,'r') as f:
            for line in f.readlines():
                if 'Waters: ' in line:
                    start_water = int(line.split('Waters: ')[-1])

        fragment_out = 'set a [atomselect top " fragment 0 to ' + str(KEMA*8+GCMA-1) + ' or fragment '
        pick_list = np.arange(KEMA*8+GCMA,start_water+KEMA*8+GCMA)
        random.Random(0).shuffle(pick_list)
        pick_list = pick_list[0:vmd_water]
        for fragment_id in pick_list:
            fragment_out = fragment_out + str(fragment_id) + ' '
        fragment_out = fragment_out + '"]\n'

        delete_water_tcl = folder_name+'/'+name +'_delete_water.tcl'
        out_solvate_pdb  = folder_name+'/'+name +'_autopsf_solvate.pdb'
        out_solvate_psf  = folder_name+'/'+name +'_autopsf_solvate.psf'
        delete_water_pdb = folder_name+'/'+name +'_autopsf_solvate_delete.pdb'
        delete_water_psf = folder_name+'/'+name +'_autopsf_solvate_delete.psf'

        with open(delete_water_tcl,'w') as f:
            out = 'mol load psf ' + out_solvate_psf +' pdb ' + out_solvate_pdb + '\n'
            f.writelines(out)
            f.writelines(fragment_out)
            out = '$a writepdb ' + delete_water_pdb +'\n'
            f.writelines(out)
            out = '$a writepsf ' + delete_water_psf +'\n'
            f.writelines(out)
            f.writelines('exit                                                     \n')
        cmd = 'vmd -dispdev text -e '+delete_water_tcl
        if packmol_pdb_num == 0:
            log = './'+folder_name+'/log.delete'
        else:
            log = './'+folder_name+'/log.delete_conjugate'
        ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))  
        for_ion_pdb = delete_water_pdb
        for_ion_psf = delete_water_psf
    else:
        for_ion_pdb = out_pdb
        for_ion_psf = out_psf

    # Ionize
    out_ion_pdb     = folder_name+'/'+name +'_autopsf_solvate_ionzied.pdb'
    out_ion_psf     = folder_name+'/'+name +'_autopsf_solvate_ionzied.psf'
    if type(VMD_SOD)!= str and (VMD_SOD != 0 or VMD_CLA != 0):
        ionized_tcl = folder_name+'/'+name+'_ionized.tcl'
        out_ion     = folder_name+'/'+name +'_autopsf_solvate_ionzied'
        out         = "autoionize -psf " + for_ion_psf +" -pdb "+ for_ion_pdb +' -o '+out_ion+' -nions {'
        if VMD_SOD != 0:
            out    += '{SOD ' + str(VMD_SOD) + '}'
        if VMD_CLA != 0:
            out    += ' {CLA ' + str(VMD_CLA) + '}'
        out        += '}\n'
        with open(ionized_tcl,'w') as f:
            f.writelines('package require autoionize                               \n')
            f.writelines('resetpsf                                                 \n')
            # out = "autoionize -psf " + delete_water_psf +" -pdb "+ delete_water_pdb +' -o '+out_ion+' -nions {{SOD '+ str(vmd_salt)+'} {CLA ' + str(vmd_salt) +'}}\n'
            #out = "autoionize -psf " + for_ion_psf +" -pdb "+ for_ion_pdb +' -o '+out_ion+' -sc ' + str(0.15) + '\n'
            f.writelines(out)
            f.writelines('exit                                                     \n')
        cmd = 'vmd -dispdev text -e '+ionized_tcl
        if packmol_pdb_num == 0:
            log = './'+folder_name+'/log.ionized'
        else:
            log = './'+folder_name+'/log.ionized_conjugate'
        ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))

    else:
        shutil.move(for_ion_pdb,out_ion_pdb)
        shutil.move(for_ion_psf,out_ion_psf)

    return [out_ion_pdb,out_ion_psf]

def charmm2lmp(charmm2lmp_pdb,charmm2lmp_psf,folder_name,name):
    # 修正倒數一行缺少TER的問題
    temp_pdb = './'+folder_name+'/charmm2lmp_temp.pdb'
    with open(charmm2lmp_pdb,'r') as f:
        with open(temp_pdb,'w') as h:
            for line in f.readlines():
                if 'END' in line:
                    h.writelines('TER\n')
                h.writelines(line)
    shutil.move(temp_pdb,charmm2lmp_pdb)

    # 執行perl
    filename = charmm2lmp_pdb.split('.pdb')[0]
    flag     = filename.split('/')[-1].split('_')[0]
    if flag == 'KE':
        cmd = 'wsl perl charmm2lammps.pl all36m_prot '+filename+' -cmap charmm36'
        log = './'+folder_name+'/'+'log.charmm2lammps_conjugate'
    else:
        cmd = 'wsl perl charmm2lammps.pl 1_25 ' + filename+' -cmap charmm36'
        log = './'+folder_name+'/'+'log.charmm2lammps'
    ode = subprocess.call(cmd.split(), stdout=open(log, 'w'))

    return

def createTWCC(folder_name,name):
    # 創建資料夾
    twcc_dir = folder_name + '/' +name
    if not os.path.exists(twcc_dir):
        os.mkdir(twcc_dir)
    in_file = twcc_dir + '/300K_equilibrium.in'
    sh_file = twcc_dir + '/lmpsub_eq.sh'
    charmm2lmp_in = folder_name+'/'+name+'_autopsf_solvate_ionzied.in'
    pair_coeff = []
    shake = ""
    # 記錄NB FIX的LJ係數
    with open(charmm2lmp_in,'r') as f:
        for line in f.readlines():
            if 'pair_coeff' in line:
                pair_coeff.append(line)
            elif 'all shake' in line:
                shake = line
    # lammps input file
    with open(in_file,'w') as f :
        f.writelines("# Variable                                                                                                                                              \n")                      
        f.writelines("variable		npt_step	equal	50000000           # 50 ns                                                                                            \n")
        f.writelines("variable		npt_thermo	equal	${npt_step}/500                                                                                                       \n")
        f.writelines("variable        small_step  equal   10                                                                                                                  \n")
        f.writelines("variable        criteria    equal   0.00001                                                                                                                \n")            
        f.writelines("variable        filename    string  input.data                                                                                                          \n")
        f.writelines("units           real                                                                                                                                    \n")
        f.writelines("timestep        1                                                                                                                                       \n")
        f.writelines("                                                                                                                                                        \n")
        f.writelines("# Potential define                                                                                                                                      \n")
        f.writelines("newton          off                                                                                                                                     \n")
        f.writelines("atom_style      full                                                                                                                                    \n")
        f.writelines("bond_style      harmonic                                                                                                                                \n")
        f.writelines("angle_style     charmm                                                                                                                                  \n")
        f.writelines("dihedral_style  charmmfsw                                                                                                                               \n")
        f.writelines("improper_style  harmonic                                                                                                                                \n")
        f.writelines("pair_style      lj/charmmfsw/coul/long 10 12                                                                                                            \n")
        f.writelines("kspace_style    pppm 1e-6                                                                                                                               \n")
        f.writelines("pair_modify     mix arithmetic                                                                                                                          \n")
        f.writelines("                                                                                                                                                        \n")
        f.writelines("# Modify following line to point to the desired CMAP file                                                                                               \n")
        f.writelines("fix             cmap all cmap charmm36.cmap                                                                                                             \n")
        f.writelines("fix_modify      cmap energy yes                                                                                                                         \n")
        f.writelines("read_data       ${filename} fix cmap crossterm CMAP                                                                                                     \n")
        for l in range(len(pair_coeff)):
            f.writelines(pair_coeff[l])
        f.writelines("\nspecial_bonds   charmm                                                                                                                                                \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("# Minimized                                                                                                                                                           \n")
        f.writelines("neigh_modify    every 1 delay 0 check yes                                                                                                                             \n")
        f.writelines("min_style       cg                                                                                                                                                    \n")
        f.writelines("minimize        0.0 1.0e-9 100000 1000000                                                                                                                             \n")
        f.writelines("write_data      minimized.data pair ij                                                                                                                                \n")
        f.writelines("velocity        all create 300 23112 dist gaussian                                                                                                                    \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("# Setup                                                                                                                                                               \n")
        f.writelines("fix 			1 all npt temp 300.0 300.0 100.0 iso 1 1 1000.0                                                                                                       \n")
        f.writelines("thermo_style    custom step time xlo xhi ylo yhi zlo zhi etotal pe ke ebond temp press eangle edihed eimp evdwl ecoul elong vol density                               \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("# Prevent PPPM error                                                                                                                                                  \n")
        f.writelines("dump            1 all dcd ${small_step} PPPM.dcd \n")                                                                                                         
        f.writelines("dump_modify     1 unwrap yes                     \n")
        f.writelines("\n")        
        f.writelines("label           loopa                                                                                                                                                 \n")
        f.writelines("variable        xlo equal xlo                                                                                                                                         \n")
        f.writelines("variable        xhi equal xhi                                                                                                                                         \n")
        f.writelines("variable        x_initial equal ${xhi}-${xlo}                                                                                                                         \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("variable        ylo equal ylo                                                                                                                                         \n")
        f.writelines("variable        yhi equal yhi                                                                                                                                         \n")
        f.writelines("variable        y_initial equal ${yhi}-${ylo}                                                                                                                         \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("variable        zlo equal zlo                                                                                                                                         \n")
        f.writelines("variable        zhi equal zhi                                                                                                                                         \n")
        f.writelines("variable        z_initial equal ${zhi}-${zlo}                                                                                                                         \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("run             ${small_step}                                                                                                                                         \n")
        f.writelines("minimize        0.0 1.0e-9 100000 1000000                                                                                                                                         \n")
        f.writelines("variable        x_end equal lx                                                                                                                                        \n")
        f.writelines("variable        y_end equal ly                                                                                                                                        \n")
        f.writelines("variable        z_end equal lz                                                                                                                                        \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("variable        xchange equal abs(${x_initial}-${x_end})                                                                                                                   \n")
        f.writelines("variable        ychange equal abs(${y_initial}-${y_end})                                                                                                                   \n")
        f.writelines("variable        zchange equal abs(${z_initial}-${z_end})                                                                                                                   \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines('print           "Change ${xchange} ${ychange} ${zchange}"                                                                                                             \n')
        f.writelines("write_data      PPPM.data pair ij                                    \n")                                                                                     
        f.writelines("write_dump      all custom PPPM.dump id type x y z vx vy vz ix iy iz \n") 
        f.writelines('if              "${xchange} > ${criteria}" then "jump SELF loopa"                                                                                                     \n')
        f.writelines('if              "${ychange} > ${criteria}" then "jump SELF loopa"                                                                                                     \n')
        f.writelines('if              "${zchange} > ${criteria}" then "jump SELF loopa"                                                                                                     \n')
        f.writelines("jump            SELF break                                                                                                                                            \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("label           break                                                                                                                                                 \n")
        f.writelines("undump          1 \n")
        f.writelines('print           "Start Production"                                                                                                                                    \n')
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("# Setup                                                                                                                                                               \n")
        f.writelines("restart 		${npt_thermo} ./restart/300K_equilibrium.restart                                                                                                      \n")
        f.writelines("dump            1 all dcd ${npt_thermo} 300K_equilibrium.dcd                                                                                                          \n")
        f.writelines("dump_modify     1 unwrap yes                                                                                                                                          \n")
        f.writelines("thermo          ${npt_thermo}                                                                                                                                         \n")
        f.writelines("                                                                                                                                                                      \n")
        f.writelines("# NPT 300K                                                                                                                                                            \n")
        f.writelines("fix 			1 all npt temp 300.0 300.0 100.0 iso 1 1 1000.0                                                                                                       \n")                                                                                     
        f.writelines("run             ${npt_step}                                                                                                                                           \n")
        f.writelines("write_data      300K_equilibrium.data pair ij                                                                                                                         \n")
        f.writelines("write_dump      all custom 300K_equilibrium.dump id type x y z vx vy vz ix iy iz                                                                                      \n")

    name_for_bash = name.split('_water_')[0]
    
    # 平衡用bash檔
    with open(sh_file,'w',encoding="utf-8") as f:
        f.writelines("#!/bin/bash\n")             
        f.writelines("#PBS -l select=4:ncpus=40:mpiprocs=40:ompthreads=1\n")
        out = "#PBS -N "+name_for_bash+"_eq \n"
        f.writelines(out)
        f.writelines("#PBS -q ct160\n")
        f.writelines("#PBS -P MST110475\n")
        f.writelines("#PBS -j oe\n")
        f.writelines("\n")
        f.writelines("cd $PBS_O_WORKDIR\n")
        f.writelines("\n")
        f.writelines("module purge\n")
        f.writelines("module load intel/2018_u1\n")
        f.writelines("module load cuda/8.0.61\n")
        f.writelines("OMP_NUM_THREADS=1\n")
        f.writelines("\n")
        f.writelines('echo "Your LAMMPS job starts at `date`"\n')
        f.writelines("\n")
        f.writelines('echo "Start time:" `date` 2>&1 > time.log\n')
        f.writelines("t1=`date +%s`\n")
        f.writelines("\n")
        f.writelines("mkdir restart\n")
        f.writelines("mpiexec.hydra -PSM2 /pkg/CMS/LAMMPS/lammps-16Mar18/bin/lmp_run_cpu -in ./300K_equilibrium.in > eq.log\n")
        f.writelines("\n")
        f.writelines("t2=`date +%s`\n")
        f.writelines('echo "Finish time:" `date` 2>&1 >> time.log\n')
        f.writelines('echo "Total runtime:" $[$t2-$t1] "seconds" 2>&1 >> time.log\n')
        f.writelines("\n")
        f.writelines("qstat -x -f ${PBS_JOBID} 2>&1 > job.log\n")
        f.writelines("\n")
        f.writelines('echo "Your LAMMPS job completed at  `date` "\n')
 
    # 個別整理成資料夾
    src = folder_name + "/" + name + "_autopsf_solvate_ionzied.data"
    # 名字太長的話，move會失敗，所以改成Input
    dst = twcc_dir + '/' +'input.data'
    shutil.move(src,dst)

    src = "charmm36.cmap"
    dst = folder_name+"/"+name+"/"+"charmm36.cmap"
    shutil.copy(src,dst)
    return


if __name__ == '__main__':
    main(args.KEMA,args.GCMA,args.Water,args.Salt,args.Boxsize,args.Conjugate,args.Delete)  