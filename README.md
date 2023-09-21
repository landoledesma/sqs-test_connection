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
## Configuración del Entorno Docker
Necesitarás los siguientes requisitos previos:
   - Una cuenta en GitHub, GitLab, Bitbucket, etc.
   - El siguiente software instalado en tu máquina local:
     - Docker ([Guía de instalación de Docker](https://docs.docker.com/get-docker/))
     - Docker Compose
     - AWS CLI (instálalo usando `pip install awscli-local`)
     - PostgreSQL (instrucciones de instalación [aquí](https://www.postgresql.org/download/)).

### Descarga las Imágenes de Docker

Ejecuta el siguiente comando para descargar las imágenes de Docker necesarias:

```bash
docker pull fetchdocker/data-takehome-localstack
docker pull fetchdocker/data-takehome-postgres
```

### Ejecuta el Entorno de Prueba

Utiliza Docker Compose para ejecutar el entorno de prueba. Crea un archivo `docker-compose.yml` en la raíz de tu proyecto con el siguiente contenido:

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

Luego, ejecuta el siguiente comando en el directorio donde se encuentra el archivo `docker-compose.yml`:

```bash
docker-compose up -d
```

### Acceso a PostgreSQL

Para conectarte a la base de datos PostgreSQL, utiliza las siguientes credenciales:

- Nombre de usuario: postgres
- Contraseña: postgres

Ejecuta el siguiente comando para conectarte a la base de datos:

```bash
psql -d postgres -U postgres -p 5432 -h localhost -W
```

Una vez conectado, puedes consultar la tabla con:

```sql
postgres=# SELECT * FROM user_logins;
```

### Acceso a AWS Local

Para leer mensajes de la cola de AWS localmente, utiliza el siguiente comando:

```bash
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
```

También puedes verificar cuántos mensajes hay en la cola con:

```bash
awslocal sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/login-queue --attribute-names
```

¡Ahora estás listo para comenzar a trabajar en el proyecto utilizando Docker!


## Gestión de Contenedores Docker

Para gestionar los contenedores Docker y detenerlos cuando termines de trabajar o reiniciarlos en caso de ser necesario, sigue estos pasos:

### Detener los Contenedores

Cuando hayas terminado de trabajar, puedes detener los contenedores ejecutando:

```bash
docker-compose down
```

Esto apagará y eliminará los contenedores, pero conservará los datos persistentes como la base de datos PostgreSQL.

### Volver a Encender los Contenedores

Si necesitas volver a encender los contenedores en el futuro, simplemente ejecuta:

```bash
docker-compose up -d
```

Esto reiniciará los contenedores previamente configurados en el archivo `docker-compose.yml`. Puedes utilizar estos comandos para iniciar y detener el entorno Docker según sea necesario para el proyecto.

---

# Algunas cuestiones referentes al codigo 

#### ¿Cómo se leen los mensajes de la cola?

Utilizando `boto3`, se invoca `sqs.receive_message` para leer mensajes de una cola SQS en un bucle infinito.

#### ¿Qué tipo de estructuras de datos se utiliza?

En este caso se utilizan diccionarios para mapear y procesar los datos, y listas para almacenar múltiples mensajes recibidos de la cola.

#### ¿Cómo se enmascaran los datos PII de manera que se puedan identificar los valores duplicados?

Utilizando la función `crear_hash`, que aplica una función hash (SHA-256) a los datos PII (IP y ID del dispositivo), permitiendo identificar valores duplicados sin exponer la información original.

#### ¿Cuál es la estrategia para conectarse y escribir en Postgres?

Se utiliza un "connection pool" (SimpleConnectionPool) para gestionar las conexiones a PostgreSQL, y se emplean consultas SQL para insertar datos, ejecutadas mediante el método `execute` del cursor de psycopg2.

#### ¿Dónde y cómo se ejecuta la aplicación?

La aplicación se ejecuta  indefinidamente en el entorno donde se lance, haciendo uso de un bucle infinito (`while True`) en la función `main`, que consulta la cola cada cada cierto tiempo y procesa los mensajes recibidos en cada iteración.

### ¿Cómo se podria implementar esta aplicación en producción?

Para implementar esta aplicación en producción, se deberia configurar un entorno que contenga todas las dependencias necesarias, tales como PostgreSQL, boto3, entre otros módulos. Posteriormente, se puede encapsular la aplicación en un contenedor usando tecnologías como Docker, facilitando así el despliegue y la escalabilidad en un entorno de nube o en un clúster de Kubernetes.

### ¿Qué otros componentes agregarías para preparar esto para producción?

Sería beneficioso agregar sistemas de monitoreo y alerta, para supervisar el rendimiento y la salud de la aplicación. También sería prudente implementar pruebas automatizadas, y procesos de integración y despliegue continuo (CI/CD) para asegurar la calidad del código y facilitar las actualizaciones.

### ¿Cómo puede escalar esta aplicación con un conjunto de datos en crecimiento?

La aplicación puede escalar horizontalmente, agregando más instancias para manejar una mayor carga de trabajo. La base de datos, por su parte, puede escalarse verticalmente para administrar un conjunto de datos más amplio.

### ¿Cómo se puede recuperar la PII más tarde?

La Información Personal Identificable (PII) puede recuperarse utilizando el mapeo de desenmascaramiento creado en el código, que vincula los hashes con sus valores originales se he creado una tabla en postgres que contiene los valores originales y se ha creado un script llamado recover_values en caso de que se necesite recuperar algunos valores. 

### ¿Cuáles son las suposiciones que se hiciceron?

Las suposiciones que pueden haberse realizado durante la creación de este código incluyen que los mensajes de SQS contendrán ciertos campos específicos, que la configuración del entorno (como las variables de entorno) está establecida correctamente, y que la estructura de la base de datos está preparada con las tablas correspondientes creadas. También parece asumirse que la cola SQS estará disponible en 'localhost:4566'