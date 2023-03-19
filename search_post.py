import sys
from database import create_connection, search_post_with_string

if len(sys.argv) < 2:
    print("Usage: python search_post.py <search_string>")
    sys.exit(1)

search_string = sys.argv[1]
conn = create_connection()
post = search_post_with_string(conn, search_string)

if post:
    print("Post found:")
    print(post)
else:
    print("No post found with the specified search string.")
