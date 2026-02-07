"""
================================================================================
Investment Recovery Path Calculator
================================================================================
Author      : Breno Farias da Silva
Created     : 2026-02-05
Description :
    This script analyzes CryptoCurrency investment portfolios from Excel files
    and calculates optimal recovery strategies for assets with negative returns.
    It performs proportional allocation of available budget based on current
    losses to minimize overall portfolio loss percentage.

    Key features include:
        - Automatic Excel data loading and preprocessing with data cleaning
        - Proportional loss-based budget allocation across losing assets
        - New loss percentage calculation after hypothetical investment
        - Improvement metrics showing expected recovery in percentage points
        - Comprehensive output table with investment recommendations

Usage:
    1. Edit the configuration constants (INPUT_FILE, SHEET_NAME, AVAILABLE_BUDGET, EXCLUDED_CRYPTOS, EXCLUDE_POSITIVE_CRYPTOCURRENCIES).
    2. Ensure the Excel file exists with the proper format and sheet name.
    3. Execute the script via Makefile or directly:
            $ make run   or   $ python main.py
    4. View results in terminal and verify logs for detailed execution history.

Outputs:
    - Terminal output with investment recovery recommendations table
    - Logs/main.log — detailed execution log with timestamps

TODOs:
    - Implement CLI argument parsing for configuration parameters
    - Add export functionality to save results to CSV or Excel
    - Add visualization of before/after portfolio loss distribution
    - Implement multiple budget scenario comparison
    - Add data validation for Excel file format verification

Dependencies:
    - Python >= 3.7
    - pandas
    - numpy
    - openpyxl (for Excel file reading)
    - colorama
    - pathlib (standard library)

Assumptions & Notes:
    - Excel file must contain columns: Data, Total Spent - R$, Current Amount - R$, Profit - R$, Profit - %
    - Currency values are in Brazilian Real (R$) format with thousands separator
    - Only assets with negative profit (losses) are considered for investment (if EXCLUDE_POSITIVE_CRYPTOCURRENCIES is True)
    - Excluded coins and the SUM row are filtered out automatically
    - Investment is allocated proportionally to the absolute loss values
"""

import atexit  # For playing a sound when the program finishes
import datetime  # For getting the current date and time
import os  # For running a command in the terminal
import platform  # For getting the operating system name
import sys  # For system-specific parameters and functions
import pandas as pd  # For data manipulation and analysis
import numpy as np  # For numerical computations
import re  # For robust numeric string parsing
from colorama import Style  # For coloring the terminal
from Logger import Logger  # For logging output to both terminal and file
from pathlib import Path  # For handling file paths


# Macros:
class BackgroundColors:  # Colors for the terminal
    CYAN = "\033[96m"  # Cyan
    GREEN = "\033[92m"  # Green
    YELLOW = "\033[93m"  # Yellow
    RED = "\033[91m"  # Red
    BOLD = "\033[1m"  # Bold
    UNDERLINE = "\033[4m"  # Underline
    CLEAR_TERMINAL = "\033[H\033[J"  # Clear the terminal


# Execution Constants:
VERBOSE = False  # Set to True to output verbose messages
INPUT_DIR = "./Input"  # Directory where input files are stored
INPUT_FILE = f"{INPUT_DIR}/Invested Money.xlsx"  # Path to the Excel file
OUTPUT_DIR = "./Output"  # Directory where output files will be saved
OUTPUT_FILE = f"{OUTPUT_DIR}/{Path(__file__).stem}_Results.xlsx"  # Path to the output Excel file
SHEET_NAME = "CryptoCurrencies"  # Name of the sheet to read from the Excel file
AVAILABLE_BUDGET = 500.00  # Available budget for investment recovery (R$)
EXCLUDED_CRYPTOS = ["Bitcoin", "Ethereum", "USDC", "USDT", "Ripple"]  # Coins to exclude from recovery calculation
EXCLUDE_POSITIVE_CRYPTOCURRENCIES = True  # Set to True to exclude cryptocurrencies with positive profit from the calculation

# Logger Setup:
logger = Logger(f"./Logs/{Path(__file__).stem}.log", clean=True)  # Create a Logger instance
sys.stdout = logger  # Redirect stdout to the logger
sys.stderr = logger  # Redirect stderr to the logger

