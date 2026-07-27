import numpy as np
import matplotlib.pyplot as plt

from bits_and_pam_skeleton import get_pam_constellation

def get_decision_boundaries(constellation):
    """
    Midpoints between adjacent constellation points, dividing maximum
    likelihood decision regions.
    """
    # Zeros as placeholder.
    constellation = list(constellation.values())
    step = np.abs(constellation[0] - constellation[1])
    first = constellation[0] + step / 2
    last = constellation[-1] - step / 2
    boundaries = np.arange(first, last+step/2, step)
    return boundaries

def pam_detect(symbols, M):
    """
    Detect noisy M-PAM symbols.
    """

    constellation_symbols = get_pam_constellation(M).values()

    detected_symbols = np.zeros_like(symbols)
    for i, symbol in enumerate(symbols):
        lowest_difference = float('inf')
        best_symbol = 0
        for const in constellation_symbols:
            difference = np.abs(const - symbol)
            if difference < lowest_difference:
                best_symbol = const
                lowest_difference = difference
        detected_symbols[i] = best_symbol
    return detected_symbols


def main():
    # Plot the decision boundaries for M = 4.
    M = 4
    constellation = get_pam_constellation(M)
    boundaries = get_decision_boundaries(constellation)

    plt.scatter(constellation.values(), np.zeros(len(constellation)))
    for b in boundaries:
        plt.axvline(b, color='red', linestyle='--')
    plt.show()

    # Plot the decision boundaries for M = 2.
    M = 2
    constellation = get_pam_constellation(M)
    boundaries = get_decision_boundaries(constellation)

    plt.scatter(constellation.values(), np.zeros(len(constellation)))
    for b in boundaries:
        plt.axvline(b, color='red', linestyle='--')
    plt.show()

    # Check correct detection of some 2-PAM symbols.
    M = 2
    true_symbols = np.array([-1, -1, 1, 1, 1, -1, 1, 1], dtype=np.int16)
    noisy_symbols = np.array([-1.3, -0.8, 0.7, 1.2, 1.3, -1.1, 0.9, 0.1])

    # Ones as placeholder.
    recovered_symbols = np.ones_like(true_symbols)
    recovered_symbols = pam_detect(noisy_symbols, M)
    print(recovered_symbols)
    print(true_symbols)
    if np.allclose(recovered_symbols, true_symbols):
        print(f"{M}-PAM symbols correctly recovered.")
    else:
        print(f"Oops! {M}-PAM symbols incorrectly recovered.")

    # Check correct detection of some 2-PAM symbols.
    M = 4
    true_symbols = np.array([-1.34164079, 1.34164079, 1.34164079, -1.34164079, -1.34164079, 0.4472136, -0.4472136, 0.4472136, -0.4472136, -0.4472136, -1.34164079, -0.4472136, 0.4472136, -1.34164079, -1.34164079, 0.4472136, -1.34164079, -1.34164079, 0.4472136, -0.4472136, 1.34164079, 1.34164079, 1.34164079, -0.4472136])
    noisy_symbols = np.array([-1.29885344, 1.51067178, 1.27346044, -1.36176538, -1.20955208, 0.49441782, -0.5498247, 0.48097023, -0.5553971, -0.42218183, -1.28329794, -0.56218162, 0.3096351, -1.28516732, -1.24598501, 0.46476806, -1.37153408, -1.4629337, 0.60845302, -0.47322956, 1.28766264, 1.31981053, 1.26053366, -0.54125534])

    # Ones as placeholder.
    # recovered_symbols = np.ones_like(true_symbols)
    recovered_symbols = pam_detect(noisy_symbols, M)
    print(recovered_symbols)
    print(true_symbols)
    if np.allclose(recovered_symbols, true_symbols):
        print(f"{M}-PAM symbols correctly recovered.")
    else:
        print(f"Oops! {M}-PAM symbols incorrectly recovered.")


if __name__ == "__main__":
    main()
