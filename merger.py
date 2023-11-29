import streamlit as st
import pandas as pd
from dateutil import parser as date_parser

st.title("Merge Sales Data")

# Define the columns for the output DataFrame
output_columns = ["Store", "Order ID", "Product", "Quantity", "Date", "Sales incl Tax", "Sales excl Tax"]

# Create an empty output DataFrame with the desired columns
output_data = pd.DataFrame(columns=output_columns)

# Define lists for "Lightspeed K CANADA" and "Lightspeed K OTHERS" stores
stores_k_canada = [
    "Iris Galerie -Toronto Distillery District",
    "Iris Galerie - Queen Street",
    "Iris Galerie - Niagara Falls",
    "Iris Galerie - Ottawa"
]

stores_k_others = [
    "Iris - Amsterdam Heiligeweg",
    "Iris - Amsterdam Spiegelgracht",
    "Iris - Maastricht",
    "Iris - Sluis",
    "Iris - Utrecht",
    "Iris - Amsterdam 9 Straatjes",
    "Iris Rotterdam",
    "Iris Galerie Spain  - KAINI INDUSTRIES SL",
    "Iris Galerie - Portobello",
    "Iris Galerie - Camden",
    "Iris Galerie - Camden 2",
    "MAROC"
]

# Function to merge uploaded files
def merge_files(tiller_file, lightspeed_l_files, flashcom_028_file, lightspeed_k_canada_files,
                lightspeed_k_others_files):
    global output_data

    # Process "TILLER" file
    if tiller_file:
        try:
            tiller_df = pd.read_csv(tiller_file, delimiter=';')  # Specify semicolon (;) as the delimiter
        except pd.errors.ParserError as e:
            st.warning(f"Error reading 'TILLER' file: {str(e)}")
            return

        if not tiller_df.empty:
            # Apply logic to populate the output DataFrame based on "TILLER" data
            tiller_df["Store"] = tiller_df.iloc[:, 0]  # Using 0-based column index
            tiller_df["Order ID"] = tiller_df.iloc[:, 4]  # Using 0-based column index
            tiller_df["Product"] = tiller_df.iloc[:, 6]  # Using 0-based column index
            tiller_df["Quantity"] = tiller_df.iloc[:, 8]  # Using 0-based column index
            tiller_df["Date"] = tiller_df.iloc[:, 2]  # Using 0-based column index
            tiller_df["Sales incl Tax"] = tiller_df.iloc[:, 12]  # Using 0-based column index
            tiller_df["Sales excl Tax"] = tiller_df.iloc[:, 13]  # Using 0-based column index

            # Append "TILLER" data to the output DataFrame
            output_data = pd.concat([output_data, tiller_df[output_columns]], ignore_index=True)

    # Process "LIGHTSPEED L" files
    for file in lightspeed_l_files:
        if file:
            try:
                df = pd.read_csv(file, delimiter=';')  # Specify comma (,) as the delimiter
            except pd.errors.ParserError as e:
                st.warning(f"Error reading 'LIGHTSPEED L' file: {str(e)}")
                continue

            if not df.empty:
                # Apply logic to populate the output DataFrame based on "LIGHTSPEED L" data
                df["Store"] = df.iloc[:, 1]  # Using 0-based column index
                df["Order ID"] = df.iloc[:, 2]  # Using 0-based column index
                df["Product"] = df.iloc[:, 9]  # Using 0-based column index
                df["Quantity"] = df.iloc[:, 11]  # Using 0-based column index

                # Custom date parser for "LIGHTSPEED L" files
                df["Date"] = df.iloc[:, 4].apply(custom_date_parser_lightspeed_l)  # Using 0-based column index

                df["Sales incl Tax"] = df.iloc[:, 15]  # Using 0-based column index
                df["Sales excl Tax"] = df.iloc[:, 15] * (1 - df.iloc[:, 16])  # Using 0-based column index

                # Append "LIGHTSPEED L" data to the output DataFrame
                output_data = pd.concat([output_data, df[output_columns]], ignore_index=True)

    # Process "FLASHCOM 028" file
    if flashcom_028_file:
        try:
            flashcom_df = pd.read_csv(flashcom_028_file, delimiter=',')  # Specify semicolon (;) as the delimiter
        except pd.errors.ParserError as e:
            st.warning(f"Error reading 'FLASHCOM 028' file: {str(e)}")
            return

        if not flashcom_df.empty:
            # Apply logic to populate the output DataFrame based on "FLASHCOM 028" data
            flashcom_df["Store"] = flashcom_df.iloc[:, 7]  # Using 0-based column index
            flashcom_df["Order ID"] = flashcom_df.iloc[:, 0]  # Using 0-based column index
            flashcom_df["Product"] = flashcom_df.iloc[:, 3]  # Using 0-based column index
            flashcom_df["Quantity"] = flashcom_df.iloc[:, 8]  # Using 0-based column index
            flashcom_df["Date"] = flashcom_df.iloc[:, 2]  # Using 0-based column index
            flashcom_df["Sales incl Tax"] = flashcom_df.iloc[:, 10]  # Using 0-based column index
            flashcom_df["Sales excl Tax"] = flashcom_df.iloc[:, 10] * 0.77  # Using 0-based column index

            # Append "FLASHCOM 028" data to the output DataFrame
            output_data = pd.concat([output_data, flashcom_df[output_columns]], ignore_index=True)

    # Process "Lightspeed K CANADA" files
    for store_name in lightspeed_k_canada_files.keys():
        store_files = lightspeed_k_canada_files[store_name]
        for file in store_files:
            if file:
                try:
                    df = pd.read_csv(file, delimiter=',')  # Specify semicolon (;) as the delimiter
                except pd.errors.ParserError as e:
                    st.warning(f"Error reading 'Lightspeed K CANADA' file: {str(e)}")
                    continue

                if not df.empty:
                    # Apply logic to populate the output DataFrame based on "Lightspeed K CANADA" data
                    df = df[df.iloc[:, 11] == "SALE"]  # Using 0-based column index
                    df["Store"] = store_name
                    df["Order ID"] = df.iloc[:, 7]  # Using 0-based column index
                    df["Product"] = df.iloc[:, 20]  # Using 0-based column index
                    df["Quantity"] = df.iloc[:, 12]  # Using 0-based column index
                    df["Date"] = df.iloc[:, 5]  # Using 0-based column index
                    df["Sales incl Tax"] = df.iloc[:, 25] * df.iloc[:, 24]  # Using 0-based column index
                    df["Sales excl Tax"] = df.iloc[:, 25]  # Using 0-based column index

                    # Append "Lightspeed K CANADA" data to the output DataFrame
                    output_data = pd.concat([output_data, df[output_columns]], ignore_index=True)

    # Process "Lightspeed K OTHERS" files
    for store_name in lightspeed_k_others_files.keys():
        store_files = lightspeed_k_others_files[store_name]

        for file in store_files:
            if file:
                try:
                    df = pd.read_csv(file, delimiter=',')  # Specify semicolon (;) as the delimiter
                except pd.errors.ParserError as e:
                    st.warning(f"Error reading 'Lightspeed K OTHERS' file: {str(e)}")
                    continue

                if not df.empty:
                    # Apply logic to populate the output DataFrame based on "Lightspeed K OTHERS" data
                    df = df[df.iloc[:, 11] == "SALE"]  # Using 0-based column index
                    df["Store"] = store_name
                    df["Order ID"] = df.iloc[:, 7]  # Using 0-based column index
                    df["Product"] = df.iloc[:, 20]  # Using 0-based column index
                    df["Quantity"] = df.iloc[:, 12]  # Using 0-based column index
                    df["Date"] = df.iloc[:, 5]  # Using 0-based column index
                    df["Sales incl Tax"] = df.iloc[:, 25] * df.iloc[:, 24]  # Using 0-based column index
                    df["Sales excl Tax"] = df.iloc[:, 25]  # Using 0-based column index

                    # Append "Lightspeed K OTHERS" data to the output DataFrame
                    output_data = pd.concat([output_data, df[output_columns]], ignore_index=True)
    if not output_data.empty:
        date_formats = {
            "FLASHCOM 028": "%Y-%m-%d",
            "Lightspeed K CANADA": "%d/%m/%y",
            "Lightspeed K OTHERS": "%d/%m/%y",
            "LIGHTSPEED L": "%m/%d/%y",
        }

        for store_name, date_format in date_formats.items():
            mask = output_data["Store"] == store_name
            output_data.loc[mask, "Date"] = pd.to_datetime(output_data.loc[mask, "Date"], format=date_format,
                                                           errors='coerce')

        # Now, check if the "Date" column contains datetime values before formatting
        if pd.api.types.is_datetime64_any_dtype(output_data["Date"]):
            output_data["Date"] = output_data["Date"].dt.strftime('%d/%m/%Y')
        else:
            st.warning("Date column does not contain valid datetime values. Please check the input files.")

    st.header("Merged Data:")
    st.write(output_data)

