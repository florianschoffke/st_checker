import subprocess
import sys
import shutil

def run_script(script_name):
    try:
        # Run the script using the same Python interpreter
        result = subprocess.run([sys.executable, script_name], check=True, capture_output=True, text=True)
        print(f"Output of {script_name}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {script_name}: {e.stderr}")

def main():
    temp_dir = "temp"
    # First step: Run the search_and_extract script
    run_script('search_and_extract.py') # we have a list of all Schlüsseltabellen relevant for E-Rezept-Fachdienst 
    
    # Deal with kbv.st.all
    run_script('compare_kbv_st_all.py')
    
    # Deal with kbv.st.all-rc
    run_script('process_all-rc.py')
    
    # Check for changes
    run_script('check_for_rc_changes.py')
    
    # Get unique Schlüsseltabellen
    run_script('unique_st.py')

    # Delete the temp directory
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
