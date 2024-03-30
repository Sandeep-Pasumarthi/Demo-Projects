from neo4j import GraphDatabase
from dotenv import load_dotenv

import os

load_dotenv()

class Neo4jDemo:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))

    def close(self):
        self._driver.close()

    def create_user_nodes(self):
        with self._driver.session() as session:
            session.run("""
                LOAD CSV WITH HEADERS FROM 'file:///C:/Users/sivas/Desktop/BlackCofferInternship/TasksBeforeJoining/Neo4j/DataSet/users.csv' AS row
                MERGE (u:User {user_id: toInteger(row.user_id)})
                SET u.name = row.name
            """)

    def create_relationships(self):
        with self._driver.session() as session:
            session.run("""
                LOAD CSV WITH HEADERS FROM 'file:///C:/Users/sivas/Desktop/BlackCofferInternship/TasksBeforeJoining/Neo4j/DataSet/relationships.csv' AS row
                MATCH (user1:User {user_id: toInteger(row.user_id_1)})
                MATCH (user2:User {user_id: toInteger(row.user_id_2)})
                MERGE (user1)-[:FRIEND]->(user2)
            """)

    def create_posts(self):
        with self._driver.session() as session:
            session.run("""
                LOAD CSV WITH HEADERS FROM 'file:///C:/Users/sivas/Desktop/BlackCofferInternship/TasksBeforeJoining/Neo4j/DataSet/posts.csv' AS row
                MATCH (user:User {user_id: toInteger(row.user_id)})
                CREATE (post:Post {post_id: toInteger(row.post_id), content: row.content})
                MERGE (user)-[:POSTED]->(post)
            """)
    
    def query_friends_of_user(self, user_id):
        with self._driver.session() as session:
            result = session.run("""
                MATCH (user:User {user_id: $user_id})-[:FRIEND]->(friend)
                RETURN friend.name AS friend_name
            """, user_id=user_id)
            return [record["friend_name"] for record in result]

    def like_post(self, user_id, post_id):
        with self._driver.session() as session:
            session.run("""
                MATCH (user:User {user_id: $user_id})
                MATCH (post:Post {post_id: $post_id})
                MERGE (user)-[:LIKED]->(post)
            """, user_id=user_id, post_id=post_id)

    def comment_on_post(self, user_id, post_id, content):
        with self._driver.session() as session:
            session.run("""
                MATCH (user:User {user_id: $user_id})
                MATCH (post:Post {post_id: $post_id})
                CREATE (comment:Comment {content: $content})
                MERGE (user)-[:COMMENTED]->(comment)
                MERGE (comment)-[:ON_POST]->(post)
            """, user_id=user_id, post_id=post_id, content=content)

    def get_posts_with_comments(self):
        with self._driver.session() as session:
            result = session.run("""
                MATCH (post:Post)<-[:POSTED]-(user:User)
                OPTIONAL MATCH (comment:Comment)-[:ON_POST]->(post)
                RETURN post, user, COLLECT(comment) AS comments
            """)
            return [(record["post"], record["user"], record["comments"]) for record in result]


if __name__ == "__main__":
    neo4j_demo = Neo4jDemo(os.getenv("NEO4J_URI"), os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    neo4j_demo.create_user_nodes()
    neo4j_demo.create_relationships()
    neo4j_demo.create_posts()

    # Friends of user
    user_id=1
    friends=neo4j_demo.query_friends_of_user(user_id)
    print(f"Friends of user {user_id}: {friends}\n")

    # Like post
    neo4j_demo.like_post(user_id=1, post_id=2)

    #Comment on post
    neo4j_demo.comment_on_post(user_id=2, post_id=1, content="Nice post!")
    neo4j_demo.comment_on_post(user_id=1, post_id=3, content="I totally agree!!!")

    # Get posts with comments
    posts_with_comments = neo4j_demo.get_posts_with_comments()
    for post, user, comments in posts_with_comments:
        print(f"Post by {user['name']}: {post['content']}")
        if comments:
            print("Comments:")
            for comment in comments:
                print(f"- {comment['content']}")
        else:
            print("No comments yet")
        print()

    neo4j_demo.close()