def custom_date_parser_lightspeed_l(date_str):
    try:
        # Specify the date format used in "LIGHTSPEED L" files, e.g., 'dd/mm/yy'
        return date_parser.parse(date_str, dayfirst=True).date()
    except ValueError:
        return None
# Allow users to upload the "TILLER" file
tiller_file = st.file_uploader("Upload TILLER file (e.g., with Order ID)", type=["csv"])

# Allow users to upload multiple "LIGHTSPEED L" files
lightspeed_l_files = st.file_uploader("Upload LIGHTSPEED L files (e.g., with Order ID)", type=["csv"],
                                      accept_multiple_files=True)

# Allow users to upload the "FLASHCOM 028" file
flashcom_028_file = st.file_uploader("Upload FLASHCOM 028 file (e.g., with Order ID)", type=["csv"])

# Allow users to upload files for "Lightspeed K CANADA" stores
lightspeed_k_canada_files = {}
for store_name in stores_k_canada:
    lightspeed_k_canada_files[store_name] = st.file_uploader(f"Upload files for {store_name}", type=["csv"],
                                                             accept_multiple_files=True)

# Allow users to upload files for "Lightspeed K OTHERS" stores
lightspeed_k_others_files = {}
for store_name in stores_k_others:
    lightspeed_k_others_files[store_name] = st.file_uploader(f"Upload files for {store_name}", type=["csv"],
                                                             accept_multiple_files=True)

# Add a button to trigger the merging process
if st.button("Merge Files"):
    merge_files(tiller_file, lightspeed_l_files, flashcom_028_file, lightspeed_k_canada_files,
                lightspeed_k_others_files)
    st.success(f"Successfully merged files!")

# Add a button to generate and download the merged data as a CSV file
if st.button("Generate Merged Data as CSV"):
    if not output_data.empty:
        csv_data = output_data.to_csv(index=False, sep=';')  # Specify semicolon (;) as the delimiter
        st.download_button("Download Merged Data", csv_data, key="download", file_name="merged_data.csv",
                           mime="text/csv")
    else:
        st.warning("No merged data to download. Please merge files first.")