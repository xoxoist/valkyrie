# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from caller import Call, Perform
from pydantic import BaseModel


class CreatePostReq(BaseModel):
    title: str | None
    body: str | None
    userId: int | None
    headers: dict = {}


class CreatePostRes(BaseModel):
    id: int | None = None
    title: str | None = None
    body: str | None = None
    userId: int | None = None


def main():
    req_api = Call("https://1290912671264cc1a9235d4525eef0b1.api.mockbin.io/", connection=5, size=10, retry=5)
    req_api.add_header({"Content-Type": "application/json"})
    req_api.add_api(Perform("create_post", "posts", "POST"))

    create_post_res = req_api.execute("create_post", CreatePostReq(
        headers={"User-Agent": "Call-Lib-Test/1.0"},
        title="Foo2",
        body="Bar2",
        userId=2,
    ))
    if type(create_post_res) is str:
        raise Exception(f"Error {create_post_res}")
    created_post = CreatePostRes(**create_post_res.data)
    print(created_post)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
