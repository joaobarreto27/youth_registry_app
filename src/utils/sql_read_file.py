from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import text


class SqlReadFile:
    def __init__(self, sql_file: str, engine, current_dir: Path) -> None:
        self.sql_file: str = sql_file
        self.engine: Any = engine
        self.current_dir: Path = current_dir
        self.query = None
        self.path_file = None
        self.df = None
        self.columns = None

    def read_sql_file(self) -> str:
        self.path_file = self.current_dir.parent.joinpath(
            "sql", "query", f"{self.sql_file}.sql"
        )

        if not self.path_file.is_file():
            raise FileNotFoundError(f"SQL file '{self.path_file}' not found.")

        with open(self.path_file, "r") as file:
            self.query = file.read()
        return self.query

    def execute_query_sql(self, params: Optional[dict] = None) -> Any | dict[str, Any]:

        if not self.query:
            raise ValueError("Query is empty. Please read the SQL file first.")

        with self.engine.connect() as connection:
            try:
                result: Any = connection.execute(text(self.query), params or {})
                if result.return_rows:
                    self.data = result.fetchall()
                    self.columns = result.keys()
                    return self.data
                else:
                    return {"rowcount": result.rowcount}
            except Exception as e:
                raise RuntimeError(f"Error executing query: {e}")

    def query_to_dataframe(self) -> pd.DataFrame:

        if not self.data:
            raise ValueError("Data is empty. Please execute the query first.")
        if not self.columns:
            raise ValueError("Columns are missing. Please execute the query first.")

        self.df = pd.DataFrame(self.data, self.columns)
        return self.df
