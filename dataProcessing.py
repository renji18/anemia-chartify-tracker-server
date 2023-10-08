import io
import pandas as pd


def process_csv_to_json(csv_file, type):
    """
    This function processes a CSV file, extracts specific data from it, and converts it into a JSON format. It also handles different data processing based on the provided type parameter.


    The function takes a CSV file object csv_file and a type parameter (either "quarterly" or "monthly").

    It reads the CSV file, cleans the data by selecting specific rows (14:48 for "quarterly" and 13:47 for "monthly"), and renames columns for consistency.

    The cleaned data is then converted to a JSON format using the Pandas library's to_json method.

    Any errors during this process are caught and re-raised with an informative error message.
    """
    try:
        file_bytes = csv_file.read()
        file_stream = io.BytesIO(file_bytes)
        df = pd.read_csv(file_stream)
        if type == "quarterly":
            cleaned_df = df[14:48].copy()
        elif type == "monthly":
            cleaned_df = df[13:47].copy()
        else:
            raise ValueError("Invalid type passed")
        cleaned_df.rename(
            columns={
                "Unnamed: 1": "Children (6 - 59 months)",
                "Unnamed: 2": "Children (6 - 9 years)",
                "Unnamed: 3": "Adolescents (10 - 19 years)",
                "Unnamed: 4": "Pregnant Women",
                "Unnamed: 5": "Mothers",
                "Unnamed: 6": "Index Value",
                "Unnamed: 7": "Rank",
                "INDIA": "District",
            },
            inplace=True,
        )
        json_data = cleaned_df.to_json(orient="records")
        return json_data
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")
