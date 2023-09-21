## Configuración del Entorno de Desarrollo

 Guía paso a paso para configurar el entorno de desarrollo, que será útil tanto si utilizas Anaconda como si prefieres otro sistema de gestión de paquetes.

### Requisitos Previos

- Python < 3.10: Asegúrate de tener instalado Python 3.10 o mayor en tu sistema ya que este es la version con la que se construyo la aplicacion y esta probada. Puedes verificarlo e instalarlo desde la [página oficial de Python](https://www.python.org/).

### Pasos para la Configuración

1. **Clonar el Repositorio**
   
    Clona el repositorio de GitHub usando el siguiente comando en tu terminal:
   
    ```bash
    https://github.com/landoledesma/sqs-test_connection.git
    ```

2. **Crear un Entorno Virtual**

    - **Con Anaconda:**
      - Crea un nuevo entorno:
      
        ```bash
        conda create --name tu_entorno python=3.x
        ```
      
      - Activa el entorno:
      
        ```bash
        conda activate tu_entorno
        ```

    - **Sin Anaconda (Python venv):**

      - Crea un entorno virtual:
        
        ```bash
        python3 -m venv tu_entorno
        ```

      - Activa el entorno:
        
        - En Windows:
          
          ```bash
          .\tu_entorno\Scripts\activate
          ```

        - En Linux/Mac:
          
          ```bash
          source tu_entorno/bin/activate
          ```

    _(Reemplaza `tu_entorno` con un nombre para tu entorno y `3.x` con la versión de Python que deseas usar)_

---

# Instrucciones para instalar los requisitos desde un archivo `requirements.txt`

## Pasos:

### 1. Preparación Inicial

1. **Abre una Terminal**
   Abre una terminal o línea de comandos en tu sistema operativo.

2. **Navegación al Directorio del Proyecto**
   Navega al directorio raíz del proyecto que has descargado desde GitHub usando el comando `cd`. Por ejemplo:
   
   ```bash
   cd ruta/al/proyecto
   ```

3. **Verificación de Python y pip**
   Asegúrate de que tienes Python y pip instalados en tu sistema. Puedes verificarlo con los siguientes comandos:
   
   ```bash
   python --version
   pip --version
   ```
   
   Si no tienes Python instalado o no está en tu variable de entorno PATH, siga las instrucciones para instalarlo.

### 2. Instalación de Dependencias

4. **Configuración del Entorno**
   Asegúrate de configurar y activar tu entorno de Python correctamente antes de ejecutar los comandos de instalación. Si estás utilizando un entorno virtual, actívalo antes de seguir adelante.

5. **Instalación de Requisitos**
   - **Con Anaconda:**
     Si estás utilizando Anaconda, utiliza el siguiente comando para instalar las dependencias:
     
     ```bash
     conda install --file requirements.txt
     ```
   
   - **Sin Anaconda (pip):**
     Si utilizas `venv` u otro gestor que no es Anaconda, utiliza el siguiente comando:
     
     ```bash
     pip install -r requirements.txt
     ```

### 3. Verificación

6. **Verificar la Instalación**
   Una vez instaladas todas las dependencias, verifica que tu ambiente está configurado correctamente ejecutando tu script o aplicación Python.

---
## Setup docker 
Necesitarás los siguientes requisitos previos:
   - Una cuenta en GitHub, GitLab, Bitbucket, etc.
   - El siguiente software instalado en tu máquina local:
     - Docker ([Guía de instalación de Docker](https://docs.docker.com/get-docker/))
     - Docker Compose
     - AWS CLI (instálalo usando `pip install awscli-local`)
     - PostgreSQL (instrucciones de instalación [aquí](https://www.postgresql.org/download/)).

Utiliza las siguientes imágenes de Docker con datos de prueba incorporados:
   - Postgres
   - Localstack

### Ejemplo de archivo YAML de Docker Compose para ejecutar el entorno de prueba:

```yaml
version: "3.9"
services:
  localstack:
    image: fetchdocker/data-takehome-localstack
    ports:
      - "4566:4566"
  postgres:
    image: fetchdocker/data-takehome-postgres
    ports:
      - 5432:5432
```

Credenciales de PostgreSQL:
   - Contraseña: postgres
   - Nombre de usuario: postgres

Prueba el acceso local:
   - Lee un mensaje de la cola utilizando `awslocal`:
     ```bash
     awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
     ```
   - Conéctate a la base de datos PostgreSQL y verifica que la tabla esté creada:
     i. Ejecuta el siguiente comando:
     ```bash
     psql -d postgres -U postgres -p 5432 -h localhost -W
     ```
     ii. Una vez conectado a PostgreSQL, puedes consultar la tabla con:
     ```sql
     postgres=# SELECT * FROM user_logins;
     ```
```
### consideraciones 
puedes usar el comando:

  ```bash
  awslocal sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/login-queue --attribute-names 
  ```
para verificar cuantos mensajes hay en la cola 


#### ¿Cómo leerás los mensajes de la cola?

Utilizando `boto3`, se invoca `sqs.receive_message` para leer mensajes de una cola SQS en un bucle infinito.

#### ¿Qué tipo de estructuras de datos se deben utilizar?

EN este caso se utilizan diccionarios para mapear y procesar los datos, y listas para almacenar múltiples mensajes recibidos de la cola.

#### ¿Cómo enmascararás los datos PII de manera que se puedan identificar los valores duplicados?

Utilizando la función `crear_hash`, que aplica una función hash (SHA-256) a los datos PII (IP y ID del dispositivo), permitiendo identificar valores duplicados sin exponer la información original.

#### ¿Cuál será tu estrategia para conectarte y escribir en Postgres?

Se utiliza un "connection pool" (SimpleConnectionPool) para gestionar las conexiones a PostgreSQL, y se emplean consultas SQL para insertar datos, ejecutadas mediante el método `execute` del cursor de psycopg2.

#### ¿Dónde y cómo se ejecutará tu aplicación?

La aplicación se ejecuta  indefinidamente en el entorno donde se lance, haciendo uso de un bucle infinito (`while True`) en la función `main`, que consulta la cola cada cada cierto tiempo y procesa los mensajes recibidos en cada iteración.

### ¿Cómo implementarías esta aplicación en producción?

Para implementar esta aplicación en producción, configuraría un entorno que contenga todas las dependencias necesarias, tales como PostgreSQL, boto3, entre otros módulos. Posteriormente, optaría por encapsular la aplicación en un contenedor usando tecnologías como Docker, facilitando así el despliegue y la escalabilidad en un entorno de nube o en un clúster de Kubernetes.

### ¿Qué otros componentes agregarías para preparar esto para producción?

Sería beneficioso agregar sistemas de monitoreo y alerta, para supervisar el rendimiento y la salud de la aplicación. También sería prudente implementar pruebas automatizadas, y procesos de integración y despliegue continuo (CI/CD) para asegurar la calidad del código y facilitar las actualizaciones.

### ¿Cómo puede escalar esta aplicación con un conjunto de datos en crecimiento?

La aplicación puede escalar horizontalmente, agregando más instancias para manejar una mayor carga de trabajo. La base de datos, por su parte, puede escalarse verticalmente para administrar un conjunto de datos más amplio.

### ¿Cómo se puede recuperar la PII más tarde?

La Información Personal Identificable (PII) puede recuperarse utilizando el mapeo de desenmascaramiento creado en el código, que vincula los hashes con sus valores originales. 

### ¿Cuáles son las suposiciones que hiciste?

Las suposiciones que pueden haberse realizado durante la creación de este código incluyen que los mensajes de SQS contendrán ciertos campos específicos, que la configuración del entorno (como las variables de entorno) está establecida correctamente, y que la estructura de la base de datos está preparada con las tablas correspondientes creadas. También parece asumirse que la cola SQS estará disponible en 'localhost:4566'