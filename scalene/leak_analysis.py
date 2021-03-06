import math
import numpy as np
from numpy.random import default_rng
from typing import Any, List, Tuple

rng = default_rng()


def log(x: float) -> float:
    """Redefine log so that if x is 0, log x is 0."""
    if x == 0:
        return 0
    else:
        return math.log(x)


def xform(i: float, n: int) -> float:
    return i / n * log(i / n)


def normalized_entropy(v: List[float]) -> float:
    """Returns a value between 0 (all mass concentrated in one item) and 1 (uniformly spread)."""
    assert len(v) > 0
    if len(v) == 1:
        return 1
    n = int(np.nansum(v))
    assert n > 0
    h = -sum([xform(i, n) for i in v])
    return h / math.log(len(v))


def multinomial_pvalue(vec: List[float], trials: int = 2000) -> float:
    """Returns the empirical likelihood (via Monte Carlo trials) of randomly finding a vector with as low entropy as this one."""
    n = np.nansum(vec)
    newvec = list(filter(lambda x: not np.isnan(x), vec))
    m = len(newvec)
    ne = normalized_entropy(newvec)
    sampled_vec = rng.multinomial(n, [1 / m for i in range(m)], trials)
    # Return the fraction of times the sampled vector has no more entropy than the original vector
    return sum(normalized_entropy(v) <= ne for v in sampled_vec) / trials


def argmax(vec: List[Any]) -> int:
    """Return the (first) index with the maximum value."""
    m = np.nanmax(vec)
    for (index, value) in enumerate(vec):
        if value == m:
            return index
    return 0  # never reached


def harmonic_number(n: int) -> float:
    """Returns an approximate value of n-th harmonic number.

    http://en.wikipedia.org/wiki/Harmonic_number

    """
    if n < 100:
        return sum(1 / d for d in range(2, n + 1))
    # Euler-Mascheroni constant
    gamma = 0.57721566490153286060651209008240243104215933593992
    return (
        gamma
        + math.log(n)
        + 0.5 / n
        - 1.0 / (12 * n ** 2)
        + 1.0 / (120 * n ** 4)
    )


def outliers(
    vec: List[float], alpha: float = 0.01, trials: int = 3000
) -> List[Tuple[int, float]]:
    """Returns the indices with values that are significant outliers, with their p-values"""
    m = len(vec)
    removed = 0
    results = []
    pv = multinomial_pvalue(vec, trials)
    # We use the Benjamin-Yekutieli procedure to control false-discovery rate.
    # See https://en.wikipedia.org/wiki/False_discovery_rate#Benjamini%E2%80%93Yekutieli_procedure
    c_m = harmonic_number(m)
    while pv <= alpha * (removed + 1) / (m * c_m) and removed < m:
        # While we remain below the threshold, remove (zero-out by
        # setting to NaN) the max and add its index to the list of
        # results with its p-value.
        max_index = argmax(vec)
        results.append((max_index, pv))
        vec[max_index] = np.nan
        removed += 1
        if removed < m:
            pv = multinomial_pvalue(vec)
    return results


if __name__ == "__main__":
    # Run a simple test.
    print(outliers([1000, 8, 8, 1, 0], alpha=0.01, trials=10000))
    print(outliers([8, 8, 1, 0], alpha=0.01, trials=10000))
    print(outliers([8, 1, 0], alpha=0.01, trials=10000))
    print(outliers([1, 0], alpha=0.01, trials=10000))
