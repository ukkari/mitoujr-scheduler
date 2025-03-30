
import pandas as pd
import argparse
import os
import re
from datetime import datetime, timedelta

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
    
    from generate_test_data import split_into_hourly_slots
    
    hourly_slots = []
    for slot in original_slots:
        hourly_slots.extend(split_into_hourly_slots(slot))
    
    return hourly_slots

def create_mentor_availability(input_file, output_file):
    """
    Convert Google Form CSV format to mentor availability format.
    
    Args:
        input_file: Path to the input CSV file from Google Form
        output_file: Path to save the output mentor availability CSV
    """
    df = pd.read_csv(input_file)
    
    time_slots = generate_time_slots()
    
    availability_df = pd.DataFrame(index=time_slots)
    
    for _, row in df.iterrows():
        if pd.isna(row['名前']):
            continue
            
        mentor_id = row['名前']
        
        available_slots_str = row['インタビュー希望時間']
        available_slots = [slot.strip() for slot in available_slots_str.split(',')]
        
        availability_df[mentor_id] = False
        
        for slot in available_slots:
            if slot in time_slots:
                availability_df.loc[slot, mentor_id] = True
    
    availability_df = availability_df.astype(int)
    
    availability_df.to_csv(output_file)
    
    return availability_df

def main():
    parser = argparse.ArgumentParser(description='Create mentor availability file from Google Form CSV.')
    parser.add_argument('--input-file', required=True, help='Input CSV file from Google Form')
    parser.add_argument('--output-file', default='mentor_availability.csv', help='Output mentor availability CSV file')
    
    args = parser.parse_args()
    
    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    availability_df = create_mentor_availability(args.input_file, args.output_file)
    
    print(f"Mentor availability file created: {args.output_file}")
    print(f"Number of mentors: {len(availability_df.columns)}")
    print(f"Number of time slots: {len(availability_df)}")

if __name__ == "__main__":
    main()