# Sound Constants:
SOUND_COMMANDS = {
    "Darwin": "afplay",
    "Linux": "aplay",
    "Windows": "start",
}  # The commands to play a sound for each operating system
SOUND_FILE = "./.assets/Sounds/NotificationSound.wav"  # The path to the sound file

# RUN_FUNCTIONS:
RUN_FUNCTIONS = {
    "Play Sound": True,  # Set to True to play a sound when the program finishes
}

# Functions Definitions:


def verbose_output(true_string="", false_string=""):
    """
    Outputs a message if the VERBOSE constant is set to True.

    :param true_string: The string to be outputted if the VERBOSE constant is set to True.
    :param false_string: The string to be outputted if the VERBOSE constant is set to False.
    :return: None
    """

    if VERBOSE and true_string != "":  # If VERBOSE is True and a true_string was provided
        print(true_string)  # Output the true statement string
    elif false_string != "":  # If a false_string was provided
        print(false_string)  # Output the false statement string


def verify_filepath_exists(filepath):
    """
    Verify if a file or folder exists at the specified path.

    :param filepath: Path to the file or folder
    :return: True if the file or folder exists, False otherwise
    """

    verbose_output(
        f"{BackgroundColors.GREEN}Verifying if the file or folder exists at the path: {BackgroundColors.CYAN}{filepath}{Style.RESET_ALL}"
    )  # Output the verbose message

    return os.path.exists(filepath)  # Return True if the file or folder exists, False otherwise


def compute_totals(final_table, totals_df=None):
    """
    Computes the total current loss and total investment.

    :param final_table: DataFrame already prepared for display (renamed columns)
    :param totals_df: Optional DataFrame with allocation rows to compute totals from
    :return: Tuple (total_current_loss, total_investment)
    """

    if totals_df is not None and not totals_df.empty:  # Prefer totals from allocated assets when available
        total_current_loss = totals_df["Profit - R$"].sum()  # Sum losses from allocated assets
        total_investment = totals_df["Investment"].sum()  # Sum investments from allocated assets
    else:  # Fallback to summing from the final table if totals_df is not provided or empty (handles case with no eligible assets)
        if "Current Loss (R$)" in final_table.columns:  # Check if the expected column exists in the final table
            total_current_loss = final_table["Current Loss (R$)"].sum()  # Sum losses from the final table
        else:  # If the expected column is missing, attempt to sum from the original column name as a fallback
            total_current_loss = final_table.get("Profit - R$", pd.Series(dtype=float)).sum()  # Sum losses from the original column if the renamed column is missing, using get to avoid KeyError and defaulting to an empty Series of floats

        if "Investment" in final_table.columns:  # Check if the expected column exists in the final table
            total_investment = final_table["Investment"].sum()  # Sum investments from the final table
        else:  # If the expected column is missing, attempt to sum from the original column name as a fallback
            total_investment = final_table.get("Investment", pd.Series(dtype=float)).sum()  # Sum investments from the original column if the renamed column is missing, using get to avoid KeyError and defaulting to an empty Series of floats

    return total_current_loss, total_investment  # Return the computed totals as a tuple


def build_total_row(total_current_loss, total_investment):
    """
    Builds a single-row DataFrame representing the totals row.

    :param total_current_loss: Sum of current losses
    :param total_investment: Sum of allocated investments
    :return: Single-row DataFrame suitable for concatenation
    """

    return pd.DataFrame(
        {
            "CryptoCurrency": ["TOTAL"],
            "Current Loss (R$)": [total_current_loss],
            "Investment": [total_investment],
            "Old % Loss": [np.nan],
            "New % Loss": [np.nan],
            "Improvement %": [np.nan],
        }  # Create a DataFrame with the totals row, using NaN for percentage columns since they don't have meaningful totals
    )
    


def append_total_row(final_table, total_row):
    """
    Appends the totals row to the final table and returns a new DataFrame.

    :param final_table: DataFrame with presentation columns
    :param total_row: Single-row DataFrame containing totals
    :return: Concatenated DataFrame including totals row
    """

    return pd.concat([final_table, total_row], ignore_index=True)  # Concatenate the final table with the totals row, resetting the index to maintain a clean sequential index


