
import numpy as np
from yamata import *


def ProducerConsumerEx():
    code = '''
        [c b d] :=0;
        {
            loop
                if # M0[c] -> 
                        <H[b]; X[c]>
                    # M1[c] -> skip 
                end
            end
            ||
            loop
				if # M0[c] -> skip
					# M1[c] ->
						<SWAP[b d]; X[c]>;

						// an arbitrary operation here
						if # M0[d] -> skip # M1[d] -> skip end;
						d :=0
				end
            end
        }
    '''
    vec = np.array([1., 0., 0., 0., 0., 0., 0., 0.])
    vinit = VVec(QVar(['c', 'b', 'd']), vec)

    fc = compile(code)
    fc.show("output/flowchart")

    # vec sim
    print(vecsim(fc, vinit, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vinit.outer(), 12)
    qts.show("output/qts")
    qts.reduce().show("output/reduced_qts")
