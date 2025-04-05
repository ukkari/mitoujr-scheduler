import pandas as pd
import re
from datetime import datetime, timedelta

def process_availability_string(available_slots_str, proposer_id, availability_df, time_slots, original_slots, slot_mapping):
    """
    Process an availability string and update the availability DataFrame.
    
    Args:
        available_slots_str: String containing availability information
        proposer_id: ID of the proposer
        availability_df: DataFrame to update
        time_slots: List of hourly time slots
        original_slots: List of original time slots
        slot_mapping: Mapping from original slots to hourly slots
    """
    print(f"Processing availability for {proposer_id}: {available_slots_str[:100]}...")
    
    matched = False
    
    for orig_slot in original_slots:
        if orig_slot in available_slots_str:
            matched = True
            print(f"  Direct match found: {orig_slot}")
            for hourly_slot in slot_mapping[orig_slot]:
                availability_df.loc[hourly_slot, proposer_id] = True
    
    if not matched:
        available_slots = [slot.strip() for slot in available_slots_str.split(',')]
        print(f"  Trying comma-separated parsing, found {len(available_slots)} slots")
        for slot in available_slots:
            for orig_slot in original_slots:
                if orig_slot == slot:
                    print(f"  Exact match found: {orig_slot}")
                    for hourly_slot in slot_mapping[orig_slot]:
                        availability_df.loc[hourly_slot, proposer_id] = True
                    matched = True
                    break
    
    if not matched:
        print("  Trying partial matching...")
        for orig_slot in original_slots:
            date_part = orig_slot.split(' ')[0]  # e.g., "4/23"
            time_part = orig_slot.split(' ')[1]  # e.g., "夜"
            
            if date_part in available_slots_str and time_part in available_slots_str:
                print(f"  Partial match found: {orig_slot} (date: {date_part}, time: {time_part})")
                for hourly_slot in slot_mapping[orig_slot]:
                    availability_df.loc[hourly_slot, proposer_id] = True
                matched = True
    
    if not matched:
        print("  Trying regex pattern matching...")
        date_pattern = r'(\d+/\d+)'
        dates = re.findall(date_pattern, available_slots_str)
        
        time_indicators = ["午前", "午後", "夜"]
        
        if dates:
            print(f"  Found dates: {dates}")
            for date in dates:
                for time_indicator in time_indicators:
                    if time_indicator in available_slots_str:
                        potential_slot = f"{date} {time_indicator}"
                        print(f"  Constructed potential slot: {potential_slot}")
                        
                        for orig_slot in original_slots:
                            if potential_slot in orig_slot:
                                print(f"  Matched with original slot: {orig_slot}")
                                for hourly_slot in slot_mapping[orig_slot]:
                                    availability_df.loc[hourly_slot, proposer_id] = True
                                matched = True
    
    if not matched:
        print(f"  WARNING: No availability matches found for {proposer_id}")
    else:
        print(f"  Successfully marked {availability_df[proposer_id].sum()} time slots as available for {proposer_id}")