def prepare_final_table(display_df, totals_df=None):
    """
    Prepares the final formatted table for display with totals row.

    This function accepts a DataFrame containing all cryptocurrencies to be
    displayed (including those that won't receive any investment). The
    optional `totals_df` parameter is used to compute the summary totals
    (current losses and total investment) based only on the assets that
    actually received allocations.

    :param display_df: DataFrame with rows to display (must contain columns: "Data", "Profit - R$", "Profit - %", "Investment", "New % Loss", "Improvement %")
    :param totals_df: DataFrame used to compute totals (typically only allocated assets)
    :return: Formatted DataFrame ready for display with proper column names and totals
    """

    verbose_output(  # Output verbose preparation start message
        f"{BackgroundColors.GREEN}Preparing final output table...{Style.RESET_ALL}"
    )

    final_table = select_and_rename_display_columns(display_df)  # Select and rename columns for display
    total_current_loss, total_investment = compute_totals(final_table, totals_df)  # Compute totals for current loss and investment
    total_row = build_total_row(total_current_loss, total_investment)  # Build the totals row as a single-row DataFrame
    final_table = append_total_row(final_table, total_row)  # Append the totals row to the final table

    verbose_output(  # Output verbose completion message
        f"{BackgroundColors.GREEN}Final table prepared with {BackgroundColors.CYAN}{len(final_table) - 1}{BackgroundColors.GREEN} investments and totals row{Style.RESET_ALL}"
    )

    return final_table  # Return the formatted final table


def prepare_empty_allocation_result(display_df):
    """
    Prepares allocation result when no eligible assets are found for investment.

    :param display_df: DataFrame with all assets to display
    :return: DataFrame with zero allocations for all assets
    """

    combined_df = display_df[["Data", "Profit - R$", "Profit - %"]].copy()  # Prepare display with basic columns
    combined_df["Investment"] = 0.0  # Set zero investment for all assets
    combined_df["New % Loss"] = combined_df["Profit - %"].copy()  # Copy old loss as new loss (no change)
    combined_df["Improvement %"] = 0.0  # Set zero improvement for all assets
    combined_df = combined_df.sort_values(by="Profit - R$", ascending=False).reset_index(drop=True)  # Sort by loss descending

    return combined_df  # Return the prepared DataFrame


def merge_and_fill_allocation_data(display_df, target_df):
    """
    Merges allocation data with display DataFrame and fills missing values.

    :param display_df: DataFrame with all assets to display
    :param target_df: DataFrame with allocation data for eligible assets
    :return: Combined DataFrame with allocations merged and missing values filled
    """

    alloc = target_df.set_index("Data")[["Investment", "New % Loss", "Improvement %"]]  # Extract allocation columns from target DataFrame
    combined_df = (  # Merge allocations into display DataFrame using left join
        display_df.set_index("Data")[["Profit - R$", "Profit - %"]]  # Select profit columns from display DataFrame
        .join(alloc, how="left")  # Left join with allocations (keeps all display rows)
        .reset_index()  # Reset index to restore Data column
    )

    combined_df["Investment"] = combined_df["Investment"].fillna(0.0)  # Fill missing investments with zero (assets that received no allocation)
    combined_df["New % Loss"] = combined_df["New % Loss"].fillna(combined_df["Profit - %"])  # Fill missing new loss with old loss (no change for unallocated assets)
    combined_df["Improvement %"] = combined_df["Improvement %"].fillna(0.0)  # Fill missing improvement with zero (no improvement for unallocated assets)

    combined_df = combined_df.sort_values(by="Profit - R$", ascending=True).reset_index(drop=True)  # Sort by loss ascending (worst losses first)

    return combined_df  # Return the merged and filled DataFrame


