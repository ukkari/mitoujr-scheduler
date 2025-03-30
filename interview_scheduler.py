#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from collections import defaultdict
import argparse
import os
import re
from datetime import datetime, timedelta

class InterviewScheduler:
    def __init__(self, proposer_file, mentor_file, preference_file):
        """
        Initialize the scheduler with the input CSV files.
        
        Args:
            proposer_file: CSV file with proposers' availability
            mentor_file: CSV file with mentors' availability
            preference_file: CSV file with mentors' project preferences
        """
        self.proposer_file = proposer_file
        self.mentor_file = mentor_file
        self.preference_file = preference_file
        
        # Load data
        self.proposer_availability = self._load_availability(proposer_file)
        self.mentor_availability = self._load_availability(mentor_file)
        self.mentor_preferences = self._load_preferences(preference_file)
        
        # Extract unique projects and mentors
        self.projects = self.proposer_availability.columns.tolist()
        self.mentors = self.mentor_availability.columns.tolist()
        self.time_slots = self.proposer_availability.index.tolist()
        
        # Store the final schedule
        self.schedule = {}
        
    def _load_availability(self, file_path):
        """Load and parse availability CSV file."""
        df = pd.read_csv(file_path, index_col=0)
        # Convert to boolean (assuming 1/0 or True/False in CSV)
        return df.astype(bool)
    
    def _load_preferences(self, file_path):
        """Load and parse mentor preferences CSV file."""
        df = pd.read_csv(file_path, index_col=0)
        
        # Convert to dictionary: {mentor: [project1, project2, ...]}
        preferences = {}
        for mentor in df.index:
            # Get projects that this mentor wants to interview (non-NaN values)
            projects = df.loc[mentor].dropna().tolist()
            preferences[mentor] = projects
            
        return preferences
    
    def _get_common_availability(self, project, mentors):
        """Find time slots where both the project proposer and all specified mentors are available."""
        # Get project proposer's availability
        proposer_avail = self.proposer_availability[project]
        
        # Start with all time slots where the proposer is available
        common_slots = proposer_avail[proposer_avail].index.tolist()
        
        # Filter by each mentor's availability
        for mentor in mentors:
            mentor_avail = self.mentor_availability[mentor]
            # Keep only slots where both are available
            common_slots = [slot for slot in common_slots if mentor_avail.get(slot, False)]
            
            if not common_slots:
                # No common slots found
                break
                
        return common_slots
    
    def _get_consecutive_slots(self, available_slots):
        """Group available slots into consecutive blocks."""
        if not available_slots:
            return []
            
        # Sort slots by date and time
        sorted_slots = sorted(available_slots)
        
        # Group consecutive slots
        consecutive_groups = []
        current_group = [sorted_slots[0]]
        
        for i in range(1, len(sorted_slots)):
            current_slot = current_group[-1]
            next_slot = sorted_slots[i]
            
            try:
                current_datetime = datetime.strptime(current_slot, "%Y/%m/%d %I:%M %p")
                next_datetime = datetime.strptime(next_slot, "%Y/%m/%d %I:%M %p")
                
                if next_datetime - current_datetime == timedelta(hours=1):
                    # Consecutive slot
                    current_group.append(next_slot)
                else:
                    # Start a new group
                    consecutive_groups.append(current_group)
                    current_group = [next_slot]
            except ValueError:
                current_slot_idx = self.time_slots.index(current_group[-1])
                next_slot_idx = self.time_slots.index(sorted_slots[i])
                
                if next_slot_idx == current_slot_idx + 1:
                    # Consecutive slot
                    current_group.append(sorted_slots[i])
                else:
                    # Start a new group
                    consecutive_groups.append(current_group)
                    current_group = [sorted_slots[i]]
                
        consecutive_groups.append(current_group)
        return consecutive_groups
    
    def schedule_interviews(self):
        """
        Schedule interviews based on availability and preferences.
        
        The algorithm prioritizes:
        1. Scheduling interviews where multiple mentors want to interview the same project
        2. Scheduling consecutive interviews for mentors
        3. Using earlier time slots
        """
        # Create a dictionary to track which projects each mentor needs to interview
        mentor_to_projects = defaultdict(list)
        for mentor, projects in self.mentor_preferences.items():
            for project in projects:
                mentor_to_projects[mentor].append(project)
        
        # Create a dictionary to track which mentors want to interview each project
        project_to_mentors = defaultdict(list)
        for mentor, projects in self.mentor_preferences.items():
            for project in projects:
                project_to_mentors[project].append(mentor)
        
        # Sort projects by number of interested mentors (descending)
        sorted_projects = sorted(project_to_mentors.keys(), 
                                key=lambda p: len(project_to_mentors[p]), 
                                reverse=True)
        
        # First pass: Try to schedule projects with multiple mentors
        for project in sorted_projects:
            mentors = project_to_mentors[project]
            
            if len(mentors) > 1:
                # Try to find slots where all mentors are available
                common_slots = self._get_common_availability(project, mentors)
                
                if common_slots:
                    # Use the earliest available slot
                    selected_slot = common_slots[0]
                    
                    # Schedule this interview
                    self.schedule[(project, selected_slot)] = mentors
                    
                    # Mark this project as scheduled for these mentors
                    for mentor in mentors:
                        if project in mentor_to_projects[mentor]:
                            mentor_to_projects[mentor].remove(project)
                else:
                    # No common slot for all mentors, will handle in second pass
                    pass
        
        # Second pass: Schedule remaining interviews, prioritizing consecutive slots
        # Sort mentors by number of remaining projects (descending)
        sorted_mentors = sorted(mentor_to_projects.keys(), 
                               key=lambda m: len(mentor_to_projects[m]), 
                               reverse=True)
        
        for mentor in sorted_mentors:
            remaining_projects = mentor_to_projects[mentor]
            
            if not remaining_projects:
                continue
                
            # Get all available slots for this mentor
            mentor_slots = self.mentor_availability[mentor][self.mentor_availability[mentor]].index.tolist()
            
            # Group into consecutive blocks
            consecutive_blocks = self._get_consecutive_slots(mentor_slots)
            
            # Try to schedule as many projects as possible in consecutive blocks
            for block in consecutive_blocks:
                # Skip if no more projects to schedule
                if not remaining_projects:
                    break
                    
                for slot in block:
                    # Skip if no more projects to schedule
                    if not remaining_projects:
                        break
                        
                    # Try to schedule the next project in this slot
                    for project in list(remaining_projects):  # Create a copy to safely modify during iteration
                        # Check if the proposer is available in this slot
                        if self.proposer_availability.loc[slot, project]:
                            # Check if this slot is still available (not already scheduled)
                            slot_available = True
                            for scheduled_key in self.schedule:
                                if scheduled_key[1] == slot and mentor in self.schedule[scheduled_key]:
                                    slot_available = False
                                    break
                                    
                            if slot_available:
                                # Schedule this interview
                                if (project, slot) in self.schedule:
                                    # Add this mentor to an existing interview
                                    self.schedule[(project, slot)].append(mentor)
                                else:
                                    # Create a new interview
                                    self.schedule[(project, slot)] = [mentor]
                                    
                                # Mark this project as scheduled
                                remaining_projects.remove(project)
                                break
        
        # Third pass: Handle any remaining unscheduled interviews
        for mentor, projects in mentor_to_projects.items():
            for project in projects:
                # Find common availability
                common_slots = self._get_common_availability(project, [mentor])
                
                if common_slots:
                    # Use the earliest available slot
                    for slot in common_slots:
                        # Check if this slot is still available for this mentor
                        slot_available = True
                        for scheduled_key in self.schedule:
                            if scheduled_key[1] == slot and mentor in self.schedule[scheduled_key]:
                                slot_available = False
                                break
                                
                        if slot_available:
                            # Schedule this interview
                            if (project, slot) in self.schedule:
                                # Add this mentor to an existing interview
                                self.schedule[(project, slot)].append(mentor)
                            else:
                                # Create a new interview
                                self.schedule[(project, slot)] = [mentor]
                            break
    
    def output_schedule(self):
        """Generate a formatted schedule output."""
        # Sort by time slot
        sorted_schedule = sorted(self.schedule.items(), key=lambda x: x[0][1])
        
        # Create a DataFrame for the schedule
        schedule_data = []
        for (project, slot), mentors in sorted_schedule:
            schedule_data.append({
                'Time Slot': slot,
                'Project ID': project,
                'Mentors': ', '.join(mentors)
            })
            
        schedule_df = pd.DataFrame(schedule_data)
        
        # Create a mentor-specific view
        mentor_schedules = {mentor: [] for mentor in self.mentors}
        
        for (project, slot), mentors in sorted_schedule:
            for mentor in mentors:
                mentor_schedules[mentor].append({
                    'Time Slot': slot,
                    'Project ID': project
                })
        
        return schedule_df, mentor_schedules
    
    def save_schedule(self, output_dir):
        """Save the schedule to CSV files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Get schedule data
        schedule_df, mentor_schedules = self.output_schedule()
        
        # Save main schedule
        schedule_df.to_csv(os.path.join(output_dir, 'complete_schedule.csv'), index=False)
        
        # Save mentor-specific schedules
        for mentor, schedule in mentor_schedules.items():
            if schedule:  # Only save if the mentor has interviews
                mentor_df = pd.DataFrame(schedule)
                mentor_df.to_csv(os.path.join(output_dir, f'{mentor}_schedule.csv'), index=False)
        
        # Create a summary of unscheduled interviews
        unscheduled = self._get_unscheduled_interviews()
        if unscheduled:
            unscheduled_df = pd.DataFrame(unscheduled)
            unscheduled_df.to_csv(os.path.join(output_dir, 'unscheduled_interviews.csv'), index=False)
    
    def _get_unscheduled_interviews(self):
        """Identify any interviews that couldn't be scheduled."""
        unscheduled = []
        
        for mentor, projects in self.mentor_preferences.items():
            for project in projects:
                # Check if this interview was scheduled
                scheduled = False
                for (scheduled_project, _), mentors in self.schedule.items():
                    if scheduled_project == project and mentor in mentors:
                        scheduled = True
                        break
                        
                if not scheduled:
                    unscheduled.append({
                        'Mentor': mentor,
                        'Project ID': project,
                        'Reason': 'No common availability'
                    })
                    
        return unscheduled
        
    def _parse_time_slot(self, time_slot):
        """
        Parse a time slot string and return the date, start time, and end time.
        
        Example: "4/23 夜 (19:00 - 21:00)" -> (4/23, 19:00, 21:00)
        """
        match = re.match(r'(\d+/\d+)\s+[^\(]+\((\d+:\d+)\s*-\s*(\d+:\d+)\)', time_slot)
        if match:
            date_str, start_time, end_time = match.groups()
            return date_str, start_time, end_time
        return None, None, None
    
    def _split_into_hourly_slots(self, time_slot):
        """
        Split a time slot into hourly slots.
        
        Example: "4/23 夜 (19:00 - 21:00)" -> ["2024/04/23 19:00 PM", "2024/04/23 20:00 PM"]
        """
        date_str, start_time, end_time = self._parse_time_slot(time_slot)
        if not (date_str and start_time and end_time):
            return []
        
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

def main():
    parser = argparse.ArgumentParser(description='Schedule interviews based on availability and preferences.')
    parser.add_argument('--proposer-file', required=True, help='CSV file with proposers\' availability')
    parser.add_argument('--mentor-file', required=True, help='CSV file with mentors\' availability')
    parser.add_argument('--preference-file', required=True, help='CSV file with mentors\' project preferences')
    parser.add_argument('--output-dir', default='schedule_output', help='Directory to save schedule files')
    
    args = parser.parse_args()
    
    scheduler = InterviewScheduler(args.proposer_file, args.mentor_file, args.preference_file)
    scheduler.schedule_interviews()
    scheduler.save_schedule(args.output_dir)
    
    print(f"Scheduling complete. Results saved to {args.output_dir}/")

if __name__ == "__main__":
    main()
