import io
import pandas as pd


def process_csv_to_json(csv_file):
    """
    This function processes a CSV file, extracts specific data from it, and converts it into a JSON format.
    It also handles different data processing based on the provided type parameter.

    Parameters:
    - csv_file: File-like object
        The CSV file object to be processed.

    Returns:
    - str: JSON representation of the processed data.

    The function reads the CSV file using the Pandas library and renames specific columns for clarity.

    Renamed Columns:
    - "HMIS: 9.9- Percentage of children (6-59 months)" to "Children (6 - 59 months)"
    - "HMIS: 23.1 & 23.3- Percentage of Children (6-9 yrs)" to "Children (6 - 9 years)"
    - "HMIS: 22.1.1 & 22.1.3- Percentage of adolescents (10-19 years)" to "Adolescents (10 - 19 years)"
    - "HMIS: 1.2.4- Percentage of Pregnant Women" to "Pregnant Women"
    - "HMIS: 6.3- Percentage of mothers" to "Mothers"
    - "Index Value (%)" to "Index Value"
    - "District Rank" to "Rank"
    - "Location" to "District"

    The processed data is then converted to a JSON format using the Pandas library's to_json method
    with the orientation set to "records".

    Any errors during this process are caught, and an informative error message is raised.
    """
    try:
        # Read CSV file into a Pandas DataFrame
        file_bytes = csv_file.read()
        file_stream = io.BytesIO(file_bytes)
        df = pd.read_csv(file_stream)

        # Rename columns for clarity
        df.rename(
            columns={
                "HMIS: 9.9- Percentage of children (6-59 months)": "Children (6 - 59 months)",
                "HMIS: 23.1 & 23.3- Percentage of Children (6-9 yrs)": "Children (6 - 9 years)",
                "HMIS: 22.1.1 & 22.1.3- Percentage of adolescents (10-19 years)": "Adolescents (10 - 19 years)",
                "HMIS: 1.2.4- Percentage of Pregnant Women": "Pregnant Women",
                "HMIS: 6.3- Percentage of mothers": "Mothers",
                "Index Value (%)": "Index Value",
                "District Rank": "Rank",
                "Location": "District",
            },
            inplace=True,
        )

        # Convert DataFrame to JSON records
        json_data = df.to_json(orient="records")
        return json_data

    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")