def calculate_investment_recovery(INPUT_FILE, sheet_name, budget, excluded_cryptos, exclude_positive_cryptos=True):
    """
    Calculates the optimal investment recovery strategy based on the provided Excel data and parameters.

    :param INPUT_FILE: Path to the Excel file containing investment data
    :param sheet_name: Name of the sheet to read from the Excel file
    :param budget: Available budget for investment recovery (R$)
    :param excluded_cryptos: List of CryptoCurrency names to exclude from calculation
    :param exclude_positive_cryptos: If True, exclude cryptocurrencies with positive profit
    :return: Formatted pandas DataFrame with investment recommendations, or error message string
    """

    try:  # Wrap in error handling
        df = load_and_clean_excel_data(INPUT_FILE, sheet_name)  # Load and clean Excel data

        display_df = df[(df["Data"] != "SUM")].copy()  # Create display DataFrame excluding SUM row

        target_df = filter_target_investments(display_df, excluded_cryptos, exclude_positive_cryptos)  # Filter for eligible assets

        if len(target_df) == 0:  # If no eligible assets found
            combined_df = prepare_empty_allocation_result(display_df)  # Prepare result with zero allocations
            final_table = prepare_final_table(combined_df, totals_df=None)  # Prepare table for display
            return final_table  # Return the empty allocation result

        target_df = calculate_proportional_allocation(target_df, budget)  # Calculate allocations for eligible assets

        combined_df = merge_and_fill_allocation_data(display_df, target_df)  # Merge allocations and fill missing values

        final_table = prepare_final_table(combined_df, totals_df=target_df)  # Prepare final table for display

        return final_table  # Return results table

    except FileNotFoundError:  # Handle file not found
        return f"{BackgroundColors.RED}Error: File '{INPUT_FILE}' not found. Please verify the file path.{Style.RESET_ALL}"
    except ValueError as e:  # Handle value errors
        return f"{BackgroundColors.RED}Error: Invalid sheet name or data format. {str(e)}{Style.RESET_ALL}"
    except Exception as e:  # Handle other exceptions
        return f"{BackgroundColors.RED}Error processing the file: {str(e)}{Style.RESET_ALL}"


def format_percentage_values(val):
    """
    Formats a value for display in the table, handling NaN and numeric formatting.
    
    :param val: The value to format
    :return: A string representation of the value, formatted for display
    """
    
    if pd.isna(val):  # If the value is NaN, return an empty string for cleaner display
        return ""  # Return empty string for NaN values to keep the table clean
    
    if isinstance(val, (int, float, np.floating, np.integer)):  # If the value is numeric, format it with commas and 2 decimal places
        return f"{val:,.2f}"  # Format numeric values with commas and 2 decimal places for better readability

    return str(val)  # For non-numeric values, return the string representation as-is (e.g., cryptocurrency names)
        


def pad(s, w):
    """
    Pads the string `s` with spaces on the right to ensure it has a total width of `w`.

    :param s: The string to pad
    :param w: The total width to pad to
    """
    
    return str(s) + " " * (w - len(str(s)))  # Convert to string and pad with spaces to the right to ensure consistent column width in the table display
    


def prepare_table_rows(df):
    """
    Prepares formatted row data from DataFrame for table display.

    :param df: DataFrame containing result data
    :return: List of formatted row values
    """

    rows = []  # List to hold formatted row data
    for i, row in df.iterrows():  # Iterate through DataFrame rows
        name = "" if str(row.get("CryptoCurrency", "")).upper() == "TOTAL" else str(row.get("CryptoCurrency", ""))  # Get cryptocurrency name, but use empty string for TOTAL row
        idx = "" if name == "" else str(len(rows) + 1)  # Use index number for non-TOTAL rows, but leave blank for TOTAL row

        row_vals = [  # Format each cell value appropriately for display
            idx,  # Row index number
            name if name != "" else "TOTAL",  # Cryptocurrency name or TOTAL label
            format_percentage_values(row.get("Current Loss (R$)", "")),  # Current loss formatted
            format_percentage_values(row.get("Investment", "")),  # Investment amount formatted
            format_percentage_values(row.get("Old % Loss", "")),  # Old percentage loss formatted
            format_percentage_values(row.get("New % Loss", "")),  # New percentage loss formatted
            format_percentage_values(row.get("Improvement %", "")),  # Improvement percentage formatted
        ]  # Format each cell value appropriately for display, handling NaN and numeric formatting
        rows.append(row_vals)  # Append the formatted row values to the list of rows

    return rows  # Return the list of formatted rows


