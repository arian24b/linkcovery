from rich import print

from database import LinkDatabase, User, Link

# Main Script for Demonstration
if __name__ == "__main__":
    db = LinkDatabase()
    db.connect()
    db.create_table()

    # Create a user
    user = User(name="Alice", email="alice@example.com")

    # Create a link with an author
    new_link = Link(
        url="https://example.com",
        domain="example.com",
        description="An example website",
        tag=["example", "test"],
        author_id=0,  # Temporary, will be set atomically
    )

    success = db.create_user_and_link(user, new_link)

    if not success:
        print("[red]Failed to create user and link atomically. Exiting.[/red]")
        db.close()
        exit(1)

    # Retrieve all links with authors
    print("\nLinks with authors:")
    links_with_authors = db.read_links_with_authors()
    for entry in links_with_authors:
        print(f"Link: {entry['link']}, Author: {entry['author']}")

    # Search links with filtering, sorting, and pagination
    print("\nSearch results:")
    search_results = db.search_links(
        domain="example",
        tags=["test"],
        description="example",
        sort_by="created_at",
        sort_order="DESC",
        limit=5,
        offset=0,
    )
    for link in search_results:
        print(link)

    # Close the database connection
    db.close()
