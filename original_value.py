import psycopg2

def obtener_valor_original(cursor, hash_val):
    cursor.execute("SELECT original_val FROM mapeo_desenmascaramiento WHERE hash_val = %s", (hash_val,))
    resultado = cursor.fetchone()
    if resultado:
        return resultado[0]
    else:
        return None

def main():
    # Conexión a la base de datos
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='localhost', port='5433')
    cursor = conn.cursor()

    # Solicita al usuario que ingrese los hashes para buscar
    hash_device_id = input("Ingrese el hash del device_id: ")  
    hash_ip = input("Ingrese el hash de la IP: ")  
    
    # Obtener y mostrar los valores originales
    device_id_original = obtener_valor_original(cursor, hash_device_id)
    ip_original = obtener_valor_original(cursor, hash_ip)

    if device_id_original:
        print(f"El device_id original es: {device_id_original}")
    else:
        print("No se encontró un device_id con ese hash.")

    if ip_original:
        print(f"La IP original es: {ip_original}")
    else:
        print("No se encontró una IP con ese hash.")

    # Cerrar la conexión
    cursor.close()
    conn.close()

# Verifica si el script se está ejecutando directamente (no está siendo importado)
if __name__ == "__main__":
    main()
