import pandas as pd
import pycountry
from sklearn.preprocessing import OneHotEncoder

from snowfall.project.junction.plus.service.flight_prediction.models import (
    encoder as encoder_models,
)


class Encoder(object):
    def encode(
        self,
        flight_info: encoder_models.FlightInfo,
    ) -> encoder_models.FlightInfoEncoded:
        data_frame = self._flight_info_to_pd_date_frame(flight_info)

        # Calculate departure delay
        actual_departure = data_frame["actual_departure"]
        scheduled_departure = data_frame["scheduled_departure"]
        departure_delay = actual_departure - scheduled_departure
        departure_delay_seconds = departure_delay.dt.total_seconds() / 60
        data_frame["departure_delay"] = departure_delay_seconds

        # Extract additional date and time components
        data_frame["scheduled_departure_time"] = scheduled_departure.dt.strftime("%H%M")
        data_frame["actual_departure_time"] = actual_departure.dt.strftime("%H%M")
        data_frame["quarter"] = actual_departure.dt.quarter
        data_frame["month"] = actual_departure.dt.month
        data_frame["day"] = actual_departure.dt.day
        data_frame["week_day"] = actual_departure.dt.dayofweek

        schedule_arrival = data_frame["scheduled_arrival"]
        data_frame["scheduled_arrival_time"] = schedule_arrival.dt.strftime("%H%M")

        data_frame = data_frame.drop(
            columns=[
                "scheduled_departure",
                "actual_departure",
                "scheduled_arrival",
            ],
        )

        categorical_columns = [
            "quarter",
            "month",
            "day",
            "week_day",
            "departure_country_code",
            "arrival_country_code",
        ]

        # Select the columns that won't be encoded
        unchanged_columns = [
            col for col in data_frame.columns if col not in categorical_columns
        ]

        # Separate and encode the categorical columns
        categorical_data = data_frame[categorical_columns]
        encoder = self._create_encoder_object()
        encoded_categorical_data = encoder.fit_transform(categorical_data)
        encoded_categorical_data = pd.DataFrame(encoded_categorical_data.toarray())
        encoded_categorical_data = encoded_categorical_data.reset_index(drop=True)
        unchanged_data = data_frame[unchanged_columns]
        unchanged_data = unchanged_data.reset_index(drop=True)
        # Combine the encoded categorical columns with the uchanged columns
        encoded_data = pd.concat([unchanged_data, encoded_categorical_data], axis=1)
        encoded_data = encoded_data.astype(int)

        row = encoded_data.iloc[0]
        row_array = row.to_numpy()
        vector = ",".join(row_array.astype(str))

        return encoder_models.FlightInfoEncoded(vector=vector)

    def _create_encoder_object(self) -> OneHotEncoder:
        country_codes = [country.alpha_2 for country in pycountry.countries]

        max_day_of_month = 31
        max_month_number = 12

        categories = [
            [1, 2, 3, 4],
            list(range(1, max_month_number + 1)),
            list(range(1, max_day_of_month + 1)),
            list(range(7)),
            country_codes,
            country_codes,
        ]

        return OneHotEncoder(handle_unknown="error", categories=categories)

    def _flight_info_to_pd_date_frame(
        self,
        flight_info: encoder_models.FlightInfo,
    ) -> pd.DataFrame:
        scheduled_departure_time_iso = (
            flight_info.scheduled_departure_date_time_local.isoformat()
        )
        actual_departure_time_iso = (
            flight_info.departure_actual_off_ground_date_time_local.isoformat()
        )
        scheduled_arrival_time_iso = (
            flight_info.scheduled_arrival_date_time_local.isoformat()
        )

        frame_data = {
            "scheduled_departure": [scheduled_departure_time_iso],
            "actual_departure": [actual_departure_time_iso],
            "scheduled_arrival": [scheduled_arrival_time_iso],
            "departure_country_code": [flight_info.departure_country_code],
            "arrival_country_code": [flight_info.arrival_country_code],
        }

        data_frame = pd.DataFrame(frame_data)

        # Convert to optimized data type
        data_frame["departure_country_code"] = data_frame[
            "departure_country_code"
        ].astype("category")
        data_frame["arrival_country_code"] = data_frame["arrival_country_code"].astype(
            "category",
        )

        # Convert strings date time
        data_frame["scheduled_departure"] = pd.to_datetime(
            data_frame["scheduled_departure"],
            format="ISO8601",
        )
        data_frame["actual_departure"] = pd.to_datetime(
            data_frame["actual_departure"],
            format="ISO8601",
        )
        data_frame["scheduled_arrival"] = pd.to_datetime(
            data_frame["scheduled_arrival"],
            format="ISO8601",
        )

        return data_frame
