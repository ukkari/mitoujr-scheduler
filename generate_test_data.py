#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import random
import argparse
import os
import re
from datetime import datetime, timedelta

def split_into_hourly_slots(time_slot):
    """
    Split a time slot into hourly slots.
    
    Example: "4/23 夜 (19:00 - 21:00)" -> ["2024/04/23 19:00 PM", "2024/04/23 20:00 PM"]
    """
    match = re.match(r'(\d+/\d+)\s+[^\(]+\((\d+:\d+)\s*-\s*(\d+:\d+)\)', time_slot)
    if not match:
        return []
    
    date_str, start_time, end_time = match.groups()
    
    year = "2024"
    
    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))
    
    month, day = map(int, date_str.split('/'))
    
    start_datetime = datetime(int(year), month, day, start_hour, start_minute)
    end_datetime = datetime(int(year), month, day, end_hour, end_minute)
    
    hourly_slots = []
    current_time = start_datetime
    while current_time < end_datetime:
        am_pm = "AM" if current_time.hour < 12 else "PM"
        hour_12 = current_time.hour if current_time.hour <= 12 else current_time.hour - 12
        if hour_12 == 0:
            hour_12 = 12
        
        slot = f"{year}/{current_time.month:02d}/{current_time.day:02d} {hour_12:02d}:{current_time.minute:02d} {am_pm}"
        hourly_slots.append(slot)
        
        current_time += timedelta(hours=1)
    
    return hourly_slots

def generate_time_slots():
    """Generate the list of time slots as specified in the requirements."""
    original_slots = [
        "4/23 夜 (19:00 - 21:00)",
        "4/24 夜 (19:00 - 21:00)",
        "4/25 夜 (19:00 - 21:00)",
        "4/26 午前 (9:00 - 12:00)",
        "4/26 午後 (13:00 - 17:00)",
        "4/26 夜 (19:00 - 21:00)",
        "4/27 午前 (9:00 - 12:00)",
        "4/27 午後 (13:00 - 17:00)",
        "4/27 夜 (19:00 - 21:00)",
        "4/28 夜 (19:00 - 21:00)",
        "4/29 午前 (9:00 - 12:00)",
        "4/29 午後 (13:00 - 17:00)",
        "4/29 夜 (19:00 - 21:00)",
        "4/30 夜 (19:00 - 21:00)",
        "5/1 夜 (19:00 - 21:00)",
        "5/2 夜 (19:00 - 21:00)",
        "5/3 午前 (9:00 - 12:00)",
        "5/3 午後 (13:00 - 17:00)",
        "5/3 夜 (19:00 - 21:00)",
        "5/4 午前 (9:00 - 12:00)",
        "5/4 午後 (13:00 - 17:00)",
        "5/4 夜 (19:00 - 21:00)",
        "5/5 午前 (9:00 - 12:00)",
        "5/5 午後 (13:00 - 17:00)",
        "5/5 夜 (19:00 - 21:00)",
        "5/6 午前 (9:00 - 12:00)",
        "5/6 午後 (13:00 - 17:00)",
        "5/6 夜 (19:00 - 21:00)"
    ]
    
    hourly_slots = []
    for slot in original_slots:
        hourly_slots.extend(split_into_hourly_slots(slot))
    
    return hourly_slots

def generate_availability_data(num_entities, time_slots, availability_rate=0.3):
    """
    Generate random availability data.
    
    Args:
        num_entities: Number of entities (proposers or mentors)
        time_slots: List of time slots
        availability_rate: Probability of being available for a given time slot
    
    Returns:
        DataFrame with availability data
    """
    # Create entity IDs
    if num_entities <= 26:
        # Use letters for small numbers
        entity_ids = [chr(65 + i) for i in range(num_entities)]
    else:
        # Use numbers for larger sets
        entity_ids = [f"ID{i+1:03d}" for i in range(num_entities)]
    
    # Generate random availability (True/False)
    data = {}
    for entity_id in entity_ids:
        # Each entity has random availability
        data[entity_id] = np.random.random(len(time_slots)) < availability_rate
    
    # Create DataFrame
    df = pd.DataFrame(data, index=time_slots)
    
    return df

def generate_preference_data(mentor_ids, project_ids, preference_rate=0.2):
    """
    Generate random mentor preferences for projects.
    
    Args:
        mentor_ids: List of mentor IDs
        project_ids: List of project IDs
        preference_rate: Probability of a mentor being interested in a project
    
    Returns:
        DataFrame with preference data
    """
    # Initialize empty DataFrame
    df = pd.DataFrame(index=mentor_ids)
    
    # For each mentor, generate random preferences
    for i, mentor in enumerate(mentor_ids):
        preferences = []
        
        # Determine how many projects this mentor is interested in
        num_preferences = max(1, int(len(project_ids) * preference_rate))
        
        # Randomly select projects
        selected_projects = random.sample(project_ids, num_preferences)
        
        # Add to DataFrame
        for j, project in enumerate(selected_projects):
            df.loc[mentor, f"Project{j+1}"] = project
    
    return df

def main():
    parser = argparse.ArgumentParser(description='Generate test data for interview scheduler.')
    parser.add_argument('--num-proposers', type=int, default=100, help='Number of project proposers')
    parser.add_argument('--num-mentors', type=int, default=20, help='Number of mentors')
    parser.add_argument('--output-dir', default='test_data', help='Directory to save test data files')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate time slots
    time_slots = generate_time_slots()
    
    # Generate project proposer IDs
    project_ids = [f"P{i+1:03d}" for i in range(args.num_proposers)]
    
    # Generate mentor IDs
    mentor_ids = ["田中太郎", "佐藤次郎", "山田三郎", "鈴木四郎", "高橋五郎", 
                 "伊藤六郎", "渡辺七郎", "小林八郎", "加藤九郎", "吉田十郎",
                 "松本一郎", "井上二郎", "木村三郎", "林四郎", "清水五郎",
                 "山本六郎", "中村七郎", "石田八郎", "前田九郎", "藤田十郎"][:args.num_mentors]
    
    # Generate availability data
    proposer_availability = generate_availability_data(args.num_proposers, time_slots, 0.3)
    proposer_availability.columns = project_ids
    
    mentor_availability = generate_availability_data(args.num_mentors, time_slots, 0.4)
    mentor_availability.columns = mentor_ids
    
    # Generate preference data
    mentor_preferences = generate_preference_data(mentor_ids, project_ids, 0.15)
    
    # Save to CSV files
    proposer_availability.to_csv(os.path.join(args.output_dir, 'proposer_availability.csv'))
    mentor_availability.to_csv(os.path.join(args.output_dir, 'mentor_availability.csv'))
    mentor_preferences.to_csv(os.path.join(args.output_dir, 'mentor_preferences.csv'))
    
    print(f"Test data generated and saved to {args.output_dir}/")
    print(f"- {args.num_proposers} proposers")
    print(f"- {args.num_mentors} mentors")
    print(f"- {len(time_slots)} time slots")

if __name__ == "__main__":
    main()
