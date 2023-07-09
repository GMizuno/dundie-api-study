import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select
import pandas as pd

from dundie.models.user import generate_username
from .config import settings
from .db import engine, SQLModel
from .models import User, Transaction, Balance
from .tasks.transaction import add_transaction

main = typer.Typer(name="dundie CLI", add_completion=False)


@main.command()
def shell():
    """Opens interactive shell"""
    _vars = {
        "settings": settings,
        "engine": engine,
        "select": select,
        "session": Session(engine),
        "User": User,
        "Transaction": Transaction,
        "Balance": Balance,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    typer.echo('Hello Dunder Mifflin employers')
    try:
        from IPython import start_ipython

        start_ipython(
            argv=["--ipython-dir=/tmp", "--no-banner"], user_ns=_vars
        )
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@main.command()
def user_list():
    """Lists all users"""
    table = Table(title="dundie users")
    fields = ["name", "username", "dept", "email", "currency"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        users = session.exec(select(User))
        for user in users:
            table.add_row(*[getattr(user, field) for field in fields])

    Console().print(table)


@main.command()
def create_user(
        name: str,
        email: str,
        password: str,
        dept: str,
        username: str | None = None,
        currency: str = "USD",
):
    """Create user"""
    with Session(engine) as session:
        user = User(
            name=name,
            email=email,
            password=password,
            dept=dept,
            username=username or generate_username(name),
            currency=currency,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {user.username} user")
        return user

@main.command()
def balance_list():
    """List balances of all users. NOT IMPLEMENTED YET"""
    query = select(User.name, Balance).join(User, Balance.user_id == User.id)

    table = Table(title="User balances")
    fields = ["name", "updated_at", "value", "user_id"]

    table.add_column("name", style="blue")
    for header in fields[1:]:
        table.add_column(header, style="red")

    with Session(engine) as session:
        balance_list = session.exec(query)
        for balance in balance_list:
            _balance = [
                getattr(balance, 'name'),
                str(getattr(balance[1], "updated_at")),
                str(getattr(balance[1], "value")),
                str(getattr(balance[1], "user_id")),
            ]
            table.add_row(*_balance)
        Console().print(table)


@main.command()
def transaction(
        username: str,
        value: int,
):
    """Adds specified value to the user"""

    table = Table(title="Transaction")
    fields = ["user", "before", "after"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        from_user = session.exec(select(User).where(User.username == "admin")).first()
        if not from_user:
            typer.echo("admin user not found")
            exit(1)
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            typer.echo(f"user {username} not found")
            exit(1)

        from_user_before = from_user.balance
        user_before = user.balance
        add_transaction(user=user, from_user=from_user, session=session, value=value)
        table.add_row(from_user.username, str(from_user_before), str(from_user.balance))
        table.add_row(user.username, str(user_before), str(user.balance))

        Console().print(table)


@main.command()
def create_user_from_csv():
    """Create user from csv. NOT IMPLEMENTED YET"""
    pass


@main.command()
def export_user_to_csv(path: str = '.'):
    """Export all user to csv file. NOT IMPLEMENTED YET"""
    with Session(engine) as session:
        fields = ['email', 'name', 'username', 'dept', 'currency']
        query = select(User.email, User.name, User.username, User.dept, User.currency)
        users = session.exec(query).all()
        _users = [{field: getattr(user, field) for field in fields} for user in users]
        df = pd.DataFrame.from_records(_users)
        path = path + '/users.csv'
        df.to_csv(path_or_buf=path, index=False)

@main.command()
def export_transaction_to_csv():
    """Export all transaction to csv file. NOT IMPLEMENTED YET"""
    pass


@main.command()
def reset_db(
        force: bool = typer.Option(
            False, "--force", "-f", help="Run with no confirmation"
        )
):
    """Resets the database tables"""
    force = force or typer.confirm("Are you sure?")
    if force:
        SQLModel.metadata.drop_all(engine)
