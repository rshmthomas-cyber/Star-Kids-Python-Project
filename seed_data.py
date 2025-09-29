from app import app, db
from models import Parent, Kid, Task

with app.app_context():
    # 1. Clear old data
    db.drop_all()
    db.create_all()

    # 2. Create a parent
    parent = Parent(username="Reshma", password="1234")
    db.session.add(parent)
    db.session.commit()

    # 3. Add kids
    kid1 = Kid(name="Aaric", age=7, parent_id=parent.id, points=0)
    kid2 = Kid(name="Aksha", age=5, parent_id=parent.id, points=0)
    kid3 = Kid(name="Abram", age=3, parent_id=parent.id, points=0)
    db.session.add_all([kid1, kid2, kid3])
    db.session.commit()

    # 4. Add tasks for kids
    task1 = Task(description="Clean your study table", kid_id=kid1.id, completed=False)
    task2 = Task(description="Do homework", kid_id=kid2.id, completed=False)
    db.session.add_all([task1, task2])
    db.session.commit()

    print("✅ Sample parent, kids, and tasks inserted successfully!")
