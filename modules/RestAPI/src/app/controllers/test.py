import pandas_market_calendars as mcal

# Create a calendar
nyse = mcal.get_calendar('24/5')

# Show available calendars
# print(mcal.get_calendar_names())
early = nyse.schedule(start_date='2024-01-01', end_date='2024-02-01')
print(early)