from backend.model import Image

def insert(conn, name, timestamp, image_url):
    print("insert", name, timestamp, image_url)

    # open a cursor to perform database operations
    cur = conn.cursor()

    # define SQL query using placeholders
    insert_query = """
                   INSERT INTO images (name, timestamp, image_url)
                   VALUES (%s, %s, %s); \
                   """

    # data to insert (as a tuple)
    data_to_insert = (name, timestamp, image_url)

    try:
        # execute the query
        cur.execute(insert_query, data_to_insert)

        # commit the transaction to save changes
        conn.commit()

    except Exception as error:
        print(f"Error: {error}")
        conn.rollback()  # rollback transaction if it fails
        raise error

    finally:
        # close the communication with the database
        cur.close()


def selectAll(conn):
    try:
        # create a cursor object
        cursor = conn.cursor()

        # define and execute the SELECT query
        query = "SELECT * FROM images ORDER BY timestamp;"
        cursor.execute(query)

        # fetch all rows from the table
        rows = cursor.fetchall()

        # print or process your list of data
        return [Image(row[0], row[1], row[2], row[3]) for row in rows]

    except Exception as error:
        raise error

    finally:
        if 'cursor' in locals():
            cursor.close()


def select(conn, id):
    try:
        # create a cursor object
        cursor = conn.cursor()

        # define and execute the SELECT query
        query = "SELECT * FROM images WHERE id = %s ORDER BY timestamp;"
        cursor.execute(query, (id,))

        # fetch all rows from the table
        rows = cursor.fetchall()
        row = rows[0]

        # print or process your list of data
        return Image(row[0], row[1], row[2], row[3])

    except Exception as error:
        raise error

    finally:
        if 'cursor' in locals():
            cursor.close()