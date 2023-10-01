import io
import pandas as pd


def process_csv_to_json(csv_file):
    try:
        file_bytes = csv_file.read()
        file_stream = io.BytesIO(file_bytes)
        df = pd.read_csv(file_stream)
        cleaned_df = df[14:48].copy()
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
