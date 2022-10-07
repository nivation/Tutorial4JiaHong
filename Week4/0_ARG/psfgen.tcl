package require psfgen             
resetpsf    
topology top_all36m_prot.rtf               
mol new not_complete_ARG.pdb
set all_atom [atomselect top "all"]                     
set chain_list [lsort -unique [$all_atom get fragment]]
set chain_list {0}
foreach chain_id $chain_list {                           
    puts $chain_id                                       
    set select_atoms [atomselect top "all"]
    $select_atoms set segname $chain_id                  
    $select_atoms writepdb ${chain_id}.pdb  

	#神秘的東西
    segment ${chain_id} {pdb ${chain_id}.pdb}            
    coordpdb ${chain_id}.pdb ${chain_id}
	
    guesscoord                                           
    regenerate angles dihedrals 
	
    $select_atoms delete   
	
    file delete ${chain_id}.pdb                          
}                                       
writepdb complete_ARG.pdb                                 
writepsf complete_ARG.psf                                 
resetpsf                                                
