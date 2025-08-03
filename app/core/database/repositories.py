from sqlalchemy.orm import Session

from app.core.database.models import Link
from app.core.exceptions import EntityAlreadyExistsError, RepositoryError


class LinkRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, link_data):
        """Create a new link with better error handling."""
        if self.get_by_url(link_data.get("url")):
            msg = "Link"
            raise EntityAlreadyExistsError(msg, link_data.get("url"))

        try:
            link = Link(**link_data)
            self.session.add(link)
            self.session.commit()
            return link
        except Exception as e:
            self.session.rollback()
            msg = f"Failed to create link: {e}"
            raise RepositoryError(msg) from e

    def get_by_id(self, link_id: int):
        return self.session.query(Link).filter(Link.id == link_id).first()

    def get_by_url(self, url: str):
        return self.session.query(Link).filter(Link.url == url).first()

    def search(self, search_criteria):
        query = self.session.query(Link)

        # Filter by URL if provided
        if search_criteria.get("url"):
            query = query.filter(Link.url.contains(search_criteria["url"]))

        # Filter by domain if provided
        if search_criteria.get("domain"):
            query = query.filter(Link.domain.contains(search_criteria["domain"]))

        # Filter by each tag provided
        if search_criteria.get("tag"):
            for tag in search_criteria["tag"]:
                query = query.filter(Link.tag.contains(tag))

        # Filter by description if provided
        if search_criteria.get("description"):
            query = query.filter(Link.description.contains(search_criteria["description"]))

        # Filter by read status if provided
        if search_criteria.get("is_read") is not None:
            query = query.filter(Link.is_read == search_criteria["is_read"])

        # Sorting: if a sort field is provided and exists on the Link model
        if (sort_by := search_criteria.get("sort_by")) and hasattr(Link, sort_by):
            column = getattr(Link, sort_by)
            if search_criteria.get("sort_order", "ASC").upper() == "DESC":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

        # Pagination: apply offset and limit if provided
        if search_criteria.get("offset") is not None:
            query = query.offset(search_criteria["offset"])
        if search_criteria.get("limit") is not None:
            query = query.limit(search_criteria["limit"])

        return query.all()

    def update(self, link_id: int, link_data):
        if link := self.get_by_id(link_id):
            for key, value in link_data.items():
                setattr(link, key, value)
            self.session.commit()
        return link

    def delete(self, link_id: int) -> None:
        if link := self.get_by_id(link_id):
            self.session.delete(link)
            self.session.commit()

    def get_all(self):
        return self.session.query(Link).all()
