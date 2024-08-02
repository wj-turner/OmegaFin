import socketio
import psycopg2
import datetime
import os
# Database connection parameters

open_positions = set()
# Establishing the connection
conn = psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host="postgres",
            database=os.getenv("POSTGRES_CONFIG_DB_name")
                                      )


def fetch_open_positions_from_db():
    """Fetch open positions from the database and return a set of tickets."""
    open_positions = set()
    with conn.cursor() as cur:
        try:
            cur.execute("SELECT ticket FROM positions")
            for record in cur.fetchall():
                open_positions.add(record[0])  # Assuming ticket is the first column
        except Exception as e:
            print(f"Failed to fetch open positions from database: {e}")
    return open_positions

def update_profile(profile_data):
    """Updates or inserts a profile into the database based on login."""
    fields = [
        'login', 'trade_mode', 'leverage', 'limit_orders', 'margin_so_mode', 
        'trade_allowed', 'trade_expert', 'margin_mode', 'currency_digits', 'fifo_close', 
        'balance', 'credit', 'profit', 'equity', 'margin', 'margin_free', 'margin_level', 
        'margin_so_call', 'margin_so_so', 'margin_initial', 'margin_maintenance', 
        'assets', 'liabilities', 'commission_blocked', 'name', 'server', 'currency', 'company'
    ]
    values = [profile_data.get(field) for field in fields]
    placeholders = ", ".join(["%s"] * len(fields))
    updates = ", ".join([f"{field} = EXCLUDED.{field}" for field in fields if field != 'login'])
    
    query = f"""
    INSERT INTO user_profiles ({", ".join(fields)})
    VALUES ({placeholders})
    ON CONFLICT (login) DO UPDATE SET
    {updates}
    """
    
    with conn.cursor() as cur:
        try:
            cur.execute(query, values)
            conn.commit()
        except Exception as e:
            print(f"Failed to save profile into database: {e}")

def fetch_open_orders_from_db():
    """Fetch open orders from the database and return a set of tickets."""
    open_positions = set()
    with conn.cursor() as cur:
        try:
            cur.execute("SELECT ticket FROM orders")
            for record in cur.fetchall():
                open_positions.add(record[0])  # Assuming ticket is the first column
        except Exception as e:
            print(f"Failed to fetch open orders from database: {e}")
    return open_positions


# Create a Socket.IO client
sio = socketio.Client()
def handle_mt5_account_info(data):
    positions = data.get('data', {}).get('positions', [])
    positions_tickets = {position.get('ticket') for position in positions}
    orders = data.get('data', {}).get('orders', [])
    orders_tickets = {order.get('ticket') for order in orders}
    deals = data.get('data', {}).get('deals', [])
    profiles = data.get('data', {}).get('profile', [])

    
    with conn.cursor() as cur:
        positions_to_delete = fetch_open_positions_from_db() - positions_tickets
        if positions_to_delete:
            delete_query = "DELETE FROM positions WHERE ticket IN %s"
            try:
                # psycopg2 requires a list of tuples for the IN clause, convert set to list of tuples
                cur.execute(delete_query, (tuple(positions_to_delete),))
                conn.commit()
            except Exception as e:
                print(f"Failed to delete old positions: {e}")
                # Optionally, handle rollback if needed
                conn.rollback()
        else:
            print("No old positions to delete.")

        for position in positions:
        # Map received fields to your new schema
            fields = [
                'ticket', 'time', 'time_msc', 'time_update', 'time_update_msc', 'type', 
                'magic', 'identifier', 'reason', 'volume', 'price_open', 'sl', 'tp', 
                'price_current', 'swap', 'profit', 'symbol', 'comment', 'external_id'
            ]
            values = [position.get(field) for field in fields]
            
            # Construct the insert or update query
            insert_query = f"""
            INSERT INTO positions ({', '.join(fields)})
            VALUES ({', '.join(['%s'] * len(values))})
            ON CONFLICT (ticket) DO UPDATE SET
            {', '.join([f"{field} = EXCLUDED.{field}" for field in fields[1:]])}
            """
                
            try:
                cur.execute(insert_query, values)
            except Exception as e:
                print(f"Failed to insert/update position {position.get('ticket')}: {e}")
                continue  # Skip to the next position if an error occurs

        conn.commit()  # Commit the transaction
        orders_to_delete = fetch_open_orders_from_db() - orders_tickets
        if orders_to_delete:
            delete_query = "DELETE FROM orders WHERE ticket IN %s"
            try:
                # psycopg2 requires a list of tuples for the IN clause, convert set to list of tuples
                cur.execute(delete_query, (tuple(orders_to_delete),))
                conn.commit()
            except Exception as e:
                print(f"Failed to delete old orders: {e}")
                # Optionally, handle rollback if needed
                conn.rollback()
        else:
            print("No old order to delete.")
        # Check if the profile with this login already exists
        update_profile(profiles)


        for order in orders:
        # Map received fields to your database schema for the 'orders' table
            fields = [
                'ticket', 'time_setup', 'time_setup_msc', 'time_done', 'time_done_msc',
                'time_expiration', 'type', 'type_time', 'type_filling', 'state', 'magic',
                'position_id', 'position_by_id', 'reason', 'volume_initial', 'volume_current',
                'price_open', 'sl', 'tp', 'price_current', 'price_stoplimit', 'symbol',
                'comment', 'external_id'
            ]
            values = [order.get(field) for field in fields]
            
            # Construct the insert or update query for 'orders'
            insert_query = f"""
            INSERT INTO orders ({', '.join(fields)})
            VALUES ({', '.join(['%s'] * len(values))})
            ON CONFLICT (ticket) DO UPDATE SET
            {', '.join([f"{field} = EXCLUDED.{field}" for field in fields[1:]])}
            """

            try:
                cur.execute(insert_query, values)
            except Exception as e:
                print(f"Failed to insert/update order {order.get('ticket')}: {e}")
                continue  # Skip to the next order if an error occurs
        conn.commit()  # Commit the transaction

        for deal in deals:
        # Map received fields to your database schema for the 'deals' table
            fields = [
                'ticket', '"order"', 'time', 'time_msc', 'type', 'entry', 'magic',
                'position_id', 'reason', 'volume', 'price', 'commission', 'swap',
                'profit', 'fee', 'symbol', 'comment', 'external_id'
            ]
            values = [
                deal.get('ticket'), deal.get('order'), deal.get('time'), deal.get('time_msc'), deal.get('type'),
                deal.get('entry'), deal.get('magic'), deal.get('position_id'), deal.get('reason'),
                deal.get('volume'), deal.get('price'), deal.get('commission'), deal.get('swap'),
                deal.get('profit'), deal.get('fee'), deal.get('symbol'), deal.get('comment'), deal.get('external_id')
            ]
            
            placeholders = ', '.join(['%s'] * len(values))
            fields_str = ', '.join(fields)
            update_str = ', '.join([f"{field} = EXCLUDED.{field}" for field in fields if field != '"order"'])

            insert_query = f"""
            INSERT INTO deals ({fields_str})
            VALUES ({placeholders})
            ON CONFLICT (ticket) DO UPDATE SET
            {update_str}
            """
            try:
                cur.execute(insert_query, values)
            except Exception as e:
                print(f"Failed to insert/update deal {deal.get('ticket')}: {e}")
                continue  # Skip to the next deal if an error occurs
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
