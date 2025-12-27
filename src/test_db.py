
# In src/test_db.py

# Import the functions from your database manager file
from database_manager import create_database, save_composition, load_all_compositions

def run_database_test():
    """
    A function to demonstrate and test the database operations.
    """
    print("--- Starting Database Test ---")

    # 1. Create the database and table.
    # This will create a file named 'compositions.db' in your root folder.
    create_database()

    # 2. Create some DUMMY data to save.
    # In the real app, this data will come from your melody and chord generators.
    dummy_melody = [(60, 100), (64, 100), (67, 200)] # Represents C, E, G
    dummy_chords = ["Cmaj", "Gmaj", "Fmaj"] # A simple chord progression
    
    # 3. Save a few compositions.
    print("\nSaving new compositions...")
    save_composition(
        name="My First AI Song",
        melody_events=dummy_melody,
        chord_sequence=dummy_chords,
        key="C"
    )
    save_composition(
        name="A Minor Melody",
        melody_events=[(69, 150), (72, 150), (76, 300)], # A, C, E
        chord_sequence=["Am", "Dm", "E7"],
        key="a"
    )

    # 4. Load the data back from the database to "see" it.
    print("\nLoading all saved compositions...")
    all_songs = load_all_compositions()

    # 5. Print the results to the console.
    if not all_songs:
        print("No compositions found in the database.")
    else:
        print("\n--- Compositions in Database ---")
        for song in all_songs:
            # song is a tuple: (id, name, timestamp)
            song_id, song_name, song_timestamp = song
            print(f"  ID: {song_id}, Name: {song_name}, Saved on: {song_timestamp}")
    
    print("\n--- Database Test Complete ---")


# This makes the script runnable
if __name__ == "__main__":
    run_database_test()