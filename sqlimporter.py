import pymssql

# Establish a connection to the remote MySQL server
def connect():
    connection = pymssql.connect(
        host='192.168.1.110',
        user='sa',
        password='M0nk3ym@n6797',
        database='real_estate'
    )
    return connection

def insert_data(connection, data):
    try:
        with connection.cursor() as cursor:
            # Execute SQL INSERT statement
            sql = "INSERT INTO dbo.listings (Price, Address, Link, Bed, Bath, Parking, Area, Type) VALUES (%d, %s, %s, %d, %d, %d, %d, %s)"
            cursor.execute(sql, (data['price'], data['address'], data['link'], data['bed'], data['bath'], data['parking'], data['area'], data['type']))

        # Commit transaction
        connection.commit()

        print("Data imported successfully.")

    except pymssql.Error as e:
        print(f"Error importing data: {e}")

def disconnect(connection):
    # Close connection
    connection.close()