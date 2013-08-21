

labelSanityCheck:
	mkdir $@
	../../bin/bioGraphTrain --no_shared_em --pathway input-processed/pathway.tab --obs input-processed/obs.tab --output $@ --libdaiBIN ../../bin/runEM_BP > $@/em.summary
	../../bin/bioGraphTest --pathway input-processed/pathway.tab --obs input-processed/obs.tab --output $@ --libdaiBIN ../../bin/runINFERENCES --fg $@/learned.fg > $@/learned.sll
	join.pl input/braf.status.tab $@/learned.sll  | cut -f 1,2,4
