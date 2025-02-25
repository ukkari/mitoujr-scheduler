#!/bin/bash

# Run the interview scheduler demo

echo "===== Interview Scheduler Demo ====="
echo

# 1. Generate test data
echo "Generating test data..."
python generate_test_data.py --num-proposers 20 --num-mentors 5 --output-dir test_data
echo

# 2. Run the scheduler with test data
echo "Running scheduler with test data..."
python interview_scheduler.py --proposer-file test_data/proposer_availability.csv --mentor-file test_data/mentor_availability.csv --preference-file test_data/mentor_preferences.csv --output-dir test_output
echo

# 3. Run the small example
echo "Running small example..."
python example.py
echo

echo "===== Demo Complete ====="
echo "Check the following directories for results:"
echo "- test_data/: Generated test data"
echo "- test_output/: Scheduling results for test data"
echo "- example_output/: Scheduling results for the small example"