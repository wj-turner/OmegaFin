import socketio
import psycopg2
import datetime
# Database connection parameters

open_positions = set()
# Establishing the connection
conn = psycopg2.connect(
            user="forexuser",
            password="forexpassword",
            host="postgres",
            database="configdb"
                                      )


def fetch_open_positions_from_db():
    """Fetch open positions from the database and return a set of tickets."""
    open_positions = set()
    with conn.cursor() as cur:
        try:
            cur.execute("SELECT ticket FROM trade_orders WHERE position_status = 'open'")
            for record in cur.fetchall():
                open_positions.add(record[0])  # Assuming ticket is the first column
        except Exception as e:
            print(f"Failed to fetch open positions from database: {e}")
    return open_positions


# Create a Socket.IO client
sio = socketio.Client()
def handle_mt5_account_info(data):
    positions = data.get('data', {}).get('positions', [])
    open_positions = fetch_open_positions_from_db()
    new_positions = set(position['ticket'] for position in data.get('data', {}).get('positions', []))
    closed_positions = open_positions - new_positions
    # Request data for closed positions
    for ticket in closed_positions:
        sio.emit('request_closed_position_data', {'ticket': ticket})


    with conn.cursor() as cur:
        for position in positions:
            # Align fields with the SQLAlchemy model
            fields = [
                'ticket', 'symbol', 'price_open', 'price_current', 
                'sl', 'tp', 'swap', 
                'profit', 'reason', 'magic', 'comment', 'external_id'
            ]
            values = [position.get(field) for field in fields]
            
            # Convert epoch to datetime for time_setup and time_done
            time_setup = datetime.datetime.fromtimestamp(position.get('time'))
            time_done = datetime.datetime.fromtimestamp(position.get('time_update')) if position.get('time_update') else None
            
            # Assuming the type field in your positions data matches the type in your TradeOrder model
            type_ = position.get('type')
            # Adding converted datetime and type to values
            values.extend([time_setup, time_done, type_])

            # Add default values for state and position_status
            state = position.get('state', 0)  # Assuming a default state, adjust as needed
            position_status = 'open'  # Assuming positions from the socket are always open; adjust logic as needed
            volume_initial = position.get('volume', 0)
            volume_current = position.get('volume', 0)
            # Extend values to include state and position_status
            values.extend([state, position_status, volume_initial, volume_current])

            # Adjust the insert_query to include the new fields and placeholders
            insert_query = f"""
            INSERT INTO trade_orders ({', '.join(fields + ['time_setup', 'time_done', 'type', 'state', 'position_status', 'volume_initial', 'volume_current'])})
            VALUES ({', '.join(['%s'] * len(values))})
            ON CONFLICT (ticket) DO UPDATE SET
            {', '.join([f"{field} = EXCLUDED.{field}" for field in fields[1:] + ['time_setup', 'time_done', 'type', 'state', 'position_status', 'volume_initial', 'volume_current']])}
            """

            try:
                cur.execute(insert_query, values)
            except Exception as e:
                print(f"Failed to insert/update position {position.get('ticket')}: {e}")
                continue  # Skip to the next position if an error occurs

        conn.commit()  # Commit the transaction



def update_position_in_db(position, position_status):
    fields = [
        'ticket', 'symbol', 'price_open', 'price_current',
        'sl', 'tp', 'swap',
        'profit', 'reason', 'magic', 'comment', 'external_id',
        'volume_initial', 'volume_current', 'type', 'state'
    ]
    # Assuming the 'order' field maps to 'external_id' in the DB, and 'price' to 'price_open'
    values = {
        'ticket': position.get('ticket'),
        'symbol': position.get('symbol'),
        'price_open': position.get('price'),
        'price_current': position.get('price'),  # Assuming price_current is the same as price_open for closed positions
        'sl': position.get('sl'),
        'tp': position.get('tp'),
        'swap': position.get('swap'),
        'profit': position.get('profit'),
        'reason': position.get('reason'),
        'magic': position.get('magic'),
        'comment': position.get('comment'),
        'external_id': position.get('order'),  # Assuming this is the mapping
        'volume_initial': position.get('volume'),
        'volume_current': 0,  # Assuming volume_current is 0 for closed positions
        'type': position.get('type'),
        'state': 0,  # You might need to adjust this based on your application logic
        'time_setup': datetime.datetime.fromtimestamp(position.get('time')),
        'time_done': datetime.datetime.fromtimestamp(position.get('time')),  # Assuming time_done is the same as time for closed positions
    }

    # Convert values list for SQL query execution
    query_values = [values[field] for field in fields] + [position_status]

    # Adjust the SQL query to include new fields and placeholders
    insert_query = f"""
    INSERT INTO trade_orders ({', '.join(fields + ['position_status'])})
    VALUES ({', '.join(['%s'] * len(query_values))})
    ON CONFLICT (ticket) DO UPDATE SET
    {', '.join([f"{field} = EXCLUDED.{field}" for field in fields])}, position_status = EXCLUDED.position_status
    """

    try:
        with conn.cursor() as cur:
            cur.execute(insert_query, query_values)
            conn.commit()  # Commit the transaction
    except Exception as e:
        print(f"Failed to insert/update position {position.get('ticket')}: {e}")
def update_closed_position_fields(ticket, fee, commission, profit, swap):
    """
    Updates specific fields for a closed position in the trade_orders table.

    Parameters:
    - ticket: The unique identifier for the trade order.
    - fee: The fee associated with the trade order.
    - commission: The commission for the trade order.
    - profit: The profit (or loss) of the trade order.
    - swap: The swap fee for the trade order.
    """
    update_query = """
    UPDATE trade_orders
    SET 
        fee = %s, 
        commission = %s, 
        profit = %s, 
        swap = %s, 
        position_status = 'closed'
    WHERE ticket = %s;
    """

    try:
        with conn.cursor() as cur:
            cur.execute(update_query, (fee, commission, profit, swap, ticket))
            conn.commit()
    except Exception as e:
        conn.rollback()  # Rollback in case of any error
        print(f"Failed to update closed position {ticket}: {e}")

@sio.event
def connect():
    print("I'm connected!")
    sio.emit('setLastDeal', '2023-01-01 00:00:00')  # Example event

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.event
def my_response(data):
    print('Received response: ', data)

@sio.event
def mt5_account_info(data):
    print('Received MT5 account info: ', data)
    handle_mt5_account_info(data)


@sio.event
def closed_position_data(data):
    print('Received closed position data: ', data)
    if 'data' in data:
        position_data = data['data']
        try:
            # Extract necessary fields from position_data
            ticket = position_data.get('order')
            fee = position_data.get('fee', 0)  # Default to 0 if not provided
            commission = position_data.get('commission', 0)  # Default to 0 if not provided
            profit = position_data.get('profit', 0)  # Default to 0 if not provided
            swap = position_data.get('swap', 0)  # Default to 0 if not provided
            
            # Call the function to update the database for the closed position
            update_closed_position_fields(ticket, fee, commission, profit, swap)
        except Exception as e:
            print(f"Error updating closed position: {e}")
    else:
        print("No data found in the closed position data event.")


if __name__ == '__main__':
    try:
        #to do account management
        sio.connect('http://172.16.14.144:5000')  # Update with your Flask-SocketIO app's address
        sio.wait()
    except socketio.exceptions.ConnectionError as e:
        print("Connection failed:", e)
