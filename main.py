import pandas as pd
import json
import os
import numpy as np

class DataMatcher:
    def __init__(self):
        self.database_file = "database.csv"

    def read_csv(self, file_path):
        return pd.read_csv(file_path)

    def match_subjects(self, professionals_data, demands_data):
        matched_data = []

        for _, professional_row in professionals_data.iterrows():
            professional_id = professional_row['id_prof']
            professional_name = professional_row['name']
            professional_subject = professional_row['subject']

            # Filter demands for the current professional's subject
            relevant_demands = demands_data[demands_data['subject'] == professional_subject]

            for _, demand_row in relevant_demands.iterrows():
                demand_id = demand_row['id_data']
                subject = demand_row['subject']
                due_date = demand_row['due_date']

                # Check if the demand is already in matched_data
                existing_demand = next(
                    (item for item in matched_data if item['demand_id'] == demand_id),
                    None
                )

                if existing_demand:
                    # If the demand is already attributed to another professional, split it
                    existing_demand['professional_id'] = [existing_demand['professional_id'], professional_id]
                    existing_demand['professional_name'] = [existing_demand['professional_name'], professional_name]
                else:
                    matched_data.append({
                        'professional_id': professional_id,
                        'professional_name': professional_name,
                        'subject': subject,
                        'due_date': due_date,
                        'demand_id': demand_id
                    })

        return matched_data

    def write_to_file(self, data, output_file):
    # Convert int64 to int before writing to JSON
        for entry in data:
            for key, value in entry.items():
                if isinstance(value, np.int64):
                    entry[key] = int(value)

        with open(output_file, 'w') as file:
            json.dump(data, file, indent=2, default=str)

    def execute_main_logic(self):
        if not os.path.exists(self.database_file):
            professionals_csv = self.get_file_path("professionals CSV")
            demands_csv = self.get_file_path("demands CSV")

            professionals_data = self.read_csv(professionals_csv)
            demands_data = self.read_csv(demands_csv)

            matched_data = self.match_subjects(professionals_data, demands_data)

            self.write_to_file(matched_data, "database.json")

            # Flatten the list of dictionaries and create a DataFrame
            matched_data_df = pd.DataFrame(matched_data)
            matched_data_df.to_csv(self.database_file, index=False)

            print("Matching subjects saved to database.json and database.csv")
        else:
            print(f"Using existing database: {self.database_file}")

    def get_file_path(self, prompt):
        return input(f"Enter the path to the {prompt} file: ")

    def show_all_matched_data(self):
        matched_data_df = self.read_csv(self.database_file)
        print(matched_data_df)

    def show_specific_data(self, professional_name):
        matched_data_df = self.read_csv(self.database_file)
        if professional_name in matched_data_df['professional_name'].unique():
            professional_data = matched_data_df[matched_data_df['professional_name'] == professional_name]
            print(professional_data)
        else:
            print(f"No data found for professional: {professional_name}")

    def search_by_id(self, demand_id):
        matched_data_df = self.read_csv(self.database_file)

        if 'demand_id' in matched_data_df.columns:
            if demand_id in matched_data_df['demand_id'].unique():
                specific_data = matched_data_df[matched_data_df['demand_id'] == demand_id]
                print(specific_data)
            else:
                print(f"No data found for ID: {demand_id}")
        else:
            print("The 'demand_id' column is not present in the database.")

    def show_demands_by_due_date(self):
        matched_data_df = self.read_csv(self.database_file)
        demands_by_due_date = matched_data_df.sort_values(by=['due_date'])
        print(demands_by_due_date)

    def add_more_demands(self):
        professionals_csv = self.get_file_path("professionals CSV")
        demands_csv = self.get_file_path("demands CSV")

        professionals_data = self.read_csv(professionals_csv)
        demands_data = self.read_csv(demands_csv)

        new_demands = self.match_subjects(professionals_data, demands_data)

        # Append the new demands to the existing database
        existing_data = self.read_csv(self.database_file)
        new_data = existing_data.append(pd.DataFrame(new_demands), ignore_index=True)

        # Save the updated data to the database file
        new_data.to_csv(self.database_file, index=False)

        print("New demands added to the database.")

    def complete_demands(self):
        choice = input("Choose completion method:\n1. Complete all demands of a specific professional\n2. Complete specific demand by ID\n3. Complete demands by date range\nEnter your choice (1-3): ")

        if choice == '1':
            professional_name = input("Enter the professional name: ")
            self.complete_by_professional(professional_name)
        elif choice == '2':
            demand_id = int(input("Enter the demand ID to complete: "))
            self.complete_by_id(demand_id)
        elif choice == '3':
            start_date = input("Enter the start date (YYYY-MM-DD): ")
            end_date = input("Enter the end date (YYYY-MM-DD): ")
            self.complete_by_date_range(start_date, end_date)
        else:
            print("Invalid choice.")

    def complete_by_professional(self, professional_name):
        matched_data_df = self.read_csv(self.database_file)
        professional_data = matched_data_df[matched_data_df['professional_name'] == professional_name]

        if not professional_data.empty:
            self.update_database_after_completion(professional_data)
            print(f"All demands for {professional_name} completed.")
        else:
            print(f"No demands found for {professional_name}.")

    def complete_by_id(self, demand_id):
        matched_data_df = self.read_csv(self.database_file)
        demand_data = matched_data_df[matched_data_df['demand_id'] == demand_id]

        if not demand_data.empty:
            self.update_database_after_completion(demand_data)
            print(f"Demand with ID {demand_id} completed.")
        else:
            print(f"No demand found with ID {demand_id}.")

    def complete_by_date_range(self, start_date, end_date):
        matched_data_df = self.read_csv(self.database_file)
        date_range_data = matched_data_df[
            (matched_data_df['due_date'] >= start_date) & (matched_data_df['due_date'] <= end_date)
        ]

        if not date_range_data.empty:
            self.update_database_after_completion(date_range_data)
            print(f"All demands in the date range {start_date} to {end_date} completed.")
        else:
            print(f"No demands found in the specified date range.")

    def update_database_after_completion(self, completed_data):
    # Read the existing database
        existing_data = self.read_csv(self.database_file)

        # Identify the indices of the completed demands in the existing database
        indices_to_remove = completed_data.index

        # Remove the completed demands from the existing database
        updated_data = existing_data.drop(indices_to_remove)

        # Save the updated data to the database file
        updated_data.to_csv(self.database_file, index=False)

        print("Database updated after completing demands.")

    def main_menu(self):
        while True:
            print("\nMain Menu:")
            print("1. Show all matched data")
            print("2. Show specific data for a professional")
            print("3. Show demands organized by due date")
            print("4. Search for data by ID")
            print("5. Add more demands")
            print("6. Complete demands")
            print("7. Exit")

            choice = input("Enter your choice (1-7): ")

            if choice == '1':
                self.show_all_matched_data()
            elif choice == '2':
                professional_name = input("Enter the professional name: ")
                self.show_specific_data(professional_name)
            elif choice == '3':
                self.show_demands_by_due_date()
            elif choice == '4':
                demand_id = int(input("Enter the ID to search for: "))
                self.search_by_id(demand_id)
            elif choice == '5':
                self.add_more_demands()
            elif choice == '6':
                self.complete_demands()
            elif choice == '7':
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")

    def run(self):
        self.execute_main_logic()
        self.main_menu()

if __name__ == "__main__":
    matcher = DataMatcher()
    matcher.run()
