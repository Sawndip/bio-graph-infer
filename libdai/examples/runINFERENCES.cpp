/*  This file is part of libDAI - http://www.libdai.org/
 *
 *  Copyright (c) 2006-2011, The libDAI authors. All rights reserved.
 *
 *  Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
 */

#include <dai/alldai.h>
#include <iostream>
#include <fstream>
#include <string>

using namespace std;
using namespace dai;

int main() {
	// This is the INFERENCE/EM engine, derived from the 
    // libDAI example program (example_sprinkler_em)
    // (http://www.cs.ubc.ca/~murphyk/Bayes/bnintro.html)
    //
    // The factor graph file (input.fg) has to be generated first
	// and the data file (sprinkler.tab),
	// as well as the EM commands 

    // Read the factorgraph from the file
    FactorGraph Network;
    Network.ReadFromFile( "learned.fg" );

    // Prepare BP object for doing exact inference for E-step
    PropertySet infprops;
    infprops.set( "verbose", (size_t)1 );
    infprops.set( "updates", string("HUGIN") );
    infprops.set( "maxiter", string("1000") );
    infprops.set( "tol", string("0.00001") );
    infprops.set( "logdomain", true);
    infprops.set( "updates", string("SEQFIX") );
    InfAlg* inf = newInfAlg("BP", Network, infprops );
    inf->init();

    // Read sample from file
    Evidence e;
    ifstream estream( "test.tab" );
    e.addEvidenceTabFile( estream, Network );
    cout << "Number of samples: " << e.nrSamples() << endl;

	// Output sample likelihoods
	cout << endl << "likelihoods" << endl; 
    for( Evidence::const_iterator ei = e.begin(); ei != e.end(); ++ei ) {
        InfAlg* clamped = inf->clone();
        // Apply evidence
        for( Evidence::Observation::const_iterator i = ei->begin(); i != ei->end(); ++i )
            clamped->clamp( clamped->fg().findVar(i->first), i->second );
        clamped->init();
        clamped->run();

        Real sample_logZ = clamped->logZ();
		cout << sample_logZ << endl;

		// output variable posterior inferences for this Sample
  		for (size_t i = 0; i < Network.nrVars(); ++i) 
		{

			// get the belief states for this variable
      		const Var& v = Network.var(i);
			Factor belief = clamped->belief(v);
      		vector<double> posteriors;
      		bool beliefEqualOne = false;
      		for (size_t j = 0; j < belief.nrStates(); ++j)
			{
	  			if(belief[j] == 1)
	    		{
	      			beliefEqualOne = true;
	      			break;
	    		}
	  			posteriors.push_back(belief[j]);
			}	

	  		double down = posteriors[0];
	  		double nc = posteriors[1];
	  		double up = posteriors[2];

	  		if (nc > down && nc > up)
	    		cout << "0";
	  		else if (down > up)
	    		cout << (-1.0*down);
	  		else
	    		cout << up;

			cout << "\t";
		}
      	cout << endl;

        delete clamped;
    }
	// InfAlg* cloned = inf->clone();
	// cloned->run()
	// cout << l << endl;

    delete inf;

    return 0;
}
