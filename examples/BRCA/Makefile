
input-2:
	
	./makeOBS_GRAPH -n data/small.pathway.sif -m data/MEMO_calls.tab -e data/BRCA.exp.547.centered.to.22normals.txt -t data/down.lst -f data/superpathway.sif -z 0.5 --output_files input/obs.tab:input/pathway.tab

test:
	../../bin/bioGraphTrain --pathway input/pathway.tab --obs input/obs.tab --output output --libdaiBIN ../../bin/runEM_BP > output/em.summary
	../../bin/bioGraphTest --pathway input/pathway.tab --obs input/obs.tab --output output --libdaiBIN ../../bin/runINFERENCES --fg output/learned.fg > output/learned.sll

test-basal:
	../../bin/bioGraphTrain --no_shared_em --pathway input/pathway.tab --obs basal/obs.tab --output basal --libdaiBIN ../../bin/runEM_BP > basal/em.summary
	../../bin/bioGraphTest --pathway input/pathway.tab --obs basal/obs.tab --output basal --libdaiBIN ../../bin/runINFERENCES --fg basal/learned.fg > basal/learned.sll

test-lumA:
	../../bin/bioGraphTrain --no_shared_em --pathway input/pathway.tab --obs lumA/obs.tab --output lumA --libdaiBIN ../../bin/runEM_BP > lumA/em.summary
	../../bin/bioGraphTest --pathway input/pathway.tab --obs lumA/obs.tab --output lumA --libdaiBIN ../../bin/runINFERENCES --fg lumA/learned.fg > lumA/learned.sll

clean: 
	rm -f basal-training/learned.fa 
	rm -f lumA-training/learned.fa 
	rm -f basal-train-basal-test/learned.sll 
	rm -f basal-train-lumA-test/learned.sll 
	rm -f lumA-train-basal-test/learned.sll 
	rm -f lumA-train-lumA-test/learned.sll
	rm -f basal.train.in
	rm -f lumA.train.in

testx: basal-train-basal-test/learned.sll basal-train-lumA-test/learned.sll

all: basal-training/learned.fa lumA-training/learned.fa basal-train-basal-test/learned.sll basal-train-lumA-test/learned.sll lumA-train-basal-test/learned.sll lumA-train-lumA-test/learned.sll lumA.train.in basal.train.in

basal-training/learned.fa:
	join.pl input/obs.tab basal-training/samples.lst > basal-training/obs.tab
	../../bin/bioGraphTrain --no_shared_em --pathway input/pathway.tab --obs basal-training/obs.tab --output basal-training --libdaiBIN ../../bin/runEM_BP > basal-training/em.summary

lumA-training/learned.fa:
	join.pl input/obs.tab lumA-training/samples.lst > lumA-training/obs.tab
	../../bin/bioGraphTrain --no_shared_em --pathway input/pathway.tab --obs lumA-training/obs.tab --output lumA-training --libdaiBIN ../../bin/runEM_BP > lumA-training/em.summary

# get sample likelihoods from on basal basal trained
basal-train-basal-test/learned.sll:
	join.pl input/obs.tab basal-test/samples.lst > basal-test/obs.tab
	../../bin/bioGraphTest --no_shared_em --pathway input/pathway.tab --obs basal-test/obs.tab --output basal-train-basal-test --libdaiBIN ../../bin/runINFERENCES --fg basal-training/learned.fg > $@

# use the basal trained factor graph
basal-train-lumA-test/learned.sll:
	join.pl input/obs.tab lumA-test/samples.lst > lumA-test/obs.tab
	../../bin/bioGraphTest --no_shared_em --pathway input/pathway.tab --obs lumA-test/obs.tab --output basal-train-lumA-test --libdaiBIN ../../bin/runINFERENCES --fg basal-training/learned.fg > $@

# get sample likelihoods from on basal basal trained
lumA-train-basal-test/learned.sll:
	join.pl input/obs.tab basal-test/samples.lst > basal-test/obs.tab
	../../bin/bioGraphTest --no_shared_em --pathway input/pathway.tab --obs basal-test/obs.tab --output lumA-train-basal-test --libdaiBIN ../../bin/runINFERENCES --fg lumA-training/learned.fg > $@

# use the basal trained factor graph
lumA-train-lumA-test/learned.sll:
	join.pl input/obs.tab lumA-test/samples.lst > lumA-test/obs.tab
	../../bin/bioGraphTest --no_shared_em --pathway input/pathway.tab --obs lumA-test/obs.tab --output lumA-train-lumA-test --libdaiBIN ../../bin/runINFERENCES --fg lumA-training/learned.fg > $@

lumA.train.in:
	echo "subtype	logl" > $@
	cut -f 2 lumA-train-basal-test/learned.sll  | grep -v ' ' | sed -e 's/^/BASAL	/' >> $@
	cut -f 2 lumA-train-lumA-test/learned.sll  | grep -v ' ' | sed -e 's/^/LUM_A	/' >> $@

basal.train.in:
	echo "subtype	logl" > $@
	cut -f 2 basal-train-basal-test/learned.sll  | grep -v ' ' | sed -e 's/^/BASAL	/' >> $@
	cut -f 2 basal-train-lumA-test/learned.sll  | grep -v ' ' | sed -e 's/^/LUM_A	/' >> $@

plot: lumA.train.in basal.train.in
	./densities.R
	
compare:

	echo "LumA Trained:"
		
	echo "Test on LumA Samples:"
	echo $(shell sort -n -k 2 lumA-train-lumA-test/learned.sll  | transpose.pl | sed -e 's/^/index	/' | row_stats.pl -mean | grep index | cut -f 2)
	sleep 2

	echo "Test on Basal Samples:"
	echo $(shell sort -n -k 2 lumA-train-basal-test/learned.sll  | transpose.pl | sed -e 's/^/index	/' | row_stats.pl -mean | grep index | cut -f 2)
	sleep 2

	echo ""
	echo ""

	echo "Basal Trained:"
		
	echo "Test on Basal Samples:"
	echo $(shell sort -n -k 2 basal-train-basal-test/learned.sll  | transpose.pl | sed -e 's/^/index	/' | row_stats.pl -mean | grep index | cut -f 2)
	sleep 2
	echo "Test on LumA Samples:"
	echo $(shell sort -n -k 2 basal-train-lumA-test/learned.sll  | transpose.pl | sed -e 's/^/index	/' | row_stats.pl -mean | grep index | cut -f 2)
