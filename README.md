# Parser Application

This application is a parser that supports both partial parsing for testing purposes and full parsing.

## Configuration

You can configure the application using environment variables:

- `TEST_MODE`: Set to `True` for partial parsing mode (default is `False`).
- `PROXY`: Specify the proxy server URL and port if needed.
- `SLEEP_PAUSE`: Set the delay in seconds between requests (default is `1`).
- `FILENAME`: The name of the file used to store the parsing results (default is `test`).

### Locally

1. Make sure you have Python installed.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the parser using `python main_calendar.py`.

