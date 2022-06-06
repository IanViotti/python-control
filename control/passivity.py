'''
Author: Mark Yeatman  
Date: May 15, 2022
'''

from . import statesp as ss
import numpy as np
import cvxopt as cvx


def is_passive(sys):
    '''
    Indicates if a linear time invarient system is passive

    Constructs a linear matrix inequality and a feasibility optimization
    such that is a solution exists, the system is passive.

    The source for the algorithm is: 
    McCourt, Michael J., and Panos J. Antsaklis. "Demonstrating passivity and dissipativity using computational methods." ISIS 8 (2013).
    '''

    A = sys.A
    B = sys.B
    C = sys.C
    D = sys.D

    def make_LMI_matrix(P):
        V = np.vstack((
            np.hstack((A.T @ P + P@A, P@B)),
            np.hstack((B.T@P, np.zeros_like(D))))
        )
        return V

    P = np.zeros_like(A)
    matrix_list = []
    state_space_size = A.shape[0]
    for i in range(0, state_space_size):
        for j in range(0, state_space_size):
            if j <= i:
                P = P*0.0
                P[i, j] = 1.0
                P[j, i] = 1.0
                matrix_list.append(make_LMI_matrix(P).flatten())

    coefficents = np.vstack(matrix_list).T

    constants = -np.vstack((
        np.hstack((np.zeros_like(A),  - C.T)),
        np.hstack((- C, -D - D.T)))
    )

    number_of_opt_vars = int(
        (state_space_size**2-state_space_size)/2 + state_space_size)
    c = cvx.matrix(0.0, (number_of_opt_vars, 1))

    # crunch feasibility solution
    sol = cvx.solvers.sdp(c,
                          Gs=[cvx.matrix(coefficents)],
                          hs=[cvx.matrix(constants)])

    return (sol["x"] is not None)
