r"""
Tools for working with polytopes in SageMath, with a focus on computational geometry.

Features:

- simpler matrix-vector `(A, b)` polytope constructor
- support functions computation through the MIP interface
- a bunch of commonly used functions, which do not require the double description 
  of the polytope, including Chebyshev center, Radius, Diameter, Opposite polyhedron.
   
AUTHOR:

- Marcelo Forets (Oct 2016 at VERIMAG - UGA)

Last modified: 2017-04-09
"""

#************************************************************************
#       Copyright (C) 2016 Marcelo Forets <mforets@nonlinearnotes.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#                  http://www.gnu.org/licenses/
#************************************************************************

# Sage rings
from sage.rings.rational_field import QQ
from sage.rings.real_double import RDF

# Sage common constructors
from sage.geometry.polyhedron.constructor import Polyhedron
from sage.matrix.constructor import matrix, vector
from sage.modules.free_module_element import zero_vector
from sage.matrix.special import identity_matrix

# Misc methods
from sage.geometry.polyhedron.misc import _make_listlist
from sage.functions.other import sqrt
from sage.rings.infinity import Infinity as oo

def polyhedron_to_Hrep(P, separate_equality_constraints = False):
    r"""Extract half-space representation of polytope. 
    
    By default, returns matrices ``[A, b]`` representing `P` as `Ax \leq b`. 
    If ``separate_equality_constraints = True``, returns matrices ``[A, b, Aeq, beq]``, 
    with separated inequality and equality constraints.

    INPUT:

    * ``P`` - object of class polyhedron

    * ``separate_equality_constraints`` - (default = False) If True, returns ``Aeq``, ``beq`` containing the equality constraints, 
    removing the corresponding lines from ``A`` and ``b``.

    OUTPUT:

    * ``[A, b]`` - dense matrix and vector respectively (dense, ``RDF``).

    * ``[A, b, Aeq, beq]`` - (if the flag separate_equality_constraints is True), matrices and vectors (dense, ``RDF``). 
    
    NOTES:
        
    - Equality constraints are removed from A and put into Aeq.
    - This function is used to revert the job of ``polyhedron_from_Hrep(A, b, base_ring = RDF)``. 
    - However, it is not the inverse generally, because of: 
        - automatic reordering of rows (this is uncontrolled, internal to Polyhedron), and 
        - scaling. In the example of above, with a polyhedron in RDF we see reordering of rows.    
        
    EXAMPLES::

        sage: A = matrix(RDF, [[-1.0, 0.0,  0.0,  0.0,  0.0,  0.0],
        ....: [ 1.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        ....: [ 0.0,  1.0,  0.0,  0.0,  0.0,  0.0],
        ....: [ 0.0, -1.0,  0.0,  0.0,  0.0,  0.0],
        ....: [0.0,  0.0, -1.0,  0.0,  0.0,  0.0],
        ....: [0.0,  0.0,  1.0,  0.0,  0.0,  0.0],
        ....: [0.0,  0.0,  0.0, -1.0,  0.0,  0.0],
        ....: [0.0,  0.0,  0.0,  1.0,  0.0,  0.0],
        ....: [0.0,  0.0,  0.0,  0.0,  1.0,  0.0],
        ....: [0.0,  0.0,  0.0,  0.0, -1.0,  0.0],
        ....: [0.0,  0.0,  0.0,  0.0,  0.0,  1.0],
        ....: [0.0,  0.0,  0.0,  0.0,  0.0, -1.0]])
        sage: b = vector(RDF, [0.0, 10.0, 0.0, 0.0, 0.2, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0])
        sage: from polyhedron_tools.misc import polyhedron_from_Hrep, polyhedron_to_Hrep
        sage: P = polyhedron_from_Hrep(A, b, base_ring = RDF); P
        A 3-dimensional polyhedron in RDF^6 defined as the convex hull of 8 vertices
        sage: [A, b] = polyhedron_to_Hrep(P)
        sage: A
        [-0.0  1.0 -0.0 -0.0 -0.0 -0.0]
        [ 0.0 -1.0  0.0  0.0  0.0  0.0]
        [-0.0 -0.0 -0.0 -0.0  1.0 -0.0]
        [ 0.0  0.0  0.0  0.0 -1.0  0.0]
        [-0.0 -0.0 -0.0 -0.0 -0.0  1.0]
        [ 0.0  0.0  0.0  0.0  0.0 -1.0]
        [-1.0 -0.0 -0.0 -0.0 -0.0 -0.0]
        [ 1.0 -0.0 -0.0 -0.0 -0.0 -0.0]
        [-0.0 -0.0 -1.0 -0.0 -0.0 -0.0]
        [-0.0 -0.0  1.0 -0.0 -0.0 -0.0]
        [-0.0 -0.0 -0.0 -1.0 -0.0 -0.0]
        [-0.0 -0.0 -0.0  1.0 -0.0 -0.0]
        sage: b
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.2, 0.2, 0.1, 0.1) 
        
    TESTS:: 
    
    If we choose QQ, then we have both reordering and rescaling::

        sage: P = polyhedron_from_Hrep(A, b, base_ring = QQ); P
        A 3-dimensional polyhedron in QQ^6 defined as the convex hull of 8 vertices

        sage: [A, b] = polyhedron_to_Hrep(P)
        sage: A
        [  0.0   0.0   0.0   0.0   0.0  -1.0]
        [  0.0   0.0   0.0   0.0   0.0   1.0]
        [  0.0   0.0   0.0   0.0  -1.0   0.0]
        [  0.0   0.0   0.0   0.0   1.0   0.0]
        [  0.0  -1.0   0.0   0.0   0.0   0.0]
        [  0.0   1.0   0.0   0.0   0.0   0.0]
        [ -1.0   0.0   0.0   0.0   0.0   0.0]
        [  0.0   0.0   5.0   0.0   0.0   0.0]
        [  0.0   0.0  -5.0   0.0   0.0   0.0]
        [  0.0   0.0   0.0 -10.0   0.0   0.0]
        [  0.0   0.0   0.0  10.0   0.0   0.0]
        [  1.0   0.0   0.0   0.0   0.0   0.0]
        sage: b
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 10.0)

    The polytope P is not full-dimensional. To extract the equality constraints we use the flag ``separate_equality_constraints``::

        sage: [A, b, Aeq, beq] = polyhedron_to_Hrep(P, separate_equality_constraints = True)
        sage: A
        [ -1.0   0.0   0.0   0.0   0.0   0.0]
        [  0.0   0.0   5.0   0.0   0.0   0.0]
        [  0.0   0.0  -5.0   0.0   0.0   0.0]
        [  0.0   0.0   0.0 -10.0   0.0   0.0]
        [  0.0   0.0   0.0  10.0   0.0   0.0]
        [  1.0   0.0   0.0   0.0   0.0   0.0]
        sage: b
        (0.0, 1.0, 1.0, 1.0, 1.0, 10.0)
        sage: Aeq
        [ 0.0  0.0  0.0  0.0  0.0 -1.0]
        [ 0.0  0.0  0.0  0.0 -1.0  0.0]
        [ 0.0 -1.0  0.0  0.0  0.0  0.0]
        sage: beq
        (0.0, 0.0, 0.0)
"""
    if not separate_equality_constraints:
        # a priori I don't know number of equalities; actually m may be bigger than len(P.Hrepresentation()) !
        # for this, we should transform equalities into inequalities, so that Ax <= b is correct.
        b = list(); A = list()

        P_gen = P.Hrep_generator();

        for pigen in P_gen:
            if (pigen.is_equation()):
                pi_vec = pigen.vector()
                A.append(-pi_vec[1:len(pi_vec)])
                b.append(pi_vec[0])

                A.append(pi_vec[1:len(pi_vec)])
                b.append(pi_vec[0])

            else:
                pi_vec = pigen.vector()
                A.append(-pi_vec[1:len(pi_vec)])
                b.append(pi_vec[0])

        return [matrix(RDF, A), vector(RDF, b)]

    else:
        b = list(); A = list(); beq = list(); Aeq = list()

        P_gen = P.Hrep_generator();

        for pigen in P_gen:
            if (pigen.is_equation()):
                pi_vec = pigen.vector()
                Aeq.append(-pi_vec[1:len(pi_vec)])
                beq.append(pi_vec[0])

            else:
                pi_vec = pigen.vector()
                A.append(-pi_vec[1:len(pi_vec)])
                b.append(pi_vec[0])

    return [matrix(RDF, A), vector(RDF, b), matrix(RDF, Aeq), vector(RDF, beq)]
        
