import json
import os
import mysql.connector

def lambda_handler(event, context):
    try:
        db_host = os.environ['RDS_HOST']
        db_user = os.environ['RDS_USER']
        db_password = os.environ['RDS_PASSWORD']
        db_name = os.environ['RDS_DB']

        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        cursor = connection.cursor()

        data = json.loads(event['body'])
        artist_id = data['artist_id']
        name = data.get('name')
        genre = data.get('genre')
        bio = data.get('bio')

        update_fields = []
        update_values = []

        if name:
            update_fields.append("name = %s")
            update_values.append(name)
        if genre:
            update_fields.append("genre = %s")
            update_values.append(genre)
        if bio:
            update_fields.append("bio = %s")
            update_values.append(bio)

        if not update_fields:
            return {
                'statusCode': 400,
                'body': json.dumps('Bad request. No fields to update.')
            }

        update_values.append(artist_id)

        sql = f"UPDATE artists SET {', '.join(update_fields)} WHERE artist_id = %s"
        cursor.execute(sql, tuple(update_values))
        connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('Artist updated successfully')
        }
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('Bad request. Missing required parameters.')
        }
    except mysql.connector.Error as err:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Database error: {str(err)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()
