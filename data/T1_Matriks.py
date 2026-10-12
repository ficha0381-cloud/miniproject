import numpy as np

# Array 3 dimensi pertama
A = np.array([
[[1, 2],
[3, 4]],

[[5, 6],
[7, 8]]
])

# Array 3 dimensi kedua
B = np.array([
[[2, 0],
[1, 2]],

[[1, 3],
[2, 1]]
])
# Perkalian matrix
C = np.matmul(A, B)

print("Array A:")
print(A)

print("\nArray B:")
print(B)

print("\nHasil perkalian A x B:")
print(C)