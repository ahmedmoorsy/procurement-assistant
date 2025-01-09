import logging
import warnings
import pandas as pd

logger = logging.getLogger(__name__)

warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".*Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated.*",
)


class DataTransformer:
    """
    Transform each chunk of data (clean, parse, validate).
    """

    def transform_chunk(self, chunk_df: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates the transformation by calling individual methods.
        """
        df = chunk_df.copy()

        df = self._fix_purchase_date(df)
        df = self._clean_numeric_columns(df)
        df = self._fix_total_price(df)
        df = self._clean_strings(df)

        return df

    def _fix_purchase_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rewrite the year suffix to '20xx', parse 'Purchase Date' to datetime,
        and replace missing or invalid 'Purchase Date' values with 'Creation Date'.
        """
        if "Purchase Date" in df.columns and "Creation Date" in df.columns:
            valid_dates = df["Purchase Date"].dropna()
            fixed_dates = [
                date_str[:-4] + "20" + date_str[-2:]
                for date_str in valid_dates
                if len(date_str) >= 4
            ]
            fixed_dates_series = pd.to_datetime(fixed_dates, errors="coerce")
            df.loc[valid_dates.index, "Purchase Date"] = fixed_dates_series
            df["Creation Date"] = pd.to_datetime(df["Creation Date"], errors="coerce")
            df["Purchase Date"] = (
                df["Purchase Date"]
                .fillna(df["Creation Date"])
                .infer_objects(copy=False)
            )

        return df

    def _clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove '$' sign from numeric columns, convert to float, and fill NaN.
        Handles errors gracefully for non-numeric or malformed values.
        """
        for col in ["Unit Price", "Total Price"]:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .str.replace(r"[^\d.-]", "", regex=True)
                    .replace("", "0")
                    .astype(float)
                )

        if "Quantity" in df.columns:
            df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)

        for col in ["Unit Price", "Quantity", "Total Price"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)

        return df

    def _fix_total_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recalculate 'Total Price' if missing, and remove anomalies (negative or extremely large).
        """
        if all(x in df.columns for x in ["Total Price", "Unit Price", "Quantity"]):
            df["Total Price"] = df.apply(
                lambda row: (
                    row["Unit Price"] * row["Quantity"]
                    if (
                        row["Total Price"] == 0
                        and row["Unit Price"] != 0
                        and row["Quantity"] != 0
                    )
                    else row["Total Price"]
                ),
                axis=1,
            )

        if "Total Price" in df.columns:
            df.loc[
                (df["Total Price"] < 0) | (df["Total Price"] > 8e4), "Total Price"
            ] = 0

        return df

    def _clean_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert all text columns to lowercase and replace NaN with empty string.
        """
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].fillna("")
                df[col] = df[col].str.lower()
        return df
