import numpy as np
from scipy import linalg

def find_null_space(matrix):
    """
    Find the null space of a matrix.
    
    Args:
        matrix: A 2D numpy array or list of lists
        
    Returns:
        A matrix whose columns form a basis for the null space
    """
    # Convert input to numpy array if it's not already
    A = np.array(matrix, dtype=float)
    
    # Compute the SVD
    u, s, vh = linalg.svd(A, full_matrices=True)
    
    # Find the rank of the matrix
    tol = max(A.shape) * np.spacing(max(s))
    rank = np.sum(s > tol)
    
    # Extract the basis vectors of the null space
    null_space = vh[rank:].T.conj()
    
    return null_space