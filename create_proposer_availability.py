
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

def create_proposer_availability(input_file, output_file, id_row_name="ID"):
    """
    Convert transposed Google Form CSV format to proposer availability format.
    
    Args:
        input_file: Path to the input transposed CSV file from Google Form
        output_file: Path to save the output proposer availability CSV
        id_row_name: Name of the row containing proposer IDs
    """
    df = pd.read_csv(input_file)
    
    time_slots = generate_time_slots()
    
    availability_df = pd.DataFrame(index=time_slots)
    
    interview_row_name = "二次選考（オンライン面接）が可能な日時（下記の時間から30分ほど、こちらから指定させて頂きます）"
    if interview_row_name not in df.iloc[:, 0].values:
        raise ValueError(f"Could not find row with name '{interview_row_name}' in the CSV file")
    
    interview_row_index = df.iloc[:, 0].tolist().index(interview_row_name)
    
    if id_row_name not in df.iloc[:, 0].values:
        raise ValueError(f"Could not find row with name '{id_row_name}' in the CSV file")
    
    id_row_index = df.iloc[:, 0].tolist().index(id_row_name)
    
    for col_idx in range(1, len(df.columns)):
        proposer_id = df.iloc[id_row_index, col_idx]
        
        if pd.isna(proposer_id):
            continue
            
        available_slots_str = df.iloc[interview_row_index, col_idx]
        
        if pd.isna(available_slots_str):
            continue
            
        availability_df[proposer_id] = False
        
        available_slots = [slot.strip() for slot in available_slots_str.split(',')]
        
        for slot in available_slots:
            if slot in time_slots:
                availability_df.loc[slot, proposer_id] = True
    
    availability_df = availability_df.astype(int)
    
    availability_df.to_csv(output_file)
    
    return availability_df

def main():
    parser = argparse.ArgumentParser(description='Create proposer availability file from transposed Google Form CSV.')
    parser.add_argument('--input-file', required=True, help='Input transposed CSV file from Google Form')
    parser.add_argument('--output-file', default='proposer_availability.csv', help='Output proposer availability CSV file')
    parser.add_argument('--id-row', default='ID', help='Name of the row containing proposer IDs')
    
    args = parser.parse_args()
    
    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    availability_df = create_proposer_availability(args.input_file, args.output_file, args.id_row)
    
    print(f"Proposer availability file created: {args.output_file}")
    print(f"Number of proposers: {len(availability_df.columns)}")
    print(f"Number of time slots: {len(availability_df)}")

if __name__ == "__main__":
    main()