def polyhedron_from_Hrep(A, b, base_ring=QQ):
    r"""Builds a polytope given the H-representation, in the form `Ax \leq b`

    INPUT:

    * ``A`` - matrix of size m x n, in RDF or QQ ring. Accepts generic Sage matrix, and also a Numpy arrays with a matrix shape.

    * ``b`` - vector of size m, in RDF or QQ ring. Accepts generic Sage matrix, and also a Numpy array.

    * ``base_ring`` - (default: ``QQ``). Specifies the ring (base_ring) for the Polyhedron constructor. Valid choices are:

        * ``QQ`` - rational. Uses ``'ppl'`` (Parma Polyhedra Library) backend

        * ``RDF`` - Real double field. Uses ``'cdd'`` backend.

    OUTPUT:

    * "P" - a Polyhedron object

    TO-DO:

    * accept numpy arrays. notice that we often handle numpy arrays (for instance if we load some data from matlab using the function
    ``scipy.io.loadmat(..)``, then the data will be loaded as a dictionary of numpy arrays)

    EXAMPLES::

        sage: A = matrix(RDF, [[-1.0, 0.0,  0.0,  0.0,  0.0,  0.0],
        ....: [ 1.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        ....: [ 0.0,  1.0,  0.0,  0.0,  0.0,  0.0],
        ....: [ 0.0, -1.0,  0.0,  0.0,  0.0,  0.0],
        ....: [ 0.0,  0.0, -1.0,  0.0,  0.0,  0.0],
        ....: [ 0.0,  0.0,  1.0,  0.0,  0.0,  0.0],
        ....: [ 0.0,  0.0,  0.0, -1.0,  0.0,  0.0],
        ....: [ 0.0,  0.0,  0.0,  1.0,  0.0,  0.0],
        ....: [ 0.0,  0.0,  0.0,  0.0,  1.0,  0.0],
        ....: [ 0.0,  0.0,  0.0,  0.0, -1.0,  0.0],
        ....: [ 0.0,  0.0,  0.0,  0.0,  0.0,  1.0],
        ....: [ 0.0,  0.0,  0.0,  0.0,  0.0, -1.0]])
        sage: b = vector(RDF, [0.0, 10.0, 0.0, 0.0, 0.2, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0])
        sage: from polyhedron_tools.misc import polyhedron_from_Hrep
        sage: P = polyhedron_from_Hrep(A, b, base_ring=QQ); P
        A 3-dimensional polyhedron in QQ^6 defined as the convex hull of 8 vertices

    NOTES:

    - This function is useful especially when the input matrices `A`, `b` are ill-defined 
    (constraints that differ by tiny amounts making the input data to be degenerate or almost degenerate), 
    causing problems to Polyhedron(...). 
    
    - In this case it is recommended to use ``base_ring = QQ``. Each element of `A` and `b` will be converted to rational, and this will be sent to Polyhedron.
     Note that Polyhedron automatically removes redundant constraints.
    """
    
    if (base_ring == RDF):

        if 'numpy.ndarray' in str(type(A)):
            # assuming that b is also a numpy array
            m = A.shape[0]; n = A.shape[1];

            b_RDF = vector(RDF, m, [RDF(bi) for bi in b])

            A_RDF = matrix(RDF, m, n)
            for i in range(m):
                A_RDF.set_row(i, [RDF(A[i][j]) for j in range(n)])

            A = copy(A_RDF);
            b = copy(b_RDF);

        ambient_dim = A.ncols()

        # transform to real, if needed
        if A.base_ring() != RDF:
            A.change_ring(RDF)

        if b.base_ring() != RDF:
            b.change_ring(RDF)

        ieqs_list = []
        for i in range(A.nrows()):
            ieqs_list.append(list(-A.row(i)))  #change in sign, necessary since Polyhedron receives Ax+b>=0
            ieqs_list[i].insert(0,b[i])

        P = Polyhedron(ieqs = ieqs_list, base_ring=RDF, ambient_dim=A.ncols(), backend='cdd')

    elif (base_ring == QQ):

        if 'numpy.ndarray' in str(type(A)):
            # assuming that b is also a numpy array
            m = A.shape[0]; n = A.shape[1];

            b_QQ = vector(QQ, m, [QQ(b[i]) for i in range(m)])
            A_QQ = matrix(QQ, m, n)

            for i in range(m):
                A_QQ.set_row(i, [QQ(A[i][j]) for j in range(n)])

            A = copy(A_QQ);
            b = copy(b_QQ);

        ambient_dim = A.ncols()

        # transform to rational, if needed
        if A.base_ring() != QQ:
            #for i in range(A.nrows()):
            #    A.set_row(i,[QQ(A.row(i)[j]) for j in range(ambient_dim)]);
            A.change_ring(QQ)

        if b.base_ring() != QQ:
            #b = vector(QQ, [QQ(bi) for bi in b]);
            b.change_ring(QQ)

        ieqs_list = []
        for i in range(A.nrows()):
            ieqs_list.append(list(-A.row(i)))  #change in sign, necessary since Polyhedron receives Ax+b>=0
            ieqs_list[i].insert(0,b[i])

        P = Polyhedron(ieqs = ieqs_list, base_ring=QQ, ambient_dim=A.ncols(), backend = 'ppl')

    else:
        raise ValueError('Base ring not supported. Try with RDF or QQ.')

    return P
        
