from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database.repositories import UserRepository, LinkRepository


class UserService:
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session)

    def create_user(self, user_data):
        return self.user_repository.create(user_data)

    def get_user(self, user_id: int | None = None, user_email: str | None = None):
        if user_id:
            return self.user_repository.get_by_id(user_id)
        elif user_email:
            return self.user_repository.get_by_email(user_email)
        else:
            return None

    def update_user(self, user_id: int, user_data):
        return self.user_repository.update(user_id, user_data)

    def delete_user(self, user_id: int):
        return self.user_repository.delete(user_id)

    def get_users(self):
        return self.user_repository.get_all()


class LinkService:
    def __init__(self, session: Session):
        self.link_repository = LinkRepository(session)

    def create_link(self, **link_data):
        link_data["created_at"] = datetime.utcnow()
        link_data["updated_at"] = link_data["created_at"]
        return self.link_repository.create(link_data)

    def get_link(self, link_id: int | None = None, link_url: str | None = None):
        if link_id:
            return self.link_repository.get_by_id(link_id)
        elif link_url:
            return self.link_repository.get_by_url(link_url)
        else:
            return None

    def search_links(self, search_criteria):
        return self.link_repository.search(search_criteria)

    def update_link(self, link_id: int, **link_data):
        link_data["updated_at"] = datetime.utcnow()
        return self.link_repository.update(link_id, link_data)

    def delete_link(self, link_id: int):
        return self.link_repository.delete(link_id)

    def get_links(self):
        return self.link_repository.get_all()

    def get_links_by_author(self, author_id: int, number: int | None = None):
        return self.link_repository.get_links_by_author(author_id, number)
