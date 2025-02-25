# Docker Container with Wine and C++ Build Tools

This Docker container is set up with Wine and the necessary tools to run C++ applications in a Windows-like environment on Linux.

## Usage

1. **Build the Docker image:**

   ```bash
   ./buildContainer.sh
   ```

2. **Run the Docker container with shared paths:**

   ```bash
   ./runContainer.sh <path_to_executable_direcotry>, <path_to_input_files_directory>, <path_to_output_directory> 
   ```

## Output

For each `.in` file in the `input/` directory, the container runs the program and redirects the output to the defined output volume.
Each `.in` file will have a corresponding `.out` file in the output directory (e.g., `1.in` → `1.out`).

---

### Notes

- The `runContainer.sh` script will mount the shared volume and handle the execution of the C++ program inside the Docker container.
