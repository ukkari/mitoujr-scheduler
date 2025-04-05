
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
    
    is_transposed = False
    if id_row_name in df.iloc[:, 0].values:
        is_transposed = True
    elif id_row_name in df.columns:
        is_transposed = False
    else:
        first_col_values = df.iloc[:, 0].tolist()
        if any(isinstance(val, str) and ("二次選考" in val or "面接" in val or "可能な日時" in val) for val in first_col_values):
            is_transposed = True
        else:
            is_transposed = not no_transpose
    
    if is_transposed:
        print("Processing file as transposed (rows are attributes, columns are proposers)")
        
        interview_row_index = None
        
        if interview_name in df.iloc[:, 0].values:
            interview_row_index = df.iloc[:, 0].tolist().index(interview_name)
        else:
            for idx, val in enumerate(df.iloc[:, 0]):
                if isinstance(val, str):
                    if "二次選考" in val and "面接" in val:
                        interview_row_index = idx
                        break
                    elif "可能な日時" in val:
                        interview_row_index = idx
                        break
        
        if interview_row_index is None:
            for idx, row in df.iterrows():
                for col_idx in range(1, len(row)):
                    cell_value = row.iloc[col_idx]
                    if isinstance(cell_value, str) and ("午前" in cell_value or "午後" in cell_value or "夜" in cell_value):
                        if any(f"{month}/{day}" in cell_value for month in ["4", "5"] for day in range(1, 32)):
                            interview_row_index = idx
                            print(f"Found availability data in row {idx} with first column: {row.iloc[0]}")
                            break
                if interview_row_index is not None:
                    break
        
        if interview_row_index is None:
            raise ValueError("Could not find row with interview availability data in the CSV file")
        
        id_row_index = None
        if id_row_name in df.iloc[:, 0].values:
            id_row_index = df.iloc[:, 0].tolist().index(id_row_name)
        else:
            for idx, row in df.iterrows():
                if idx != interview_row_index:  # Skip the interview row
                    values = [v for v in row.iloc[1:] if not pd.isna(v)]
                    if len(values) == len(set(values)) and len(values) > 0:
                        id_row_index = idx
                        print(f"Using row {idx} with first column '{row.iloc[0]}' as ID row")
                        break
        
        if id_row_index is None:
            print("Could not find ID row, using column indices as IDs")
            for col_idx in range(1, len(df.columns)):
                proposer_id = f"P{col_idx:03d}"
                
                available_slots_str = df.iloc[interview_row_index, col_idx]
                
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
        else:
            for col_idx in range(1, len(df.columns)):
                proposer_id = df.iloc[id_row_index, col_idx]
                
                if pd.isna(proposer_id):
                    continue
                    
                available_slots_str = df.iloc[interview_row_index, col_idx]
                
                if pd.isna(available_slots_str):
                    continue
                    
                availability_df[str(proposer_id)] = False
                
                if isinstance(available_slots_str, str):
                    for slot in time_slots:
                        if slot in available_slots_str:
                            availability_df.loc[slot, str(proposer_id)] = True
                    
                    if availability_df[str(proposer_id)].sum() == 0:
                        available_slots = [slot.strip() for slot in available_slots_str.split(',')]
                        for slot in available_slots:
                            if slot in time_slots:
                                availability_df.loc[slot, str(proposer_id)] = True
    
    else:
        print("Processing file as non-transposed (rows are proposers, columns are attributes)")
        
        interview_col = None
        
        if interview_name in df.columns:
            interview_col = interview_name
        else:
            for col in df.columns:
                if isinstance(col, str):
                    if "二次選考" in col and "面接" in col:
                        interview_col = col
                        break
                    elif "可能な日時" in col:
                        interview_col = col
                        break
        
        if interview_col is None:
            for col in df.columns:
                sample_values = df[col].dropna().head(5).tolist()
                for val in sample_values:
                    if isinstance(val, str) and ("午前" in val or "午後" in val or "夜" in val):
                        if any(f"{month}/{day}" in val for month in ["4", "5"] for day in range(1, 32)):
                            interview_col = col
                            print(f"Found availability data in column: {col}")
                            break
                if interview_col is not None:
                    break
        
        if interview_col is None:
            for col in df.columns:
                for idx, val in enumerate(df[col]):
                    if isinstance(val, str) and ("午前" in val or "午後" in val or "夜" in val):
                        if any(f"{month}/{day}" in val for month in ["4", "5"] for day in range(1, 32)):
                            interview_col = col
                            print(f"Found availability data in column {col} at row {idx}")
                            break
                if interview_col is not None:
                    break
        
        if interview_col is None:
            raise ValueError("Could not find column with interview availability data in the CSV file")
        
        print(f"Using column '{interview_col}' for interview availability data")
        
        if id_row_name not in df.columns:
            for col in df.columns:
                if col != interview_col:
                    values = df[col].dropna().tolist()
                    if len(values) == len(set(values)) and len(values) > 0:
                        id_row_name = col
                        print(f"Using column '{col}' as ID column")
                        break
        
        if id_row_name not in df.columns:
            print("Could not find ID column, using row indices as IDs")
            for idx, row in df.iterrows():
                proposer_id = f"R{idx+1:03d}"
                
                available_slots_str = row[interview_col]
                
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
        else:
            for idx, row in df.iterrows():
                proposer_id = row[id_row_name]
                
                if pd.isna(proposer_id):
                    continue
                    
                available_slots_str = row[interview_col]
                
                if pd.isna(available_slots_str):
                    continue
                    
                availability_df[str(proposer_id)] = False
                
                if isinstance(available_slots_str, str):
                    for slot in time_slots:
                        if slot in available_slots_str:
                            availability_df.loc[slot, str(proposer_id)] = True
                    
                    if availability_df[str(proposer_id)].sum() == 0:
                        available_slots = [slot.strip() for slot in available_slots_str.split(',')]
                        for slot in available_slots:
                            if slot in time_slots:
                                availability_df.loc[slot, str(proposer_id)] = True
    
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
