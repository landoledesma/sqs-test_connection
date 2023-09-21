from psycopg2.pool import SimpleConnectionPool
import os

# Configuración de Connection Pool
DB_POOL = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=os.getenv('DB_NAME'), 
    user=os.getenv('DB_USER'), 
    password=os.getenv('DB_PASSWORD'), 
    host=os.getenv('DB_HOST'), 
    port=os.getenv('DB_PORT')
)

def obtener_valores_originales(cursor, hash_vals):
    placeholders = ", ".join(["%s"] * len(hash_vals))
    cursor.execute(f"SELECT hash_val, original_val FROM map_desmask WHERE hash_val IN ({placeholders})", tuple(hash_vals))
    resultados = cursor.fetchall()
    resultado_dict = {row[0]: row[1] for row in resultados}
    return [resultado_dict.get(hash_val) for hash_val in hash_vals]

def main():
   # Obtener una conexión del pool
    conn = DB_POOL.getconn()
    cursor = conn.cursor()

    # Solicita al usuario que ingrese los hashes para buscar
    hash_device_ids = input("Ingrese los hashes de los device_ids, separados por comas: ").split(', ')
    hash_ips = input("Ingrese los hashes de las IPs, separados por comas: ").split(', ')
    
    # Obtener y mostrar los valores originales
    device_ids_originales = obtener_valores_originales(cursor, hash_device_ids)
    ips_originales = obtener_valores_originales(cursor, hash_ips)

    for i, original in enumerate(device_ids_originales):
        if original:
            print(f"El device_id original para el hash {hash_device_ids[i]} es: {original}")
        else:
            print(f"No se encontró un device_id con el hash {hash_device_ids[i]}.")

    for i, original in enumerate(ips_originales):
        if original:
            print(f"La IP original para el hash {hash_ips[i]} es: {original}")
        else:
            print(f"No se encontró una IP con el hash {hash_ips[i]}.")

    # Cerrar la conexión
    cursor.close()
    DB_POOL.putconn(conn)

# Verifica si el script se está ejecutando directamente (no está siendo importado)
if __name__ == "__main__":
    main()
