from contextlib import contextmanager
from typing import Any, Generator, TypeVar

from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from app.models.base_model import BaseModel
from app.models.model_helpers import soft_delete as soft_delete_

T = TypeVar("T", bound=BaseModel)

__all__ = [
    "DatastoreAdapter",
]


class DatastoreAdapter:
    """
    データストアアダプター
    """

    def __init__(self, db_session: Session):
        """
        コンストラクタ

        :param db_session: DBセッション
        """
        self._db_session = db_session

    @property
    def session(self) -> Session:
        return self._db_session

    def add(self, model: T) -> None:
        """
        モデルをデータベースに追加します。

        :param model: モデルインスタンス
        :return: None
        """
        self._db_session.add(model)

    def soft_delete(
        self,
        model: BaseModel,
        conditions: list | dict[str, Any] | None = None,
    ) -> int:
        """
        モデルを論理削除します。

        :param model: モデルインスタンス
        :param conditions: 削除条件（オプション）
        :return: int 削除された行数
        """

        _conditions = conditions or {
            "id": model.id,
        }
        return soft_delete_(
            db_session=self._db_session,
            model_clazz=model.__class__,
            conditions=_conditions,
        )

    def commit(self) -> None:
        self._db_session.commit()

    def rollback(self) -> None:
        self._db_session.rollback()

    @contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """
        トランザクションコンテキストを提供します。

        :return: セッションオブジェクト
        """

        session = self.session
        needs_transaction = not session.in_transaction()
        if needs_transaction:
            session.begin()

        try:
            yield session
            session.commit()
        except Exception:
            if needs_transaction:
                session.rollback()
            raise

    def query(
        self,
        model_clazz: type[T],
    ) -> Query[T]:
        return self._db_session.query(model_clazz)

    def get(
        self,
        model_clazz: type[T],
        id_: Any,
        *,
        options: list[Any] | None = None,
    ) -> T | None:
        """
        指定したIDに対応するモデルを取得します。

        :param model_clazz: モデルクラス
        :param id_: モデルID
        :param options: クエリオプション（例：joinedload など）
        :return: モデルデータ
        """

        query = self._db_session.query(model_clazz)
        if options:
            query = query.options(*options)

        return query.get(id_)

    def all(
        self,
        model_clazz: type[T],
        *,
        filters: list[Any] | None = None,
        order_by: list[Any] | None = None,
        query: Query | None = None,
        options: list[Any] | None = None,
    ) -> list[T]:
        """
        データベースから全てのレコードを取得します。

        :param model_clazz: モデルクラス
        :param filters: 検索フィルター
        :param order_by: ソート条件
        :param query: クエリオブジェクト
        :param options: クエリオプション（例：joinedload など）
        :return: モデルリスト
        """

        if query is not None:
            db_query = query
        elif model_clazz is not None:
            db_query = self._db_session.query(model_clazz)
        else:
            raise ValueError(
                "Invalid arguments: model_clazz or query must be provided."
            )

        # 検索フィルター
        if filters:
            db_query = db_query.filter(*filters)

        # ソート条件
        if order_by:
            db_query = db_query.order_by(*order_by)

        # クエリオプション
        if options:
            db_query = db_query.options(*options)

        return db_query.all()

    def add_all(self, models: list[T]) -> None:
        self._db_session.add_all(models)

    def filter_by(self, model_clazz: type[T], **kwargs: Any) -> Query[T]:
        return self._db_session.query(model_clazz).filter_by(**kwargs)

    @staticmethod
    def paginate(
        query: Query[T],
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[T], int, int]:
        """
        クエリ結果をページングします。

        :param query: クエリオブジェクト
        :param page: ページ番号（1から開始）
        :param per_page: 1ページあたりの項目数
        :return: (データリスト, 件数, 総ページ数）
        """

        total = query.count()
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        total_pages = (total + per_page - 1) // per_page  # 切り上げ除算

        return items, total, total_pages
