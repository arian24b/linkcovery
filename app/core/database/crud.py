from sqlalchemy.orm import Session

from repositories import UserRepository, LinkRepository


class UserService:
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session)

    def create_user(self, user_data):
        return self.user_repository.create(user_data)

    def get_user(self, user_id: int):
        return self.user_repository.get_by_id(user_id)

    def update_user(self, user_id: int, user_data):
        return self.user_repository.update(user_id, user_data)

    def delete_user(self, user_id: int):
        return self.user_repository.delete(user_id)


class LinkService:
    def __init__(self, session: Session):
        self.link_repository = LinkRepository(session)

    def create_link(self, link_data):
        return self.link_repository.create(link_data)

    def get_link(self, link_id: int):
        return self.link_repository.get_by_id(link_id)

    def search_links(self, search_criteria):
        return self.link_repository.search(search_criteria)

    def update_link(self, link_id: int, link_data):
        return self.link_repository.update(link_id, link_data)

    def delete_link(self, link_id: int):
        return self.link_repository.delete(link_id)
