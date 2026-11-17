import time

# def timer(func):
#     def wrapper(*args, **kwargs):
#         start = time.time()
#         result = func(*args, **kwargs)
#         print(f"{func.__name__} took {time.time()-start:.2f}s")
#         return result

#     return wrapper


# @timer
# def search_wiki():
#     pass


# search_wiki = timer(search_wiki)
# print(type(search_wiki))


def timer(func):
    print(f"timer is decorating {func.__name__}")

    def wrapper(*args, **kwargs):
        print("wrapper is running")
        result = func(*args, **kwargs)
        return result

    return wrapper


# @timer
def add(a, b):
    return a + b


new_func = add

print(new_func(1, 2))


print(add)  # <function timer.<locals>.wrapper ...>  ← proof that add IS wrapper now
print(add(2, 3))  # "wrapper is running", then 5
print(new_func(2, 3))  # "wrapper is running", then 5