def chebyshev_center(P=None, A=None, b=None):
    r"""Compute the Chebyshev center of a polytope.

    The Chebyshev center of a polytope is the center of the largest hypersphere 
    enclosed by the polytope.

    INPUT:

    * ``A, b`` - Matrix and vector representing the polyhedron, as `Ax \leq b`.

    * ``P`` - Polyhedron object.

    OUTPUT:

    * The Chebyshev center, as a vector; the base ring of ``P`` preserved.

    """
    from sage.numerical.mip import MixedIntegerLinearProgram
    
    # parse input
    got_P, got_Ab = False, False;
    if (P is not None):
        if (A is None) and (b is None):
            got_P = True
        elif (A is not None) and (b is None):
            b, A = A, P; P = [];
            got_Ab = True
    else:
        got_Ab = True if (A is not None and b is not None) else False

    if got_Ab or got_P:
        if got_P:
            [A, b] = polyhedron_to_Hrep(P)

        base_ring = A.base_ring()
        p = MixedIntegerLinearProgram (maximization = True)
        x = p.new_variable ()
        r = p.new_variable ()
        n = A.nrows ()
        m = A.ncols ()
        if not n == b.length () :
            return []
        for i in range (0, n) :
            v = A.row (i)
            norm = sqrt (v.dot_product (v))
            p.add_constraint (sum ([v[j]*x[j] for j in range (0, m)]) + norm * r[0] <= b[i])
        f = sum ([0*x[i] for i in range (0, m)]) + 1 * r[0]
        p.set_objective(f)
        p.solve()
        cheby_center = [base_ring(p.get_values (x[i])) for i in range (0, m)]
        return vector(cheby_center)
    else:
        raise ValueError('The input should be either as a Polyhedron, P, or as matrices, [A, b].')    
    
