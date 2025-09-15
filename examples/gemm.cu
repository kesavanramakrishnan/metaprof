#include <cstdio>
#include <cstdlib>

__global__ void gemm_kernel(const float* __restrict__ A,
                            const float* __restrict__ B,
                            float* __restrict__ C,
                            int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < N && col < N) {
        float acc = 0.0f;
        for (int k = 0; k < N; ++k) {
            acc += A[row * N + k] * B[k * N + col];
        }
        C[row * N + col] = acc;
    }
}

int main(int argc, char** argv) {
    int N = 512;
    if (argc > 1) {
        N = std::atoi(argv[1]);
    }
    size_t bytes = static_cast<size_t>(N) * N * sizeof(float);

    float *hA = (float*)malloc(bytes);
    float *hB = (float*)malloc(bytes);
    float *hC = (float*)malloc(bytes);
    for (int i = 0; i < N * N; ++i) {
        hA[i] = 1.0f;
        hB[i] = 1.0f;
    }

    float *dA, *dB, *dC;
    cudaMalloc(&dA, bytes);
    cudaMalloc(&dB, bytes);
    cudaMalloc(&dC, bytes);
    cudaMemcpy(dA, hA, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(dB, hB, bytes, cudaMemcpyHostToDevice);

    dim3 block(16, 16);
    dim3 grid((N + block.x - 1) / block.x, (N + block.y - 1) / block.y);
    gemm_kernel<<<grid, block>>>(dA, dB, dC, N);
    cudaDeviceSynchronize();

    cudaMemcpy(hC, dC, bytes, cudaMemcpyDeviceToHost);
    // print a checksum so the compiler doesn't optimize away everything
    double checksum = 0.0;
    for (int i = 0; i < N * N; ++i) checksum += hC[i];
    std::printf("checksum: %.0f\n", checksum);

    cudaFree(dA);
    cudaFree(dB);
    cudaFree(dC);
    free(hA);
    free(hB);
    free(hC);
    return 0;
}


