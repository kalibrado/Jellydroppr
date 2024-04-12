""" Class database for json lite database """

import json


class FinderDB:
    """This class for manipulate json data file"""

    def __init__(self, name="Jellydroppr", path="data/database.json"):
        self.name = name
        self.path = path
        self.data = {
            "radarr": {"failed": {}, "success": {}},
            "sonarr": {"failed": {}, "success": {}},
        }

    def prepare(self):
        """create database.json if file not exist"""
        with open(self.path, "w", encoding="utf-8") as infile:
            json.dump(self.data, infile, indent=4, ensure_ascii=False)

    def _read_db(self):
        with open(self.path, "r", encoding="utf-8") as infile:
            try:
                data = json.load(infile)
                return data
            except json.JSONDecodeError:
                return self.data

    def get(self, key: str):
        """Return data of specifique key

        Args:
            key (str): key of element to need in database.json

        Returns:
            any : Return value of key in database.json
        """
        data = self._read_db()
        return data[self.name][key]

    def update(self, status: str, key: str, value: any):
        """Update data in database.json for match key

        Args:
            status (str): status of data ( failed | success )
            key (str): key for update data
            value (any): value to insert in key
        """
        data = self._read_db()
        data[self.name][status][key] = value
        with open(self.path, "w", encoding="utf-8") as infile:
            json.dump(data, infile, indent=4, ensure_ascii=False)
