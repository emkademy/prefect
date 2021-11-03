"""
Routes for admin-level interactions with the Orion API.
"""

import sqlalchemy as sa
from sqlalchemy import orm
from fastapi import Depends, status, Response, Body

import prefect
from prefect.orion.utilities.server import OrionRouter
from prefect.orion.api import dependencies
from prefect.orion.database.dependencies import provide_database_interface

router = OrionRouter(prefix="/admin", tags=["Admin"])


@router.get("/hello")
def hello():
    """Say hello!"""
    return "👋"


@router.get("/settings")
def read_settings() -> prefect.utilities.settings.Settings:
    """Get the current Orion settings"""
    return prefect.settings


@router.get("/version")
def read_version() -> str:
    """Returns the Prefect version number"""
    return prefect.__version__


@router.post("/database/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_database(
    session: sa.orm.Session = Depends(dependencies.get_session),
    confirm: bool = Body(
        False,
        embed=True,
        description="Pass confirm=True to confirm you want to modify the database.",
    ),
    response: Response = None,
):
    """Clear all database tables without dropping them."""
    if not confirm:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    # TODO - can probably inject here
    db_interface = await provide_database_interface()
    for table in reversed(db_interface.Base.metadata.sorted_tables):
        await session.execute(table.delete())


@router.post("/database/drop", status_code=status.HTTP_204_NO_CONTENT)
async def drop_database(
    session: sa.orm.Session = Depends(dependencies.get_session),
    confirm: bool = Body(
        False,
        embed=True,
        description="Pass confirm=True to confirm you want to modify the database.",
    ),
    response: Response = None,
):
    """Drop all database objects."""
    if not confirm:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    db_interface = await provide_database_interface()
    await db_interface.drop_db()


@router.post("/database/create", status_code=status.HTTP_204_NO_CONTENT)
async def create_database(
    session: sa.orm.Session = Depends(dependencies.get_session),
    confirm: bool = Body(
        False,
        embed=True,
        description="Pass confirm=True to confirm you want to modify the database.",
    ),
    response: Response = None,
):
    """Create all database objects."""
    if not confirm:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    db_interface = await provide_database_interface()
    await db_interface.create_db()
