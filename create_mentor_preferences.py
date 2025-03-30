
import pandas as pd
import argparse
import os

def create_mentor_preferences(input_file, output_file, id_row_name="ID"):
    """
    Convert transposed Google Form CSV format to mentor preferences format.
    
    Args:
        input_file: Path to the input transposed CSV file
        output_file: Path to save the output mentor preferences CSV
        id_row_name: Name of the row containing project IDs
    """
    df = pd.read_csv(input_file)
    
    if id_row_name not in df.iloc[:, 0].values:
        raise ValueError(f"Could not find row with name '{id_row_name}' in the CSV file")
    
    id_row_index = df.iloc[:, 0].tolist().index(id_row_name)
    project_ids = df.iloc[id_row_index, 1:].tolist()
    
    mentor_preferences = {}
    
    for i in range(id_row_index + 1, len(df)):
        mentor_id = df.iloc[i, 0].strip()
        
        if not mentor_id:
            continue
            
        preferences = []
        
        for j in range(1, len(df.columns)):
            cell_value = df.iloc[i, j]
            
            if pd.notna(cell_value) and str(cell_value).strip():
                project_id = project_ids[j-1]
                if pd.notna(project_id) and str(project_id).strip():
                    preferences.append(project_id)
        
        if preferences:
            mentor_preferences[mentor_id] = preferences
    
    output_df = pd.DataFrame(index=mentor_preferences.keys())
    
    for mentor, projects in mentor_preferences.items():
        for i, project in enumerate(projects):
            output_df.loc[mentor, f'Project{i+1}'] = project
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    output_df.to_csv(output_file)
    
    return output_df

def main():
    parser = argparse.ArgumentParser(description='Create mentor preferences file from transposed CSV.')
    parser.add_argument('--input-file', required=True, help='Input transposed CSV file')
    parser.add_argument('--output-file', default='mentor_preferences.csv', help='Output mentor preferences CSV file')
    parser.add_argument('--id-row', default='ID', help='Name of the row containing project IDs')
    
    args = parser.parse_args()
    
    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    preferences_df = create_mentor_preferences(args.input_file, args.output_file, args.id_row)
    
    print(f"Mentor preferences file created: {args.output_file}")
    print(f"Number of mentors: {len(preferences_df)}")
    print(f"Number of preferred projects: {sum(len(row.dropna()) for _, row in preferences_df.iterrows())}")

if __name__ == "__main__":
    main()
