import pandas as pd
from flask import make_response
from io import BytesIO
import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Alignment

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
        columns_to_keep = ["Month", "Year", "State", "District", "Index Value"]
        final_df = final_df[columns_to_keep]

        column_order = ["Month", "Year", "State", "District", "Index Value"]
        final_df = final_df.reindex(columns=column_order, fill_value=None)

        excel_output = BytesIO()

        with pd.ExcelWriter(excel_output, engine="openpyxl") as writer:
            final_df.to_excel(writer, index=False, sheet_name="Sheet1")

            worksheet = writer.sheets["Sheet1"]

            (max_row, max_col) = final_df.shape

            table_range = f"A1:{openpyxl.utils.get_column_letter(max_col)}{max_row}"

            table = Table(displayName="MyTable", ref=table_range)
            style = TableStyleInfo(
                name="TableStyleMedium9",
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=True,
            )
            table.tableStyleInfo = style
            worksheet.add_table(table)

            for row_num in range(1, max_row + 1):
                for col_num in range(max_col):
                    cell_coord = openpyxl.utils.get_column_letter(col_num + 1) + str(
                        row_num + 1
                    )
                    worksheet[cell_coord].alignment = Alignment(horizontal="center")

            for col_num, value in enumerate(final_df.columns.values):
                column_letter = openpyxl.utils.get_column_letter(col_num + 1)
                max_length = max(
                    final_df[value].astype(str).apply(len).max(), len(value)
                )
                adjusted_width = max_length + 2
                worksheet.column_dimensions[column_letter].width = adjusted_width

        excel_output.seek(0)

        response = make_response(excel_output.read())
        response.headers["Content-Disposition"] = "attachment; filename=output.xlsx"
        response.headers[
            "Content-Type"
        ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        return response

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
#                     df = df[["Month", "Year", "District", "Index Value"]]

#                     year_dfs.append(df)
#                 empty_row = pd.Series([None] * df.shape[1], index=df.columns)
#                 year_dfs.append(empty_row)
#             for df in year_dfs:
#                 df["State"] = state_name
#             year_dfs = [
#                 df[["Month", "Year", "State", "District", "Index Value"]]
#                 for df in year_dfs
#             ]
#             state_df = pd.concat(year_dfs, ignore_index=True)
#             state_dfs.append(state_df)

#         final_df = pd.concat(state_dfs, ignore_index=True)
#         final_df = final_df.iloc[:, :-1]

#         excel_output = BytesIO()
#         final_df.to_excel(excel_output, index=False)
#         excel_output.seek(0)

#         response = make_response(excel_output.read())
#         response.headers[
#             "Content-Disposition"
#         ] = "attachment; filename=output.xlsx"
#         response.headers[
#             "Content-Type"
#         ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

#         return response

#         # final_df.to_excel("output.xlsx", index=False)

#     except Exception as e:
#         import traceback

#         print("Error details", traceback.format_exc())
#         raise Exception(f"Error in file: {str(e)}")
