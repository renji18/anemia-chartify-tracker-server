import pandas as pd
from flask import make_response
from io import BytesIO

month_names = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def read_database(mongo):
    """
    This function retrieves data from a MongoDB collection based on the provided type parameter (either "quarterly" or "monthly")


    The function determines the appropriate MongoDB collection based on the type parameter and retrieves documents from that collection.

    It handles exceptions and raises a ValueError for an invalid type value.
    """
    try:
        collection = mongo.db.anemiaDataMonthly
        documents = list(collection.find({}, {"_id": 0}))

        output_data = []

        for state_data in documents:
            state_name = state_data["state"]
            districts_data = state_data["data"]

            formatted_state_data = []

            for district_data in districts_data:
                district_name = district_data["District"]
                index_values = district_data["Index Value"]

                formatted_district_data = {"district": district_name, "indexValues": []}

                for index_value in index_values:
                    year = index_value["year"]
                    monthly_data = index_value["data"]

                    formatted_index_value = {"year": year, "singleYearData": []}

                    for i, value in enumerate(monthly_data):
                        month = (
                            month_names[i] if i < len(month_names) else f"Month_{i + 1}"
                        )
                        formatted_monthly_data = {month: value}
                        formatted_index_value["singleYearData"].append(
                            formatted_monthly_data
                        )
                    formatted_district_data["indexValues"].append(
                        formatted_index_value,
                    )
                formatted_state_data.append(formatted_district_data)
            output_data.append(
                {"state": state_name, "districtsData": formatted_state_data}
            )
        return output_data
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")


def modifyToExcel(data):
    try:
        state_dfs = []
        for state_data in data:
            state_name = state_data["state"]
            year_dfs = []

            for district_data in state_data["districtsData"]:
                district_name = district_data["district"]

                for index_value in district_data["indexValues"]:
                    year = index_value["year"]
                    index_value_data = index_value["singleYearData"]

                    df = pd.DataFrame(index_value_data)
                    df["Month"] = df.columns
                    df["Month"] = df["Month"].apply(
                        lambda x: x if x != "singleYearData" else None
                    )
                    df["District"] = district_name
                    df["Index Value"] = (
                        df.drop(columns=["Month", "District"]).sum(axis=1).astype(float)
                    )
                    df["Year"] = year
                    df = df[["Month", "Year", "District", "Index Value"]]

                    year_dfs.append(df)
                empty_row = pd.Series([None] * df.shape[1], index=df.columns)
                year_dfs.append(empty_row)
            for df in year_dfs:
                df["State"] = state_name
            year_dfs = [
                df[["Month", "Year", "State", "District", "Index Value"]]
                for df in year_dfs
            ]
            state_df = pd.concat(year_dfs, ignore_index=True)
            state_dfs.append(state_df)

        final_df = pd.concat(state_dfs, ignore_index=True)
        final_df = final_df.iloc[:, :-1]

        excel_output = BytesIO()
        final_df.to_excel(excel_output, index=False)
        excel_output.seek(0)

        response = make_response(excel_output.read())
        response.headers[
            "Content-Disposition"
        ] = "attachment; filename=output.xlsx"
        response.headers[
            "Content-Type"
        ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        return response

        # final_df.to_excel("output.xlsx", index=False)

    except Exception as e:
        import traceback

        print("Error details", traceback.format_exc())
        raise Exception(f"Error in file: {str(e)}")


# def modifyToExcel(data):
#     try:
#         state_dfs = []
#         for state_data in data:
#             state_name = state_data["state"]
#             year_dfs = []

#             for district_data in state_data["districtsData"]:
#                 district_name = district_data["district"]

#                 for index_value in district_data["indexValues"]:
#                     year = index_value["year"]
#                     index_value_data = index_value["singleYearData"]

#                     df = pd.DataFrame(index_value_data)
#                     df["Month"] = df.columns
#                     df["Month"] = df["Month"].apply(
#                         lambda x: x if x != "singleYearData" else None
#                     )
#                     df["District"] = district_name
#                     df["Index Value"] = (
#                         df.drop(columns=["Month", "District"]).sum(axis=1).astype(float)
#                     )
#                     df["Year"] = year
#                     df = df[["Month", "District", "Index Value", "Year"]]

#                     year_dfs.append(df)
#                 # empty_row = pd.Series(index=year_dfs[-1].columns)
#                 # year_dfs.append(empty_row)
#             state_df = pd.concat(year_dfs, ignore_index=True)
#             state_df["State"] = state_name
#             state_dfs.append(state_df)

#         final_df = pd.concat(state_dfs, ignore_index=True)
#         final_df.to_excel("output.xlsx", index=False)

#     except Exception as e:
#         import traceback

#         print("Error details", traceback.format_exc())
#         raise Exception(f"Error in file: {str(e)}")
