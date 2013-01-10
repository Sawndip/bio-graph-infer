

test:
	../../bin/bioGraphInfer --pathway input/pathway.tab --obs input/obs.tab --output output --libdaiBIN ../../bin/runEM
	#cd output && ../../../bin/runEM > learned.fg

test-part:
	../../bin/bioGraphInfer --pathway input/pathway.tab --obs input/obs.partial.tab --output output --libdaiBIN ../../bin/runEM
	#cd output && ../../../bin/runEM > learned.fg
