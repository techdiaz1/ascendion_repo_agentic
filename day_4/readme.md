To install pgvector follow the below steps:

1. Download pgvector vector.v0.8.6-pg18.zip file from the below link 

https://github.com/andreiramani/pgvector_pgsql_windows/releases

2. From downloads > open the zip file > copy vector.dll file from the lib folder

3. Paste the file in C:\Program Files\PostgreSQL\18\lib folder {may require admin login}

4. From the zip file, open share > extension > copy vector.control file and vector--0.8.6.sql file

5. Paste the vector.control and vector--0.8.6.sql files in C:\Program Files\PostgreSQL\18\share\extension folder    {may require admin login}

6. open pgadmin4, server > database > demo_db > right click - query tool >

Run the following sql query 

CREATE EXTENSION IF NOT EXISTS vector;

SELECT *
FROM pg_available_extensions
WHERE name = 'vector';

If you get a response that the installed version is 0.8.6, then pgvector is successfully installed