def radius(P):
    r"""Maximum norm of any element in a polyhedron, with respect to the supremum norm.

    It is defined as `\max\limits_{x in P} \Vert x \Vert_\inf`. It can be computed with support functions as 
    `\max\limits_{i=1,\ldots,n} \max \{|\rho_P(e_i)|, |\rho_P(-e_i)|\}`, 
    where `\rho_P(e_i)` is the support function of `P` evaluated at the i-th canonical vector `e_i`.

    INPUT:

    * ``P`` - an object of class Polyhedron. It can also be given as ``[A, b]`` with A and b matrices, assuming `Ax \leq b`.

    OUTPUT:

    * ``snorm`` - the value of the max norm of any element of P, in the sup-norm.

    TO-DO:

    - To use '*args' so that it works both with ``polyhedron_sup_norm(A, b)`` and with ``polyhedron_sup_norm(P)`` 
    (depending on the number of the arguments). 
    
    - The difference with mult-methods is that they check also for the type of the arguments.
    
    - v = P.bounding_box() # returns the coordinates of a rectangular box containing the polytope
    polyInfNorm = max( vecpnorm(v[i],p='inf') for i in range(len(v)))
    return polyInfNorm
    """
    from polyhedron_tools.misc import support_function
    
    if (type(P) == list):

        A = P[0]; b = P[1];
        # obtain dimension of the ambient space
        n = A.ncols();

        r = 0
        for i in range(n):
            # generate canonical direction
            d = zero_vector(RDF,n)
            d[i] = 1
            aux_sf = abs(support_function([A, b], d))
            if (aux_sf >= r):
                r = aux_sf;

            # change sign
            d[i] = -1
            aux_sf = abs(support_function([A, b], d))
            if (aux_sf >= r):
                r = aux_sf;
        snorm = r
        return snorm    
        
