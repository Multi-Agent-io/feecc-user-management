import hashlib
import typing as tp
from dataclasses import asdict, dataclass

from pymongo import MongoClient


@dataclass
class Employee:
    rfid_card_id: str
    name: str
    position: str
    passport_code: str = ""

    def __post_init__(self) -> None:
        if not self.passport_code:
            self.passport_code = self.get_passport_code()

    def get_passport_code(self) -> str:
        employee_passport_string: str = " ".join([self.rfid_card_id, self.name, self.position])
        employee_passport_string_encoded: bytes = employee_passport_string.encode()
        return hashlib.sha256(employee_passport_string_encoded).hexdigest()


class MongoDbWrapper:
    """handles interactions with MongoDB database"""

    def __init__(self, mongo_client_url: str) -> None:
        self._client: MongoClient = MongoClient(mongo_client_url)
        self._database = self._client["feeccProd"]
        self._employee_collection = self._database["employeeData"]

    def get_all_employees(self) -> tp.List[Employee]:
        return [Employee(**data) for data in list(self._employee_collection.find({}, {"_id": 0}))]

    def add_employee(self, employee: Employee) -> None:
        self._employee_collection.insert_one(asdict(employee))

    def remove_employee(self, employee: Employee) -> None:
        self._employee_collection.find_one_and_delete(asdict(employee))

    def update_employee(self, old_employee: Employee, new_employee: Employee) -> None:
        self._employee_collection.find_one_and_update(asdict(old_employee), {"$set": asdict(new_employee)})