def format_cell_with_color(val, col_width, col_index):
    """
    Formats a single cell with appropriate color based on column index.

    :param val: Value to format and display in the cell
    :param col_width: Width to pad the cell to for alignment
    :param col_index: Column index to determine color scheme
    :return: Formatted cell string with color codes
    """

    cell = pad(val, col_width)  # Pad the cell value to the appropriate width for alignment
    if col_index in (0, 1):  # Index and name columns use green background
        return f"{BackgroundColors.GREEN}{cell}{Style.RESET_ALL}"  # Apply green background to index and name cells
    elif col_index in (2, 4, 5):  # Current Loss, Old % Loss and New % Loss columns use red background
        return f"{BackgroundColors.RED}{cell}{Style.RESET_ALL}"  # Apply red background to loss-related cells
    elif col_index in (3, 6):  # Investment and Improvement columns use cyan background
        return f"{BackgroundColors.CYAN}{cell}{Style.RESET_ALL}"  # Apply cyan background to investment and improvement cells
    else:  # Default formatting for any other columns (future expansion)
        return cell  # Use default formatting for any other cells (currently none, but allows for future expansion)


def format_header_row(headers, col_widths):
    """
    Formats the header row with appropriate colors for each column.

    :param headers: List of header strings
    :param col_widths: List of column widths for alignment
    :return: Formatted header row string
    """

    header_cells = []  # List to hold formatted header cells with colors
    for j, h in enumerate(headers):  # Iterate through headers to format them with colors based on their column index
        header_cells.append(format_cell_with_color(h, col_widths[j], j))  # Format each header cell with color
    return "  ".join(header_cells)  # Join the formatted header cells with spacing and return as single string


def format_data_rows(rows, col_widths):
    """
    Formats all data rows with appropriate colors for each column.

    :param rows: List of row data (each row is a list of values)
    :param col_widths: List of column widths for alignment
    :return: List of formatted row strings
    """

    lines = []  # List to hold formatted row strings
    for r in rows:  # Iterate through each data row to format the cells with colors based on their column index
        cells = []  # List to hold formatted cells for the current row
        for j, val in enumerate(r):  # Iterate through each cell in the row to format it with colors based on its column index
            cells.append(format_cell_with_color(val, col_widths[j], j))  # Format each cell with color
        lines.append("  ".join(cells))  # Join the formatted cells with spacing and add to the lines list
    return lines  # Return the list of formatted row strings


def format_table_output(result_table):
    """
    Formats the result table for terminal display with proper number formatting.

    :param result_table: The pandas DataFrame to format
    :return: Formatted string representation of the table
    """

    if isinstance(result_table, str):  # If result is an error message string
        return result_table  # Return the error message as-is

    df = result_table.copy()  # Work with a copy to avoid modifying the original DataFrame

    headers = ["#", "Cryptocurrency", "Current Loss (R$)", "Investment", "Old % Loss", "New % Loss", "Improvement %"]  # Define headers for display

    rows = prepare_table_rows(df)  # Prepare formatted row data

    cols = list(zip(*([headers] + rows))) if rows else [headers]  # Transpose rows to columns for width calculation, but handle case with no data rows
    col_widths = [max(len(str(x)) for x in col) for col in cols]  # Calculate maximum width for each column based on headers and data for proper alignment

    lines = []  # List to hold each line of the formatted table output
    lines.append(format_header_row(headers, col_widths))  # Format and add the header row
    lines.extend(format_data_rows(rows, col_widths))  # Format and add all data rows

    return "\n".join(lines)  # Join all lines with newlines to create the final formatted table string for display in the terminal


