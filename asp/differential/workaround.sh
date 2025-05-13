#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <path/to/envs/pkl/filename.pkl> [flags...]"
    exit 1
fi

# Get the input file and flags
input_file="$1"
shift # Remove the first argument, leaving only flags
flags="$@"

# Extract the filename from the input file path
filename=$(basename "$input_file" .pkl)

# Construct the command to execute
command="clingo-dl envs/lp/$filename.lp asp/differential/0_input.lp asp/differential/1_path.lp -V0 --out-atom=%s. | head -n 1 | clingo - asp/differential/2_output.lp -V0 --out-atom=%s. | head -n 1 > asp/differential/test.lp"

# Measure the time taken to execute the command
start_time=$(date +%s)
eval "$command"
end_time=$(date +%s)

# Calculate the elapsed time
elapsed_time=$((end_time - start_time))

# Output the time taken
echo "Time taken for clingo-dl command: $elapsed_time seconds"

# Run the Python script with the input file and flags
python solve.py "$input_file" $flags
