from backend.model import Image

def image_insert(conn, name, timestamp, image_path, gcode_path):
    try:
        with conn.cursor() as cursor:

            #define and execute the INSERT query
            insert_query = "INSERT INTO images (name, timestamp, image_path, gcode_path) VALUES (%s, %s, %s, %s)"
            data_to_insert = (name, timestamp, image_path, gcode_path)

            cursor.execute(insert_query, data_to_insert)
            conn.commit()

    except Exception as error:
        conn.rollback()
        raise error


def get_images(conn):
    try:
        with conn.cursor() as cursor:
            # define and execute the SELECT query
            query = "SELECT * FROM images ORDER BY timestamp;"
            cursor.execute(query)

            # fetch all rows from the table
            rows = cursor.fetchall()

            # return data
            return [Image(row[0], row[1], row[2], row[3], row[4]) for row in rows]

    except Exception as error:
        raise error


def get_image(conn, id):
    try:
        with conn.cursor() as cursor:
            # define and execute the SELECT query
            query = "SELECT * FROM images WHERE id = %s ORDER BY timestamp;"
            cursor.execute(query, (id,))

            # fetch all rows from the table
            rows = cursor.fetchall()
            row = rows[0]

            # print or process your list of data
            return Image(row[0], row[1], row[2], row[3], row[4])

    except Exception as error:
        raise error


def delete_image(conn, id):
    try:
        with conn.cursor() as cursor:
            #define and execute the DELETE query
            delete_query = "DELETE FROM images WHERE id = %s"
            cursor.execute(delete_query, (id,))

            return cursor.rowcount

    except Exception as error:
        raise error

def svg_insert(conn, name, timestamp, svg_url):
    try:
        with conn.cursor() as cursor:
            #define and execute the INSERT query
            instert_query = "INSERT INTO images (name, timestamp, image_url) VALUES (%s, %s, %s)"
            data_to_insert = (name, timestamp, svg_url)

            cursor.execute(instert_query, data_to_insert)
            conn.commit()

    except Exception as error:
        conn.rollback()
        raise error


def get_svgs(conn):
    try:
        with conn.cursor() as cursor:
            # define and execute the SELECT query
            query = "SELECT * FROM images ORDER BY timestamp;"
            cursor.execute(query)

            # fetch all rows from the table
            rows = cursor.fetchall()

            # return data
            return [Image(row[0], row[1], row[2], row[3]) for row in rows]

    except Exception as error:
        raise error


def get_svg(conn, id):
    try:
        with conn.cursor() as cursor:
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


def delete_svg(conn, id):
    try:
        with conn.cursor() as cursor:
            #define and execute the DELETE query
            delete_query = "DELETE FROM svgs WHERE id = %s"
            cursor.execute(delete_query, (id,))

            return cursor.rowcount

    except Exception as error:
        raise error


#Need to create a table for svgs
#Need to extend colum for gcode for images