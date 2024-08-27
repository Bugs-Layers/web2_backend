import os
import libsql_experimental as libsql

from pydantic import BaseModel

url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("test.db", sync_url=url, auth_token=auth_token)
conn.sync()


def init_db():
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,name TEXT NOT NULL,bio TEXT,wallet TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS trees (id INTEGER PRIMARY KEY,name TEXT NOT NULL,location TEXT NOT NULL,user_id INTEGER NOT NULL,type TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES users (id))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tree_imgs (  id INTEGER PRIMARY KEY,  tree_id INTEGER NOT NULL,  img TEXT NOT NULL,  upvotes INTEGER NOT NULL,  user_id INTEGER NOT NULL,  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  FOREIGN KEY (tree_id) REFERENCES trees (id),  FOREIGN KEY (user_id) REFERENCES users (id))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY,content TEXT NOT NULL,user_id INTEGER NOT NULL,tree_id INTEGER NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES users (id),FOREIGN KEY (tree_id) REFERENCES trees (id))"
    )
    conn.commit()
    conn.sync()


class User(BaseModel):
    id: int | None = None
    name: str
    bio: str | None = None
    wallet: str
    created_at: str | None = None
    updated_at: str | None = None

    def get_obj(data):
        return User(
            id=data[0],
            name=data[1],
            bio=data[2],
            wallet=data[3],
            created_at=data[4],
            updated_at=data[5],
        )


class Tree(BaseModel):
    id: int | None = None
    name: str
    location: str
    user_id: int
    type: str
    created_at: str | None = None
    updated_at: str | None = None

    def get_obj(data):
        return Tree(
            id=data[0],
            name=data[1],
            location=data[2],
            user_id=data[3],
            type=data[4],
            created_at=data[5],
            updated_at=data[6],
        )


class Post(BaseModel):
    id: int | None = None
    content: str
    user_id: int
    tree_id: int
    created_at: str | None = None
    updated_at: str | None = None
    username: str | None = None

    def get_obj(data):
        try:
            return Post(
                id=data[0],
                content=data[1],
                user_id=data[2],
                tree_id=data[3],
                created_at=data[4],
                updated_at=data[5],
                username=data[6] if data[6] else None,
            )
        except:
            return Post(
                id=data[0],
                content=data[1],
                user_id=data[2],
                tree_id=data[3],
                created_at=data[4],
                updated_at=data[5],
            )


def insert_user(user: User):
    conn.execute(
        "INSERT INTO users (name, bio, wallet) VALUES (?, ?, ?)",
        (
            user.name,
            user.bio,
            user.wallet,
        ),
    )
    conn.commit()
    conn.sync()


def insert_tree(tree: Tree):
    conn.execute(
        "INSERT INTO trees (name, location, user_id, type) VALUES (?, ?, ?, ?)",
        (
            tree.name,
            tree.location,
            tree.user_id,
            tree.type,
        ),
    )
    id = conn.lastrowid
    conn.commit()
    conn.sync()
    return id


def insert_post(post: Post):
    conn.execute(
        "INSERT INTO posts (content, user_id, tree_id) VALUES (?, ?, ?)",
        (
            post.content,
            post.user_id,
            post.tree_id,
        ),
    )
    conn.commit()
    conn.sync()


def get_user_by_name(name: str):

    data = conn.execute("SELECT * FROM users WHERE name=?", (name,)).fetchone()
    return User.get_obj(data)


def get_user_by_id(id: int):

    data = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()
    return User.get_obj(data)


def get_user_by_wallet(wallet: str):

    data = conn.execute("SELECT * FROM users WHERE wallet=?", (wallet,)).fetchone()
    if not data:
        raise Exception("User not found")
    return User.get_obj(data)


def get_tree_by_id(id: int):

    data = conn.execute("SELECT * FROM trees WHERE id=?", (id,)).fetchone()
    return Tree.get_obj(data)


def get_tree_by_user_id(user_id: int):

    data = conn.execute("SELECT * FROM trees WHERE user_id=?", (user_id,)).fetchall()
    return [Tree.get_obj(row) for row in data]


def get_posts_by_user_id(user_id: int):

    data = conn.execute(
        "SELECT * FROM posts WHERE user_id=? ORDER BY created_at DESC", (user_id,)
    ).fetchall()
    return [Post.get_obj(row) for row in data]


def get_posts_by_tree_id(tree_id: int):

    data = conn.execute("SELECT * FROM posts WHERE tree_id=?", (tree_id,)).fetchall()
    return [Post.get_obj(row) for row in data]


def get_all_posts():

    data = conn.execute(
        "SELECT posts.*, users.name FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.created_at DESC"
    ).fetchall()
    return [Post.get_obj(row) for row in data]


def get_all_trees():

    data = conn.execute("SELECT * FROM trees").fetchall()
    return [Tree.get_obj(row) for row in data]
