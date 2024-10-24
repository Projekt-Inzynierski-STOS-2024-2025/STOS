#include <iostream>
#include <vector>
#include <chrono>

std::vector<std::vector<int>> multiplyMatrices(const std::vector<std::vector<int>>& A, const std::vector<std::vector<int>>& B, int N) {
    std::vector<std::vector<int>> result(N, std::vector<int>(N, 0));
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            for (int k = 0; k < N; ++k) {
                result[i][j] += A[i][k] * B[k][j];
            }
        }
    }
    return result;
}

int main() {
    const int N = 1000;

    std::vector<std::vector<int>> A(N, std::vector<int>(N, 1));
    std::vector<std::vector<int>> B(N, std::vector<int>(N, 2));

    auto start = std::chrono::high_resolution_clock::now();

    std::vector<std::vector<int>> result = multiplyMatrices(A, B, N);

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    std::cout <<  elapsed.count() << std::endl;

    return 0;
}