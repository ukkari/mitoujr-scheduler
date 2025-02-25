#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example script demonstrating how to use the interview scheduler with a small dataset.
This creates a minimal example with 5 proposers and 3 mentors.
"""

import pandas as pd
import numpy as np
import os
from interview_scheduler import InterviewScheduler

def create_example_data():
    """Create a small example dataset for demonstration."""
    # Define time slots
    time_slots = [
        "4/23 夜 (19:00 - 21:00)",
        "4/24 夜 (19:00 - 21:00)",
        "4/25 夜 (19:00 - 21:00)",
        "4/26 午前 (9:00 - 12:00)",
        "4/26 午後 (13:00 - 17:00)"
    ]
    
    # Define project IDs and mentor names
    project_ids = ["P001", "P002", "P003", "P004", "P005"]
    mentor_names = ["MentorA", "MentorB", "MentorC"]
    
    # Create example availability for proposers
    proposer_data = {
        "P001": [True, False, True, False, True],
        "P002": [False, True, True, True, False],
        "P003": [True, True, False, False, True],
        "P004": [False, False, True, True, True],
        "P005": [True, False, False, True, True]
    }
    proposer_availability = pd.DataFrame(proposer_data, index=time_slots)
    
    # Create example availability for mentors
    mentor_data = {
        "MentorA": [True, True, False, True, False],
        "MentorB": [False, True, True, False, True],
        "MentorC": [True, False, True, True, True]
    }
    mentor_availability = pd.DataFrame(mentor_data, index=time_slots)
    
    # Create example preferences
    preferences = {
        "MentorA": ["P001", "P003", "P005"],
        "MentorB": ["P002", "P004"],
        "MentorC": ["P001", "P002", "P003", "P004"]
    }
    
    # Convert preferences to DataFrame format
    preference_data = {}
    for mentor, prefs in preferences.items():
        for i, proj in enumerate(prefs):
            if f"Project{i+1}" not in preference_data:
                preference_data[f"Project{i+1}"] = {}
            preference_data[f"Project{i+1}"][mentor] = proj
    
    preference_df = pd.DataFrame(preference_data).T.transpose()
    
    # Create output directory
    os.makedirs("example_data", exist_ok=True)
    
    # Save to CSV
    proposer_availability.to_csv("example_data/proposer_availability.csv")
    mentor_availability.to_csv("example_data/mentor_availability.csv")
    preference_df.to_csv("example_data/mentor_preferences.csv")
    
    return "example_data/proposer_availability.csv", "example_data/mentor_availability.csv", "example_data/mentor_preferences.csv"

def main():
    # Create example data
    proposer_file, mentor_file, preference_file = create_example_data()
    
    print("Example data created:")
    print(f"- Proposer availability: {proposer_file}")
    print(f"- Mentor availability: {mentor_file}")
    print(f"- Mentor preferences: {preference_file}")
    
    # Initialize scheduler
    scheduler = InterviewScheduler(proposer_file, mentor_file, preference_file)
    
    # Schedule interviews
    scheduler.schedule_interviews()
    
    # Save results
    output_dir = "example_output"
    scheduler.save_schedule(output_dir)
    
    print(f"\nScheduling complete. Results saved to {output_dir}/")
    
    # Display the schedule
    schedule_df, _ = scheduler.output_schedule()
    print("\nInterview Schedule:")
    print(schedule_df)
    
    # Check for unscheduled interviews
    unscheduled = scheduler._get_unscheduled_interviews()
    if unscheduled:
        print("\nUnscheduled Interviews:")
        for item in unscheduled:
            print(f"- {item['Mentor']} cannot interview {item['Project ID']}: {item['Reason']}")
    else:
        print("\nAll interviews were successfully scheduled!")

if __name__ == "__main__":
    main()