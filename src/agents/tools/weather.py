import requests
from typing import Dict
from datetime import datetime, timedelta

from .tool import Tool


class WeatherTool(Tool):
    def __init__(self, api_key, TIME_FORMAT="%Y-%m-%d"):
        description = "Get historical weather data"
        name = "weather"
        parameters = {
            "city_name": {
                "type": "string",
                "description": "The name of the city",
            },
            "country_code": {
                "type": "string",
                "description": "The country code of the city",
            },
            "start_date": {
                "type": "string",
                "description": "The start date of the weather data",
            },
            "end_date": {
                "type": "string",
                "description": "The end date of the weather data",
            },
        }
        super(WeatherTool, self).__init__(description, name, parameters)
        self.TIME_FORMAT = TIME_FORMAT
        self.api_key = api_key

    def _parse(self, data):
        dict_data: dict = {}
        for item in data["data"]:
            date = item["datetime"]
            dict_data[date] = {}
            if "weather" in item:
                dict_data[date]["description"] = item["weather"]["description"]
            mapping = {
                "temp": "temperature",
                "max_temp": "max_temperature",
                "min_temp": "min_temperature",
                "precip": "accumulated_precipitation",
            }
            for key in ["temp", "max_temp", "min_temp", "precip"]:
                if key in item:
                    dict_data[date][mapping[key]] = item[key]
        return dict_data

    def _query(self, city_name, country_code, start_date, end_date):
        """https://www.weatherbit.io/api/historical-weather-daily"""
        # print(datetime.strftime(start_date, self.TIME_FORMAT), datetime.strftime(datetime.now(), self.TIME_FORMAT), end_date, datetime.strftime(datetime.now()+timedelta(days=1), self.TIME_FORMAT))
        if start_date == datetime.strftime(
            datetime.now(), self.TIME_FORMAT
        ) and end_date == datetime.strftime(
            datetime.now() + timedelta(days=1), self.TIME_FORMAT
        ):
            """today"""
            url = f"https://api.weatherbit.io/v2.0/current?city={city_name}&country={country_code}&key={self.api_key}"
        else:
            url = f"https://api.weatherbit.io/v2.0/history/daily?&city={city_name}&country={country_code}&start_date={start_date}&end_date={end_date}&key={self.api_key}"
        response = requests.get(url)
        data = response.json()
        return self._parse(data)

    def func(self, weather_dict: Dict) -> Dict:
        TIME_FORMAT = self.TIME_FORMAT
        # Beijing, Shanghai
        city_name = weather_dict["city_name"]
        # CN, US
        country_code = weather_dict["country_code"]
        # 2020-02-02
        start_date = datetime.strftime(
            datetime.strptime(weather_dict["start_date"], self.TIME_FORMAT),
            self.TIME_FORMAT,
        )
        end_date = weather_dict["end_date"] if "end_date" in weather_dict else None
        if end_date is None:
            end_date = datetime.strftime(
                datetime.strptime(start_date, TIME_FORMAT) + timedelta(days=-1),
                TIME_FORMAT,
            )
        else:
            end_date = datetime.strftime(
                datetime.strptime(weather_dict["end_date"], self.TIME_FORMAT),
                self.TIME_FORMAT,
            )
        if datetime.strptime(start_date, TIME_FORMAT) > datetime.strptime(
            end_date, TIME_FORMAT
        ):
            start_date, end_date = end_date, start_date
        assert start_date != end_date
        return self._query(city_name, country_code, start_date, end_date)
