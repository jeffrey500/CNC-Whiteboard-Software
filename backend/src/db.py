from src.model import Image, SVG


def image_insert(conn, name, timestamp, image_path, gcode_filepath, render_filepath):
    try:
        with conn.cursor() as cursor:

            # define and execute the INSERT query
            insert_query = "INSERT INTO images (name, timestamp, image_filepath, gcode_filepath, render_filepath) VALUES (%s, %s, %s, %s, %s)"
            data_to_insert = (name, timestamp, image_path, gcode_filepath, render_filepath)

            cursor.execute(insert_query, data_to_insert)
            conn.commit()

    except Exception as error:
        conn.rollback()
        raise error


def get_images(conn):
    try:
        with conn.cursor() as cursor:
            # define and execute the SELECT query
            query = "SELECT * FROM images ORDER BY timestamp DESC;"
            cursor.execute(query)

            # fetch all rows from the table
            rows = cursor.fetchall()

            # return data
            return [Image(id=row[0], name=row[1], timestamp=row[2], image_filepath=row[3], gcode_filepath=row[4], render_filepath=row[5]) for row in
                    rows]

    except Exception as error:
        raise error


def get_image(conn, id):
    try:
        with conn.cursor() as cursor:
            # define and execute the SELECT query
            query = "SELECT * FROM images WHERE id = %s ORDER BY timestamp;"
            cursor.execute(query, (id,))

            # fetch row with id
            row = cursor.fetchone()

            # check if row exists
            if row is None:
                raise ValueError(f"Image with id {id} not found.")

            # print or process your list of data
            return Image(id=row[0], name=row[1], timestamp=row[2], image_filepath=row[3], gcode_filepath=row[4], render_filepath=row[5])

    except Exception as error:
        raise error


def delete_image(conn, id):
    try:
        with conn.cursor() as cursor:
            # save filename to return
            img = get_image(conn, id)
            output = (img.image_filepath, img.gcode_filepath, img.render_filepath)

            # define and execute the DELETE query
            delete_query = "DELETE FROM images WHERE id = %s"
            cursor.execute(delete_query, (id,))

            # save changes
            conn.commit()

            return output

    except Exception as error:
        conn.rollback()
        raise error


def svg_insert(conn, name, timestamp, svg_filepath, gcode_filepath, render_filepath):
    try:
        with conn.cursor() as cursor:

            # define and execute the INSERT query
            insert_query = "INSERT INTO svgs (name, timestamp, svg_filepath, gcode_filepath, render_filepath) VALUES (%s, %s, %s, %s, %s)"
            data_to_insert = (name, timestamp, svg_filepath, gcode_filepath, render_filepath)

            cursor.execute(insert_query, data_to_insert)
            conn.commit()

    except Exception as error:
        conn.rollback()
        raise error


def get_svgs(conn):
    try:
        with conn.cursor() as cursor:
            # define and execute the SELECT query
            query = "SELECT id, name, timestamp, svg_filepath, gcode_filepath, render_filepath FROM svgs ORDER BY timestamp DESC;"
            cursor.execute(query)

            # fetch all rows from the table
            rows = cursor.fetchall()

            # return data
            return [SVG(id=row[0], name=row[1], timestamp=row[2], svg_filepath=row[3], gcode_filepath=row[4], render_filepath=row[5]) for row in
                    rows]

    except Exception as error:
        raise error


def get_svg(conn, id):
    try:
        with conn.cursor() as cursor:
            # define and execute the SELECT query
            query = "SELECT id, name, timestamp, svg_filepath, gcode_filepath, render_filepath FROM svgs WHERE id = %s ORDER BY timestamp;"
            cursor.execute(query, (id,))

            # fetch row with id
            row = cursor.fetchone()

            # check if row exists
            if row is None:
                raise ValueError(f"SVG with id {id} not found.")

            # print or process your list of data
            return SVG(id=row[0], name=row[1], timestamp=row[2], svg_filepath=row[3], gcode_filepath=row[4], render_filepath=row[5])

    except Exception as error:
        raise error

def delete_svg(conn, id):
    try:
        with conn.cursor() as cursor:
            # save filename to return
            svg = get_svg(conn, id)
            output = (svg.svg_filepath, svg.gcode_filepath, svg.render_filepath)

            # define and execute the DELETE query
            delete_query = "DELETE FROM svgs WHERE id = %s"
            cursor.execute(delete_query, (id,))

            # save changes
            conn.commit()

            return output

    except Exception as error:
        conn.rollback()
        raise error