def support_function(P, d, verbose = 0, return_xopt = False, solver = 'GLPK'):
    r"""Compute support function of a convex polytope.

    It is defined as `\max_{x in P} \langle x, d \rangle` , where `d` is an input vector.

    INPUT:

    * ``P`` - an object of class Polyhedron. It can also be given as ``[A, b]`` meaning `Ax \leq b`.

    * ``d`` - a vector (or list) where the support function is evaluated.

    * ``verbose`` - (default: 0) If 1, print the status of the LP.

    * ``solver`` - (default: ``'GLPK'``) the LP solver used.

    * ``return_xopt`` - (default: False) If True, the optimal point is returned, and ``sf = [oval, opt]``.

    OUTPUT:

    * ``sf`` - the value of the support function.

    EXAMPLES::

        sage: from polyhedron_tools.misc import BoxInfty, support_function
        sage: P = BoxInfty([1,2,3], 1); P
        A 3-dimensional polyhedron in QQ^3 defined as the convex hull of 8 vertices
        sage: support_function(P, [1,1,1], return_xopt=True)
        (9.0, {0: 2.0, 1: 3.0, 2: 4.0})

    NOTES:

    - The possibility of giving the input polytope as `[A, b]` instead of a 
    polyhedron is useful in cases when the dimensions are high (in practice, 
    above or around 20, but it depends on the particular system -number of 
    constraints- as well). 
    
    - If a different solver (e.g. ``guurobi``) is given, it should be installed properly.
    """
    from sage.numerical.mip import MixedIntegerLinearProgram

    if (type(P) == list):
        A = P[0]; b = P[1];
    elif P.is_empty():
        # avoid formulating the LP if P = []
        return 0
    else: #assuming some form of Polyhedra
        base_ring = P.base_ring()
        # extract the constraints from P
        m = len(P.Hrepresentation())
        n = len(vector( P.Hrepresentation()[0] ))-1
        b = vector(base_ring, m)
        A = matrix(base_ring, m, n)
        P_gen = P.Hrep_generator();
        i=0
        for pigen in P_gen:
            pi_vec = pigen.vector()
            A.set_row(i, -pi_vec[1:len(pi_vec)])
            b[i] = pi_vec[0]
            i+=1;
            
    s_LP = MixedIntegerLinearProgram(maximization=True, solver = solver)
    x = s_LP.new_variable(integer=False, nonnegative=False)

    # objective function
    obj = sum(d[i]*x[i] for i in range(len(d)))
    s_LP.set_objective(obj)

    s_LP.add_constraint(A * x <= b);

    if (verbose):
        print('**** Solve LP  ****')
        s_LP.show()

    oval = s_LP.solve()
    xopt = s_LP.get_values(x);

    if (verbose):
        print('Objective Value:', oval)
        for i, v in xopt.iteritems():
            print('x_%s = %f' % (i, v))
        print('\n')

    if (return_xopt == True):
        return oval, xopt
    else:
        return oval     
        