def save_table_to_excel(dataframe, output_filepath):
    """
    Saves a pandas DataFrame to an Excel file at the specified path.

    :param dataframe: The pandas DataFrame to save
    :param output_filepath: Full path where the Excel file will be saved
    :return: True if save was successful, False otherwise
    """

    verbose_output(
        f"{BackgroundColors.GREEN}Preparing to save results to: {BackgroundColors.CYAN}{output_filepath}{Style.RESET_ALL}"
    )  # Output the verbose message

    output_dir = os.path.dirname(output_filepath)  # Extract the directory path from the full file path

    if not verify_filepath_exists(output_dir):  # Check if the output directory exists
        verbose_output(
            f"{BackgroundColors.YELLOW}Output directory does not exist. Creating: {BackgroundColors.CYAN}{output_dir}{Style.RESET_ALL}"
        )  # Output the verbose message
        os.makedirs(output_dir, exist_ok=True)  # Create the output directory and any necessary parent directories

    try:  # Attempt to save the DataFrame to Excel
        dataframe.to_excel(output_filepath, index=False, engine="openpyxl")  # Save DataFrame to Excel without row indices
        verbose_output(
            f"{BackgroundColors.GREEN}Successfully saved results to: {BackgroundColors.CYAN}{output_filepath}{Style.RESET_ALL}"
        )  # Output success message
        return True  # Return True to indicate successful save
    except Exception as e:  # Handle any errors during file save
        print(
            f"{BackgroundColors.RED}Error saving file: {str(e)}{Style.RESET_ALL}"
        )  # Output error message
        return False  # Return False to indicate save failure


def to_seconds(obj):
    """
    Converts various time-like objects to seconds.
    
    :param obj: The object to convert (can be int, float, timedelta, datetime, etc.)
    :return: The equivalent time in seconds as a float, or None if conversion fails
    """
    
    if obj is None:  # None can't be converted
        return None  # Signal failure to convert
    if isinstance(obj, (int, float)):  # Already numeric (seconds or timestamp)
        return float(obj)  # Return as float seconds
    if hasattr(obj, "total_seconds"):  # Timedelta-like objects
        try:  # Attempt to call total_seconds()
            return float(obj.total_seconds())  # Use the total_seconds() method
        except Exception:
            pass  # Fallthrough on error
    if hasattr(obj, "timestamp"):  # Datetime-like objects
        try:  # Attempt to call timestamp()
            return float(obj.timestamp())  # Use timestamp() to get seconds since epoch
        except Exception:
            pass  # Fallthrough on error
    return None  # Couldn't convert


