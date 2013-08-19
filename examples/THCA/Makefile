

trainTest:
	mkdir $@
	../../bin/bioGraphTrain --no_shared_em --pathway input-processed/pathway.tab --obs input-processed/obs.tab --output trainTest --libdaiBIN ../../bin/runEM_BP > trainTest/em.summary
	../../bin/bioGraphTest --pathway input-processed/pathway.tab --obs input-processed/obs.tab --output trainTest --libdaiBIN ../../bin/runINFERENCES --fg trainTest/learned.fg > trainTest/learned.sll

