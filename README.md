## Development Environment Setup

A step-by-step guide to configuring the development environment, which will be useful whether you are using Anaconda or prefer another package management system.

### Prerequisites

- Python < 3.10: Make sure you have Python 3.10 or higher installed on your system as this is the version with which the application was built and tested. You can verify and install it from the [official Python website](https://www.python.org/).

### Configuration Steps

1. **Clone the Repository**
   
   Clone the GitHub repository using the following command in your terminal:
   
   ```bash
   https://github.com/landoledesma/sqs-test_connection.git
   ```

2. **Create a Virtual Environment**

   - **With Anaconda:**
     - Create a new environment:
       
       ```bash
       conda create --name your_environment python=3.x
       ```
       
     - Activate the environment:
       
       ```bash
       conda activate your_environment
       ```

   - **Without Anaconda (Python venv):**

     - Create a virtual environment:
       
       ```bash
       python3 -m venv your_environment
       ```

     - Activate the environment:
       
       - On Windows:
         
         ```bash
         .\your_environment\Scripts\activate
         ```

       - On Linux/Mac:
         
         ```bash
         source your_environment/bin/activate
         ```

   _(Replace `your_environment` with a name for your environment and `3.x` with the Python version you want to use)_
---
# Instructions for Installing Requirements from a `requirements.txt` File

## Steps:

### 1. Initial Setup

1. **Open a Terminal**
   Open a terminal or command line on your operating system.

2. **Navigate to Project Directory**
   Navigate to the root directory of the project you have downloaded from GitHub using the `cd` command. For example:
   
   ```bash
   cd path/to/your/project
   ```

3. **Check Python and pip**
   Make sure you have Python and pip installed on your system. You can check this with the following commands:
   
   ```bash
   python --version
   pip --version
   ```
   
   If you don't have Python installed or it's not in your PATH environment variable, follow the instructions to install it.

### 2. Installing Dependencies

4. **Set Up the Environment**
   Ensure you have set up and activated your Python environment correctly before running the installation commands. If you're using a virtual environment, activate it before proceeding.

5. **Install Requirements**
   - **With Anaconda:**
     If you're using Anaconda, use the following command to install the dependencies:
     
     ```bash
     conda install --file requirements.txt
     ```
   
   - **Without Anaconda (pip):**
     If you're using `venv` or another package manager other than Anaconda, use the following command:
     
     ```bash
     pip install -r requirements.txt
     ```

### 3. Verification

6. **Verify the Installation**
   Once all the dependencies are installed, verify that your environment is configured correctly by running your Python script or application.
---
## Docker Environment Setup

You will need the following prerequisites:

- An account on GitHub, GitLab, Bitbucket, etc.
- The following software installed on your local machine:
  - Docker ([Docker installation guide](https://docs.docker.com/get-docker/))
  - Docker Compose
  - AWS CLI (install it using `pip install awscli-local`)
  - PostgreSQL (installation instructions [here](https://www.postgresql.org/download/)).

### Download Docker Images

Run the following command to download the necessary Docker images:

```bash
docker pull fetchdocker/data-takehome-localstack
docker pull fetchdocker/data-takehome-postgres
```

### Run the Test Environment

Use Docker Compose to run the test environment. Create a `docker-compose.yml` file in the root of your project with the following content:

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

Then, run the following command in the directory where the `docker-compose.yml` file is located:

```bash
docker-compose up -d
```

### Access PostgreSQL

To connect to the PostgreSQL database, use the following credentials:

- Username: postgres
- Password: postgres

Run the following command to connect to the database:

```bash
psql -d postgres -U postgres -p 5432 -h localhost -W
```

Once connected, you can query the table with:

```sql
postgres=# SELECT * FROM user_logins;
```

### Access AWS Local

To read messages from the local AWS queue, use the following command:

```bash
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
```

You can also check how many messages are in the queue with:

```bash
awslocal sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/login-queue --attribute-names
```

Now you're ready to start working on the project using Docker!

---

## Docker Container Management

To manage Docker containers and stop them when you're done working or restart them if necessary, follow these steps:

### Stop the Containers

When you've finished working, you can stop the containers by running:

```bash
docker-compose down
```

This will shut down and remove the containers but will preserve persistent data like the PostgreSQL database.

### Start the Containers Again

If you need to start the containers again in the future, simply run:

```bash
docker-compose up -d
```

This will restart the containers previously configured in the `docker-compose.yml` file. You can use these commands to start and stop the Docker environment as needed for your project.
---

# Some Questions Regarding the Code

#### How are messages from the queue read?

Using `boto3`, `sqs.receive_message` is invoked to read messages from an SQS queue in an infinite loop.

#### What type of data structures are used?

In this case, dictionaries are used to map and process the data, and lists are used to store multiple messages received from the queue.

#### How is PII data masked so that duplicate values can be identified?

Using the `create_hash` function, which applies a hash function (SHA-256) to PII data (IP and device ID), allowing the identification of duplicate values without exposing the original information.

#### What is the strategy for connecting to and writing in Postgres?

A "connection pool" (SimpleConnectionPool) is used to manage connections to PostgreSQL, and SQL queries are used to insert data, executed using the `execute` method of the psycopg2 cursor.

#### Where and how is the application executed?

The application runs indefinitely in the environment where it is launched, making use of an infinite loop (`while True`) in the `main` function, which checks the queue at regular intervals and processes the received messages in each iteration.

### How could this application be implemented in production?

To deploy this application in production, you would need to set up an environment that includes all the necessary dependencies, such as PostgreSQL, boto3, among other modules. Subsequently, you can encapsulate the application in a container using technologies like Docker, making deployment and scalability easier in a cloud environment or Kubernetes cluster.

### What other components would you add to prepare this for production?

It would be beneficial to add monitoring and alerting systems to monitor the performance and health of the application. It would also be prudent to implement automated testing and continuous integration and continuous deployment (CI/CD) processes to ensure code quality and facilitate updates.

### How can this application scale with a growing dataset?

The application can scale horizontally by adding more instances to handle increased workloads. The database, on the other hand, can scale vertically to manage a larger dataset.

### How can PII be recover later?

Personal Identifiable Information (PII) can be retrieved using the deserialization mapping created in the code, which links hashes to their original values. A table containing the original values is created in PostgreSQL, and a script called "recover_values" has been created in case there is a need to retrieve some values.

### What assumptions were made?

Assumptions that may have been made during the creation of this code include that SQS messages will contain certain specific fields, that the environment configuration (such as environment variables) is set correctly, and that the database structure is prepared with the corresponding tables created. It also seems to assume that the SQS queue will be available at 'localhost:4566'.