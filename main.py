import random
import string
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from db import (
    Post,
    Tree,
    User,
    get_all_posts,
    get_all_trees,
    get_posts_by_tree_id,
    get_posts_by_user_id,
    get_tree_by_user_id,
    get_user_by_id,
    get_user_by_wallet,
    init_db,
    insert_post,
    insert_tree,
    insert_user,
)

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

init_db()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/login")

@app.post("/user")
def create_user(user: User):
    insert_user(user)
    return {"message": "User created successfully"}


@app.get("/user/{user_id}")
def get_user(user_id: int):
    try:
        user = get_user_by_id(user_id)
        return user
    except:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/user/wallet/{wallet_id}")
def get_by_wallet(wallet_id: str):
    try:
        user = get_user_by_wallet(wallet_id)
        return user
    except:
        raise HTTPException(status_code=404, detail="User not found")
    

@app.get("/user/{user_id}/posts")
def get_user_posts(user_id: int):
    posts = get_posts_by_user_id(user_id)
    return posts


@app.post("/post")
def create_post(post: Post):
    insert_post(post)
    return {"message": "Post created successfully"}


@app.get("/post/user/{user_id}")
def get_post(user_id: int):
    post = get_posts_by_user_id(user_id)
    return post


@app.get("/posts")
def get_posts():
    posts = get_all_posts()
    return posts


@app.get("/post/tree/{tree_id}")
def get_posts_by_tree(tree_id: int):
    posts = get_posts_by_tree_id(tree_id)
    return posts

@app.get("/tree/get_last_id")
def get_last_tree_id():
    last_id = get_all_trees()[-1].id
    return last_id


@app.get("/trees")
def get_trees():
    trees = get_all_trees()
    return trees


@app.get("/user/{user_id}/trees")
def get_user_trees(user_id: int):
    trees = get_tree_by_user_id(user_id)
    return trees

class TreeReq(BaseModel):
    tree: Tree
    post: Post

@app.post("/tree")
def create_tree(req: TreeReq):
    id = insert_tree(req.tree)
    req.post.tree_id = id
    req.post.user_id = req.tree.user_id
    insert_post(req.post)
    return {"message": "Tree created successfully", "tree_id": id}

@app.post("/images")
def upload_tree_img(file: UploadFile):
    rando = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(15))
    with open(f"images/{file.filename}_{rando}", "wb") as f:
        f.write(file.file.read())
    
    return {"filename": f"{file.filename}_{rando}"}
  
app.mount("/images", StaticFiles(directory="images"), name="images")
  
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)