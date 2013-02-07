This sample test case describes the following pathway:

	A -> B -> D -| E
	  -> C -> 

And we have the following logic:

	A strongly activates B (and is the only activator) meaning:	
		- When A is active, B is always active
		- When A is inactive, B is always inactive
	
	A weakly activates C:
		- When A is active, C is often active
		- When A is inactive, C is more likely to be inactive
	
	B and C strongly activate D (but C is stronger):
		- When either is active, D is usually active
		- When either is inactive, D is usually inactive
		- When both are active or inactive, D always follows suit
	
	D weakly inactivates E

The first 16 (A-P) samples fit the pattern, but the last two are noise
