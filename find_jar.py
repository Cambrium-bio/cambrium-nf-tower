import os
import zipfile
import jaydebeapi

def test_h2_jar(jar_path):
    """Test if the given JAR file is a valid H2 driver"""
    try:
        # Check if file contains org.h2.Driver class
        with zipfile.ZipFile(jar_path, 'r') as jar:
            if any('org/h2/Driver.class' in name for name in jar.namelist()):
                print(f"✓ Found H2 Driver class in {jar_path}")
                
                # Try to actually use the driver
                try:
                    conn = jaydebeapi.connect(
                        'org.h2.Driver',
                        'jdbc:h2:.db/h2/tower',
                        ['sa', ''],
                        jar_path
                    )
                    print("✓ Successfully tested connection with this JAR")
                    conn.close()
                    return True
                except Exception as e:
                    print(f"✗ JAR file found but connection test failed: {e}")
                    return False
        
        print(f"✗ No H2 Driver class found in {jar_path}")
        return False
    except zipfile.BadZipFile:
        print(f"✗ Not a valid JAR file: {jar_path}")
        return False
    except Exception as e:
        print(f"✗ Error testing JAR file: {e}")
        return False

def find_h2_jar():
    """Search for H2 JAR files recursively in current directory"""
    print(os.getcwd())
    possible_locations = [
        './',           # Gradle build directory
    ]
    
    found_jars = []
    
    # Search in specific locations first
    for location in possible_locations:
        if os.path.exists(location):
            for root, _, files in os.walk(location):
                for file in files:
                    #if 'h2' in file.lower() and file.endswith('.jar'):
                    if file.endswith('.jar'):
                        jar_path = os.path.join(root, file)
                        found_jars.append(jar_path)
    
    # If no JARs found in common locations, search entire directory
    if not found_jars:
        for root, _, files in os.walk('.'):
            for file in files:
                if 'h2' in file.lower() and file.endswith('.jar'):
                    jar_path = os.path.join(root, file)
                    found_jars.append(jar_path)
    
    return found_jars

if __name__ == "__main__":
    print("Searching for H2 JAR files...")
    jar_files = find_h2_jar()
    
    if not jar_files:
        print("No H2 JAR files found in directory tree")
    else:
        print(f"\nFound {len(jar_files)} potential H2 JAR files:")
        working_jars = []
        
        for jar_path in jar_files:
            print(f"\nTesting: {jar_path}")
            if test_h2_jar(jar_path):
                working_jars.append(jar_path)
        
        if working_jars:
            print("\n✓ Working H2 JAR files found:")
            for jar in working_jars:
                print(f"  - {jar}")
            
            # Update the db.py file path
            print("\nTo update your db.py, use this path:")
            print(f"self.jdbc_url = 'jdbc:h2:.db/h2/tower'")
            print(f"jar_path = '{working_jars[0]}'  # Use this in your connect() method")
        else:
            print("\n✗ No working H2 JAR files found") 