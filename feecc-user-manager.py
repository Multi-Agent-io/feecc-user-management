import typing as tp

import typer
from tabulate import tabulate

from database import Employee, MongoDbWrapper

employees: tp.Dict[str, Employee] = {}


def get_employee_by_number() -> tp.Optional[Employee]:
    employee_num: str = typer.prompt("Choose employee number from the table")

    global employees
    if employee_num in employees:
        return employees[employee_num]
    else:
        typer.echo("No such employee in table")


def list_employees(db: MongoDbWrapper) -> None:
    global employees
    data = db.get_all_employees()
    employees = {str(no): employee for no, employee in enumerate(data, start=1)}
    employee_data = [
        [no, employee.name, employee.position, employee.rfid_card_id]
        for no, employee in enumerate(data, start=1)
    ]
    employee_table = tabulate(employee_data, headers=["№", "Name", "Position", "RFID card"])
    typer.echo("\n" + employee_table + "\n")


def add_employee(db: MongoDbWrapper) -> None:
    employee = Employee(
        name=typer.prompt("Full name"),
        position=typer.prompt("Position"),
        rfid_card_id=typer.prompt("RFID card ID"),
    )
    if typer.confirm("Add employee entry?"):
        db.add_employee(employee)
        typer.echo("Employee was added successfully. New table:")
        list_employees(db)
    else:
        typer.echo("Employee add operation was cancelled.")


def delete_employee(db: MongoDbWrapper) -> None:
    employee = get_employee_by_number()
    if employee and typer.confirm(f"Remove employee {employee.name}?"):
        db.remove_employee(employee)
        typer.echo("Employee was deleted successfully. New table:")
        list_employees(db)
    else:
        typer.echo("Employee remove operation was cancelled.")


def edit_employee(db: MongoDbWrapper) -> None:
    old_employee = get_employee_by_number()
    if not old_employee:
        return

    new_employee = Employee(
        name=typer.prompt("Full name (press Enter to leave as is)", default="") or old_employee.name,
        position=typer.prompt("Position (press Enter to leave as is)", default="") or old_employee.position,
        rfid_card_id=typer.prompt("RFID card ID (press Enter to leave as is)", default="") or old_employee.rfid_card_id,
    )

    diff = f"""
    The following changes will be applied:
    {old_employee.name} -> {new_employee.name}
    {old_employee.position} -> {new_employee.position}
    {old_employee.rfid_card_id} -> {new_employee.rfid_card_id}
    """
    typer.echo(diff)

    if typer.confirm("Apply changes?"):
        db.update_employee(old_employee, new_employee)
        typer.echo("Employee data was updated successfully. New table:")
        list_employees(db)
    else:
        typer.echo("Employee update operation was cancelled.")


def main() -> None:
    mongo_connection_url = typer.prompt("MongoDB connection URI")
    database = MongoDbWrapper(mongo_connection_url)

    typer.echo("Current employee table:")
    list_employees(database)

    while True:
        command: str = typer.prompt("Enter command from [list, add, delete, edit, exit]")

        if command == "list":
            list_employees(database)
        elif command == "add":
            add_employee(database)
        elif command == "delete":
            delete_employee(database)
        elif command == "edit":
            edit_employee(database)
        elif command == "exit":
            break
        else:
            typer.echo("Command not recognized")

    typer.echo("Exiting")


if __name__ == "__main__":
    typer.run(main)
