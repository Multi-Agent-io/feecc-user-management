import typing as tp
from dataclasses import asdict, dataclass

from pymongo import MongoClient


@dataclass
class Employee:
    """stores data about the worker"""

    name: str = ""
    position: str = ""
    rfid_card_id: str = ""


class MongoDbWrapper:
    """handles interactions with MongoDB database"""

    def __init__(self, mongo_client_url: str) -> None:
        self._client: MongoClient = MongoClient(mongo_client_url)
        self._database = self._client["feeccProd"]
        self._employee_collection = self._database["emlpoyeeData"]

    def get_all_employees(self) -> tp.List[Employee]:
        return [Employee(**data) for data in list(self._employee_collection.find({}, {"_id": 0}))]

    def add_employee(self, employee: Employee) -> None:
        self._employee_collection.insert_one(asdict(employee))

    def remove_employee(self, employee: Employee) -> None:
        self._employee_collection.find_one_and_delete(asdict(employee))

    def update_employee(self, old_employee: Employee, new_employee: Employee) -> None:
        self._employee_collection.find_one_and_update(asdict(old_employee), {"$set": asdict(new_employee)})
