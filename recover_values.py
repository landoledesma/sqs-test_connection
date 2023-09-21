from psycopg2.pool import SimpleConnectionPool
import os

# Connection Pool Configuration
DB_POOL = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=os.getenv('DB_NAME'), 
    user=os.getenv('DB_USER'), 
    password=os.getenv('DB_PASSWORD'), 
    host=os.getenv('DB_HOST'), 
    port=os.getenv('DB_PORT')
)

def get_original_values(cursor, hash_vals):
    placeholders = ", ".join(["%s"] * len(hash_vals))
    cursor.execute(f"SELECT hash_val, original_val FROM map_desmask WHERE hash_val IN ({placeholders})", tuple(hash_vals))
    results = cursor.fetchall()
    result_dict = {row[0]: row[1] for row in results}
    return [result_dict.get(hash_val) for hash_val in hash_vals]

def main():
    # Get a connection from the pool
    conn = DB_POOL.getconn()
    cursor = conn.cursor()

    # Prompt the user to input the hashes to search for
    hash_device_ids = input("Enter the hashes of the device_ids, separated by commas: ").split(', ')
    hash_ips = input("Enter the hashes of the IPs, separated by commas: ").split(', ')
    
    # Get and display the original values
    original_device_ids = get_original_values(cursor, hash_device_ids)
    original_ips = get_original_values(cursor, hash_ips)

    for i, original in enumerate(original_device_ids):
        if original:
            print(f"The original device_id for the hash {hash_device_ids[i]} is: {original}")
        else:
            print(f"Device_id not found for the hash {hash_device_ids[i]}.")

    for i, original in enumerate(original_ips):
        if original:
            print(f"The original IP for the hash {hash_ips[i]} is: {original}")
        else:
            print(f"IP not found for the hash {hash_ips[i]}.")

    # Close the connection
    cursor.close()
    DB_POOL.putconn(conn)

# Check if the script is being run directly (not imported)
if __name__ == "__main__":
    main()