def support_function_ellipsoid(Q, d):
    r"""Compute support function of an ellipsoid.

    The ellipsoid is defined as `\max_{x in Q} \langle x, d \rangle`, where 
    `d` is a given vector. The ellipsoid is defined as the set 
    `\{ x \in \mathbb{R}^n : x^T Q x \leq 1\}`.

    INPUT:

    * ``Q`` - a square matrix

    * ``d`` - a vector (or list) where the support function is evaluated

    OUTPUT:

    The value of the support function at `d`.
    """
    if (Q.is_singular()):
        raise ValueError("The coefficient matrix of the ellipsoid is not invertible.")
    
    if (type(d) == list):
        d = vector(d)
    
    return sqrt(d.inner_product((~Q)*d))
                
def BoxInfty(lengths=None, center=None, radius=None, base_ring=QQ, return_HSpaceRep=False):
    r"""Generate a ball in the supremum norm, or more generally a hyper-rectangle in an Euclidean space.

    It can be constructed from its center and radius, in which case it is a box. 
    It can also be constructed giving the lengths of the sides, in which case it is an hyper-rectangle. 
    In all cases, it is defined as the Cartesian product of intervals.

    INPUT:

    * ``args`` - Available options are:

        * by center and radius:

            * ``center`` - a vector (or a list) containing the coordinates of the center of the ball.

            * ``radius`` - a number representing the radius of the ball.

        * by lengths:

            * ``lenghts`` - a list of tuples containing the length of each side with respect to the coordinate axes, in the form [(min_x1, max_x1), ..., (min_xn, max_xn)].

    * ``base_ring`` - (default: ``QQ``) base ring passed to the Polyhedron constructor. Valid choices are:

        * ``'QQ'``: rational

        * ``'RDF'``: real double field

    * ``return_HSpaceRep`` - (default: False) If True, it does not construct the Polyhedron `P`, and returns instead the pairs ``[A, b]`` corresponding to P in half-space representation, and is understood that `Ax \leq b`.

    OUTPUT:

    * ``P`` - a Polyhedron object. If the flag ``return_HSpaceRep`` is true, it is returned as ``[A, b]`` with `A` and `b` matrices, and is understood that `Ax \leq b`.

    EXAMPLES::

        sage: from polyhedron_tools.misc import BoxInfty
        sage: P = BoxInfty([1,2,3], 1); P
        A 3-dimensional polyhedron in QQ^3 defined as the convex hull of 8 vertices
        sage: P.plot(aspect_ratio=1)    # not tested (plot)

    NOTES:

    - The possibility to output in matrix form [A, b] is especially interesting 
    for more than 15 variable systems.
    """
    # Guess input
    got_lengths, got_center_and_radius = False, False;
    if (lengths is not None):
        if (center is None) and (radius is None):
            got_lengths = True
        elif (center is not None) and (radius is None):
            radius = center; center = lengths; lengths = [];
            got_center_and_radius = True
    else:
        got_center_and_radius = True if (center is not None and radius is not None) else False

    # Given center and radius
    if got_center_and_radius:

        # cast (optional)
        center = [base_ring(xi) for xi in center]
        radius = base_ring(radius)

        ndim = len(center)
        A = matrix(base_ring, 2*ndim, ndim);
        b = vector(base_ring,2*ndim)

        count = 0
        for i in range(ndim):
            diri = zero_vector(base_ring,ndim)
            diri[i] = 1

            # external bound
            A.set_row(count, diri)
            b[count] = center[i] + radius
            count += 1

            # internal bound
            A.set_row(count, -diri)
            b[count] = -(center[i] - radius)
            count += 1


    # Given the length of each side as tuples (min, max)
    elif got_lengths:

        # clean up the argument and cast
        lengths = _make_listlist(lengths)
        lengths = [[base_ring(xi) for xi in l] for l in lengths]

        ndim = len(lengths)
        A = matrix(base_ring, 2*ndim, ndim)
        b = vector(base_ring, 2*ndim)

        count = 0
        for i in range(ndim):
            diri = zero_vector(base_ring, ndim)
            diri[i] = 1

            # external bound
            A.set_row(count, diri)
            b[count] = lengths[i][1]
            count += 1

            # internal bound
            A.set_row(count, -diri)
            b[count] = -(lengths[i][0])
            count += 1

    else:
        raise ValueError('You should specify either center and radius or length of the sides.')

    if not return_HSpaceRep:
        P = polyhedron_from_Hrep(A, b, base_ring)
        return P
    else:
        return [A, b]   
    