def calculate_execution_time(start_time, finish_time=None):
    """
    Calculates the execution time and returns a human-readable string.

    Accepts either:
    - Two datetimes/timedeltas: `calculate_execution_time(start, finish)`
    - A single timedelta or numeric seconds: `calculate_execution_time(delta)`
    - Two numeric timestamps (seconds): `calculate_execution_time(start_s, finish_s)`

    Returns a string like "1h 2m 3s".
    """

    if finish_time is None:  # Single-argument mode: start_time already represents duration or seconds
        total_seconds = to_seconds(start_time)  # Try to convert provided value to seconds
        if total_seconds is None:  # Conversion failed
            try:  # Attempt numeric coercion
                total_seconds = float(start_time)  # Attempt numeric coercion
            except Exception:
                total_seconds = 0.0  # Fallback to zero
    else:  # Two-argument mode: Compute difference finish_time - start_time
        st = to_seconds(start_time)  # Convert start to seconds if possible
        ft = to_seconds(finish_time)  # Convert finish to seconds if possible
        if st is not None and ft is not None:  # Both converted successfully
            total_seconds = ft - st  # Direct numeric subtraction
        else:  # Fallback to other methods
            try:  # Attempt to subtract (works for datetimes/timedeltas)
                delta = finish_time - start_time  # Try subtracting (works for datetimes/timedeltas)
                total_seconds = float(delta.total_seconds())  # Get seconds from the resulting timedelta
            except Exception:  # Subtraction failed
                try:  # Final attempt: Numeric coercion
                    total_seconds = float(finish_time) - float(start_time)  # Final numeric coercion attempt
                except Exception:  # Numeric coercion failed
                    total_seconds = 0.0  # Fallback to zero on failure

    if total_seconds is None:  # Ensure a numeric value
        total_seconds = 0.0  # Default to zero
    if total_seconds < 0:  # Normalize negative durations
        total_seconds = abs(total_seconds)  # Use absolute value

    days = int(total_seconds // 86400)  # Compute full days
    hours = int((total_seconds % 86400) // 3600)  # Compute remaining hours
    minutes = int((total_seconds % 3600) // 60)  # Compute remaining minutes
    seconds = int(total_seconds % 60)  # Compute remaining seconds

    if days > 0:  # Include days when present
        return f"{days}d {hours}h {minutes}m {seconds}s"  # Return formatted days+hours+minutes+seconds
    if hours > 0:  # Include hours when present
        return f"{hours}h {minutes}m {seconds}s"  # Return formatted hours+minutes+seconds
    if minutes > 0:  # Include minutes when present
        return f"{minutes}m {seconds}s"  # Return formatted minutes+seconds
    return f"{seconds}s"  # Fallback: only seconds


def play_sound():
    """
    Plays a sound when the program finishes and skips if the operating system is Windows.

    :param: None
    :return: None
    """

    current_os = platform.system()  # Get the current operating system
    if current_os == "Windows":  # If the current operating system is Windows
        return  # Do nothing

    if verify_filepath_exists(SOUND_FILE):  # If the sound file exists
        if current_os in SOUND_COMMANDS:  # If the platform.system() is in the SOUND_COMMANDS dictionary
            os.system(f"{SOUND_COMMANDS[current_os]} {SOUND_FILE}")  # Play the sound
        else:  # If the platform.system() is not in the SOUND_COMMANDS dictionary
            print(
                f"{BackgroundColors.RED}The {BackgroundColors.CYAN}{current_os}{BackgroundColors.RED} is not in the {BackgroundColors.CYAN}SOUND_COMMANDS dictionary{BackgroundColors.RED}. Please add it!{Style.RESET_ALL}"
            )
    else:  # If the sound file does not exist
        print(
            f"{BackgroundColors.RED}Sound file {BackgroundColors.CYAN}{SOUND_FILE}{BackgroundColors.RED} not found. Make sure the file exists.{Style.RESET_ALL}"
        )


def main():
    """
    Main function.

    :param: None
    :return: None
    """

    print(
        f"{BackgroundColors.CLEAR_TERMINAL}{BackgroundColors.BOLD}{BackgroundColors.GREEN}Welcome to the {BackgroundColors.CYAN}Investment Recovery Path Calculator{BackgroundColors.GREEN} program!{Style.RESET_ALL}",
        end="\n",
    )  # Output the welcome message
    start_time = datetime.datetime.now()  # Get the start time of the program

    file_to_process = discover_input_file(INPUT_FILE, INPUT_DIR)  # Discover and resolve the input file to process

    if file_to_process is None:  # If file discovery failed or was cancelled
        return  # Exit the program

    result_table = calculate_investment_recovery(
        file_to_process, SHEET_NAME, AVAILABLE_BUDGET, EXCLUDED_CRYPTOS, EXCLUDE_POSITIVE_CRYPTOCURRENCIES
    )  # Calculate investment recovery

    print(
        f"{BackgroundColors.BOLD}{BackgroundColors.GREEN}Investment Recovery Recommendations:{Style.RESET_ALL}",
        end="\n",
    )  # Output results header
    print(format_table_output(result_table))  # Display the formatted result table

    save_table_to_excel(result_table, OUTPUT_FILE)  # Save the results table to Excel file

    finish_time = datetime.datetime.now()  # Get the finish time of the program
    print(
        f"{BackgroundColors.GREEN}Start time: {BackgroundColors.CYAN}{start_time.strftime('%d/%m/%Y - %H:%M:%S')}\n{BackgroundColors.GREEN}Finish time: {BackgroundColors.CYAN}{finish_time.strftime('%d/%m/%Y - %H:%M:%S')}\n{BackgroundColors.GREEN}Execution time: {BackgroundColors.CYAN}{calculate_execution_time(start_time, finish_time)}{Style.RESET_ALL}"
    )  # Output the start and finish times
    print(
        f"{BackgroundColors.BOLD}{BackgroundColors.GREEN}Program finished.{Style.RESET_ALL}"
    )  # Output the end of the program message
    (
        atexit.register(play_sound) if RUN_FUNCTIONS["Play Sound"] else None
    )  # Register the play_sound function to be called when the program finishes


if __name__ == "__main__":
    """
    This is the standard boilerplate that calls the main() function.

    :return: None
    """

    main()  # Call the main function
