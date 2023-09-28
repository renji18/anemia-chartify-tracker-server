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
                "Unnamed: 1": "toddlers",
                "Unnamed: 2": "children",
                "Unnamed: 3": "adolescents",
                "Unnamed: 4": "pregnantWomen",
                "Unnamed: 5": "mothers",
                "Unnamed: 6": "indexValue",
                "Unnamed: 7": "rank",
                "INDIA": "name",
            },
            inplace=True,
        )
        json_data = cleaned_df.to_json(orient="records")
        return json_data
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")
