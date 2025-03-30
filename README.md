# Interview Scheduler

This project provides a solution for scheduling interviews between project proposers and mentors based on their availability and preferences.

## Background

For the Mitou Junior program, mentors need to interview project proposers online for selection. This tool automates the scheduling process by matching proposers and mentors based on their availability and preferences, while optimizing for:

1. Minimizing mentors' working time by scheduling consecutive interviews
2. Ensuring all mentors who want to interview a specific project can do so (if possible)
3. Prioritizing earlier dates in the schedule

## Files

- `interview_scheduler.py`: Main script for scheduling interviews
- `generate_test_data.py`: Helper script to generate test data for demonstration
- `create_mentor_availability.py`: Script to convert Google Form CSV data to mentor availability format

## Requirements

- Python 3.6+
- pandas
- numpy

Install dependencies:

```bash
pip install pandas numpy
```

## Usage

### 1. Create Mentor Availability File from Google Form

If you have mentor availability data from a Google Form, you can convert it to the required format:

```bash
python create_mentor_availability.py --input-file path/to/google_form_export.csv --output-file test_data/mentor_availability.csv
```

The input CSV file should contain the following columns:
- タイムスタンプ (Timestamp)
- メールアドレス (Email address)
- 名前 (Name)
- インタビュー希望時間 (Interview preferred times) - comma-separated list of time slots
- Mentor ID (e.g., M01)

### 2. Generate Test Data (Optional)

If you don't have real data yet, you can generate test data:

```bash
python generate_test_data.py --num-proposers 100 --num-mentors 20 --output-dir test_data
```

This will create:
- `test_data/proposer_availability.csv`: Availability of project proposers
- `test_data/mentor_availability.csv`: Availability of mentors
- `test_data/mentor_preferences.csv`: Mentors' project preferences

### 2. Run the Scheduler

```bash
python interview_scheduler.py --proposer-file test_data/proposer_availability.csv --mentor-file test_data/mentor_availability.csv --preference-file test_data/mentor_preferences.csv --output-dir schedule_output
```

### 3. Review the Results

The scheduler will generate several files in the output directory:
- `complete_schedule.csv`: The complete interview schedule
- `{mentor_name}_schedule.csv`: Individual schedules for each mentor
- `unscheduled_interviews.csv`: List of interviews that couldn't be scheduled (if any)

## Input File Format

### Proposer and Mentor Availability Files

CSV files with time slots as rows and proposer/mentor IDs as columns. A value of 1 (or True) indicates availability.

Example:
```
Time Slot,P001,P002,P003,...
4/23 夜 (19:00 - 21:00),1,0,1,...
4/24 夜 (19:00 - 21:00),0,1,1,...
...
```

### Mentor Preferences File

CSV file with mentors as rows and their project preferences as columns.

Example:
```
Mentor,Project1,Project2,Project3,...
M01,P005,P023,P067,...
M02,P012,P045,,...
...
```

## Algorithm Details

The scheduling algorithm works in three passes:

1. First, it tries to schedule projects that multiple mentors want to interview, finding time slots where all interested mentors are available.

2. Next, it schedules remaining interviews, prioritizing consecutive time slots for each mentor to minimize their working time.

3. Finally, it handles any remaining unscheduled interviews by finding the earliest available slots.

The algorithm prioritizes earlier dates in the schedule and tries to ensure that all mentors can interview their preferred projects.

## Limitations

- The current implementation assumes that all interviews have the same duration.
- If there are no common available slots for a mentor and proposer, the interview will be listed as unscheduled.
