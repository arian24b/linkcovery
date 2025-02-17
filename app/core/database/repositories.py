from sqlalchemy.orm import Session

from models import User, Link


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_data):
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        return user

    def get_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str):
        return self.session.query(User).filter(User.email == email).first()

    def update(self, user_id: int, user_data):
        user = self.get_by_id(user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            self.session.commit()
        return user

    def delete(self, user_id: int):
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()


class LinkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, link_data):
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
        if "url" in search_criteria:
            query = query.filter(Link.url.contains(search_criteria["url"]))
        if "tag" in search_criteria:
            query = query.filter(Link.tag.contains(search_criteria["tag"]))
        return query.all()

    def update(self, link_id: int, link_data):
        link = self.get_by_id(link_id)
        if link:
            for key, value in link_data.items():
                setattr(link, key, value)
            self.session.commit()
        return link

    def delete(self, link_id: int):
        link = self.get_by_id(link_id)
        if link:
            self.session.delete(link)
            self.session.commit()
