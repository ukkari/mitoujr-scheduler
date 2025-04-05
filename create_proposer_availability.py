
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

def create_proposer_availability(input_file, output_file, id_row_name="ID", no_transpose=False):
    """
    Convert Google Form CSV format to proposer availability format.
    
    Args:
        input_file: Path to the input CSV file from Google Form
        output_file: Path to save the output proposer availability CSV
        id_row_name: Name of the row/column containing proposer IDs
        no_transpose: If True, assume the input file is not transposed (standard format)
    """
    df = pd.read_csv(input_file)
    
    time_slots = generate_time_slots()
    
    availability_df = pd.DataFrame(index=time_slots)
    
    interview_name = "二次選考（オンライン面接）が可能な日時（下記の時間から30分ほど、こちらから指定させて頂きます）"
    
    if id_row_name in df.columns and df.columns[0] == id_row_name:
        interview_row = None
        
        for idx, row in df.iterrows():
            if isinstance(row.iloc[0], str) and interview_name in row.iloc[0]:
                interview_row = row
                break
        
        if interview_row is None:
            for idx, row in df.iterrows():
                if isinstance(row.iloc[0], str) and "二次選考" in row.iloc[0] and "面接" in row.iloc[0]:
                    interview_row = row
                    break
        
        if interview_row is None:
            for idx, row in df.iterrows():
                if isinstance(row.iloc[0], str) and "可能な日時" in row.iloc[0]:
                    interview_row = row
                    break
        
        if interview_row is None:
            for idx, row in df.iterrows():
                for col_idx in range(1, len(row)):
                    cell_value = row.iloc[col_idx]
                    if isinstance(cell_value, str) and ("午前" in cell_value or "午後" in cell_value or "夜" in cell_value):
                        if any(f"{month}/{day}" in cell_value for month in ["4", "5"] for day in range(1, 32)):
                            interview_row = row
                            print(f"Found availability data in row {idx} with first column: {row.iloc[0]}")
                            break
                if interview_row is not None:
                    break
        
        if interview_row is None:
            raise ValueError(f"Could not find row with interview availability data in the CSV file")
        
        for col_name in df.columns[1:]:  # Skip the first column (ID)
            proposer_id = col_name
            
            if pd.isna(proposer_id):
                continue
                
            available_slots_str = interview_row[proposer_id]
            
            if pd.isna(available_slots_str):
                continue
                
            availability_df[proposer_id] = False
            
            if isinstance(available_slots_str, str):
                for slot in time_slots:
                    if slot in available_slots_str:
                        availability_df.loc[slot, proposer_id] = True
                
                if availability_df[proposer_id].sum() == 0:
                    available_slots = [slot.strip() for slot in available_slots_str.split(',')]
                    for slot in available_slots:
                        if slot in time_slots:
                            availability_df.loc[slot, proposer_id] = True
    
    elif no_transpose:
        if interview_name not in df.columns:
            raise ValueError(f"Could not find column with name '{interview_name}' in the CSV file")
        
        for idx, row in df.iterrows():
            proposer_id = row[id_row_name]
            
            if pd.isna(proposer_id):
                continue
                
            available_slots_str = row[interview_name]
            
            if pd.isna(available_slots_str):
                continue
                
            availability_df[proposer_id] = False
            
            available_slots = [slot.strip() for slot in str(available_slots_str).split(',')]
            
            for slot in available_slots:
                if slot in time_slots:
                    availability_df.loc[slot, proposer_id] = True
    
    else:
        if interview_name not in df.iloc[:, 0].values:
            raise ValueError(f"Could not find row with name '{interview_name}' in the CSV file")
        
        interview_row_index = df.iloc[:, 0].tolist().index(interview_name)
        
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
            
            available_slots = [slot.strip() for slot in str(available_slots_str).split(',')]
            
            for slot in available_slots:
                if slot in time_slots:
                    availability_df.loc[slot, proposer_id] = True
    
    availability_df = availability_df.astype(int)
    
    availability_df.to_csv(output_file)
    
    return availability_df

def main():
    parser = argparse.ArgumentParser(description='Create proposer availability file from Google Form CSV.')
    parser.add_argument('--input-file', required=True, help='Input CSV file from Google Form')
    parser.add_argument('--output-file', default='proposer_availability.csv', help='Output proposer availability CSV file')
    parser.add_argument('--id-row', default='ID', help='Name of the row/column containing proposer IDs')
    parser.add_argument('--no-transpose', action='store_true', help='Set this flag if the input CSV is not transposed (standard format)')
    
    args = parser.parse_args()
    
    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    availability_df = create_proposer_availability(args.input_file, args.output_file, args.id_row, args.no_transpose)
    
    print(f"Proposer availability file created: {args.output_file}")
    print(f"Number of proposers: {len(availability_df.columns)}")
    print(f"Number of time slots: {len(availability_df)}")

if __name__ == "__main__":
    main()
