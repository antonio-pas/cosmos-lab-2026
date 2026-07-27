import numpy as np
import matplotlib.pyplot as plt

def generate_gray_encoding(size):
    array = ['0', '1']
    while len(array) < size:
        first_part = list(map(lambda a: '0' + a, array))
        last_part = list(map(lambda a: '1' + a, array[::-1]))
        array = np.concatenate((first_part, last_part))
    return array

def get_pam_constellation(M, Es=1):
    """
    Generate an M-PAM constellation.

    """
    keys = generate_gray_encoding(M)
    # Add your constellation code here.
    min = -(M - 1)
    max = M - 1
    nums = np.arange(min, max+1, 2, dtype=np.float64)
    power = np.dot(nums, nums) / len(nums)
    nums /= np.sqrt(power)
    table = dict(zip(keys, nums))
    return table

def bits_to_pam_symbols(bits, M):
    """
    Convert a bit sequence to a sequence of M-PAM symbols.
    """
    constellation = get_pam_constellation(M)
    bits_per_symbol = np.log2(M)
    chunks = np.array_split(bits, int(len(bits)/bits_per_symbol))
    symbols = []
    for chunk in chunks:
        bits = ''.join(map(str, np.ndarray.tolist(chunk)))
        symbol = constellation[bits]
        symbols.append(symbol)
    return symbols

def pam_symbols_to_bits(symbols, M):
    constellation = get_pam_constellation(M)
    reversed_const = {v: k for k, v in constellation.items()}
    result = []
    for symbol in symbols:
        bits = reversed_const[symbol]
        for bit in bits:
            result.append(int(bit))
    return result

# Here are some basic tests for your functions, feel free to add your own
# for debugging as you see fit.

def main():
    # Plot the constellation for M = 2.
    M = 2
    constellation = get_pam_constellation(M)
    plt.scatter(constellation.values(), np.zeros(len(constellation)))
    plt.show()

    # Test the conversion functions for M = 2.
    test_bits = [0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1]
    symbols = bits_to_pam_symbols(test_bits, M)
    print(symbols)
    recovered_bits = pam_symbols_to_bits(symbols, M)
    print(recovered_bits)

    print(test_bits)
    print(recovered_bits)

    assert(np.allclose(recovered_bits, test_bits))
    print(f"Success for M = {M}.")


    # Plot the constellation for M = 4.
    M = 4
    constellation = get_pam_constellation(M)
    plt.scatter(constellation.values(), np.zeros(len(constellation)))
    plt.show()

    # Test the conversion functions for M = 4.
    test_bits = [0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1]
    symbols = bits_to_pam_symbols(test_bits, M)
    recovered_bits = pam_symbols_to_bits(symbols, M)

    print(test_bits)
    print(recovered_bits)

    assert(np.allclose(recovered_bits, test_bits))
    print(f"Success for M = {M}.")


if __name__ == "__main__":
    main()
