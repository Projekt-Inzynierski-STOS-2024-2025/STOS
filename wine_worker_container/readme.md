# Docker Container with Wine and C++ Build Tools

This Docker container is set up with Wine and the necessary tools to build and run C++ applications in a Windows-like environment on Linux.

## Usage

1. **Build the Docker image:**

   ```bash
   ./buildContainer.sh
   ```

2. **Run the Docker container and mount a shared volume with your project:**

   ```bash
   ./runContainer.sh "path_to_shared_volume"
   ```

   - The `path_to_shared_volume` should point to the directory containing source code and input files.

## Shared Volume Structure

The shared volume must contain the following directories:

- **`source/`**: This directory holds C++ source files (`.cpp`).
- **`input/`**: This directory contains enumerated `.in` files, which are text files with standard input data for the program (`1.in`, `2.in`, ..., `n.in`).

## Output

For each `.in` file in the `input/` directory, the container runs the program and redirects the output to the **`output/`** directory in the shared volume. Each `.in` file will have a corresponding `.out` file in the output directory (e.g., `1.in` → `1.out`).

---

### Example

Directory structure inside the shared volume:

```
/shared_volume/
├── source/
│   └── main.cpp
├── input/
│   ├── 1.in
│   ├── 2.in
│   └── n.in
└── output/
    ├── 1.out
    ├── 2.out
    └── n.out
```

- **Source files** are placed in the `source/` directory.
- **Input files** for each test case are placed in the `input/` directory.
- **Output files** corresponding to each input are generated in the `output/` directory.

### Notes

- Ensure that the `source/`, `input/`, and `output/` directories are correctly structured in your shared volume.
- The `runContainer.sh` script will mount the shared volume and handle the compilation and execution of the C++ program inside the Docker container.