def opposite_polyhedron(P, base_ring=None):
    r"""Generate the polyhedron whose vertices are oppositve to a given one.

    The opposite polyhedron `-P` is defined as the polyhedron such that `x \in -P` if and only if `-x \in P`. 

    INPUT:

    * ``P`` - an object of class Polyhedron.

    * ``base_ring`` - (default: that of P). The ``base_ring`` passed to construct `-P`.

    OUTPUT:

    A polyhedron whose vertices are opposite to those of `P`.

    EXAMPLES::

        sage: from polyhedron_tools.misc import BoxInfty, opposite_polyhedron
        sage: P = BoxInfty([1,1], 0.5)
        sage: minusP = opposite_polyhedron(P)
        sage: P.plot(aspect_ratio=1) + minusP.plot()    # not tested (plot)

    TO-DO:

    The possibility to receive P in matrix form `(A, b)`.
    """
    if base_ring is None:
        base_ring = P.base_ring()

    return Polyhedron(vertices = [-1*vector(v) for v in P.vertices_list()], base_ring = base_ring)

def diameter_vertex_enumeration(P, p=oo):
    r"""Compute the diameter of a polytope using the V-representation.

    EXAMPLES:

    By default, the supremum norm is used::
    
        sage: from polyhedron_tools.misc import diameter_vertex_enumeration
        sage: diameter_vertex_enumeration(7*polytopes.hypercube(5))
        14

    A custom `p`-norm can be specified as well::

        sage: diameter_vertex_enumeration(7*polytopes.hypercube(2), p=2)
        14*sqrt(2)
    """
    diam = 0
    vlist = P.vertices_list()
    num_vertices = len(vlist)
    for i in range(num_vertices):
        for j in range(i+1, num_vertices):
            dist_vi_vj = (vector(vlist[i]) - vector(vlist[j])).norm(p=p)
            diam = max(diam, dist_vi_vj)
    return diam

def diameter_support_function(A, b):
    r"""Compute the diameter of a polytope using the H-representation.

    The diameter is computed in the supremum norm.

    INPUT:

    Polyhedron in H-representation, `Ax \leq b`.

    OUTPUT:

    - ``diam`` -- scalar, diameter of the polyhedron in the supremum norm

    - ``u`` -- vector with components `u_j = \max x_j` for `x` in `P`

    - ``l`` -- vector with components `l_j = \min x_j` for `x` in `P`

    EXAMPLES::

        sage: from polyhedron_tools.misc import diameter_support_function, polyhedron_to_Hrep
        sage: [A, b] = polyhedron_to_Hrep(7*polytopes.hypercube(5))
        sage: diameter_support_function(A, b)
        (14.0, (7.0, 7.0, 7.0, 7.0, 7.0), (-7.0, -7.0, -7.0, -7.0, -7.0))
    """
    from polyhedron_tools.misc import support_function

    # ambient dimension
    n = A.ncols()

    # number of constraints
    m = A.rows()

    In = identity_matrix(n)

    # lower : min x_j
    l = []
    for j in range(n):
        l += [-support_function([A, b], -In.column(j))]
    l = vector(l)

    # upper : max x_j
    u = []
    for j in range(n):
        u += [support_function([A, b], In.column(j))]
    u = vector(u)

    diam = max(u-l)

    return diam, u, l
