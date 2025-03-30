
import pandas as pd
import argparse
import os

def generate_time_slots():
    """Generate the list of time slots as specified in the requirements."""
    time_slots = [
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
    return time_slots

def create_proposer_availability(input_file, output_file):
    """
    Convert Google Form CSV format to proposer availability format.
    
    Args:
        input_file: Path to the input CSV file from Google Form
        output_file: Path to save the output proposer availability CSV
    """
    df = pd.read_csv(input_file)
    
    time_slots = generate_time_slots()
    
    availability_df = pd.DataFrame(index=time_slots)
    
    for _, row in df.iterrows():
        if pd.isna(row['ID']):
            continue
            
        proposer_id = row['ID']
        
        available_slots_column = "二次選考（オンライン面接）が可能な日時（下記の時間から30分ほど、こちらから指定させて頂きます）"
        if pd.isna(row[available_slots_column]):
            continue
            
        available_slots_str = row[available_slots_column]
        available_slots = [slot.strip() for slot in available_slots_str.split(',')]
        
        availability_df[proposer_id] = False
        
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
    
    args = parser.parse_args()
    
    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    availability_df = create_proposer_availability(args.input_file, args.output_file)
    
    print(f"Proposer availability file created: {args.output_file}")
    print(f"Number of proposers: {len(availability_df.columns)}")
    print(f"Number of time slots: {len(availability_df)}")

if __name__ == "__main__":
    main()
