package require psfgen                                   
resetpsf                                                 
topology top_1_25.rtf                       
mol new packmol.pdb
set all_atom [atomselect top "all"]                      
set chain_list [lsort -unique [$all_atom get fragment]]     
foreach chain_id $chain_list {                           
    puts $chain_id                                       
    set select_atoms [atomselect top "fragment ${chain_id}"]
    $select_atoms set segname $chain_id                  
    $select_atoms writepdb ${chain_id}.pdb               
    segment ${chain_id} {pdb ${chain_id}.pdb}            
    coordpdb ${chain_id}.pdb ${chain_id}                 
    guesscoord                                           
    regenerate angles dihedrals                          
    $select_atoms delete                                 
    file delete ${chain_id}.pdb                          
}                                                        
writepdb autopsf.pdb                                 
writepsf autopsf.psf                                 
resetpsf                                                
