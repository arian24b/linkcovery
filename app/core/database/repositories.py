from sqlalchemy.orm import Session

from app.core.database.models import User, Link


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_data):
        if self.get_by_email(user_data.get("email")):
            raise ValueError(f"User with email '{user_data.get('email')}' already exists.")
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        return user

    def get_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str):
        return self.session.query(User).filter(User.email == email).first()

    def update(self, user_id: int, user_data):
        if user := self.get_by_id(user_id):
            for key, value in user_data.items():
                setattr(user, key, value)
            self.session.commit()
        return user

    def delete(self, user_id: int):
        if user := self.get_by_id(user_id):
            self.session.delete(user)
            self.session.commit()

    def get_all(self):
        return self.session.query(User).all()


class LinkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, link_data):
        if self.get_by_url(link_data.get("url")):
            raise ValueError(f"Link with URL '{link_data.get('url')}' already exists.")
        link = Link(**link_data)
        self.session.add(link)
        self.session.commit()
        return link

    def get_by_id(self, link_id: int):
        return self.session.query(Link).filter(Link.id == link_id).first()

    def get_by_url(self, url: str):
        return self.session.query(Link).filter(Link.url == url).first()

    def search(self, search_criteria):
        query = self.session.query(Link)
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
        sort_by = search_criteria.get("sort_by")
        sort_order = search_criteria.get("sort_order", "ASC")
        if sort_by and hasattr(Link, sort_by):
            column = getattr(Link, sort_by)
            if sort_order.upper() == "DESC":
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

    def delete(self, link_id: int):
        if link := self.get_by_id(link_id):
            self.session.delete(link)
            self.session.commit()

    def get_all(self):
        return self.session.query(Link).all()

    def get_links_by_author(self, author_id: int, number: int | None = None):
        if number:
            return self.session.query(Link).filter(Link.author_id == author_id).limit(number).all()
        return self.session.query(Link).filter(Link.author_id == author_id).all()
