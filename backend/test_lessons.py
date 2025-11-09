"""
Quick test script to debug lessons endpoint
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.content import Lesson

def test_lessons():
    """Test fetching lessons from database"""
    db = SessionLocal()

    try:
        # Test basic query
        print("Testing lessons query...")
        lessons = db.query(Lesson).order_by(Lesson.order_index).all()

        print(f"\nFound {len(lessons)} lessons\n")

        if lessons:
            # Print first lesson details
            lesson = lessons[0]
            print(f"First lesson:")
            print(f"  ID: {lesson.id}")
            print(f"  Title: {lesson.title}")
            print(f"  Level: {lesson.level}")
            print(f"  Order: {lesson.order_index}")
            print(f"  Total sections: {lesson.total_sections}")
            print(f"  Git commands: {lesson.git_commands}")
            print(f"  Content type: {type(lesson.content)}")

            # Try to serialize
            try:
                from app.schemas.player import LessonListResponse
                response = LessonListResponse(
                    id=lesson.id,
                    title=lesson.title,
                    level=lesson.level,
                    order_index=lesson.order_index,
                    total_sections=lesson.total_sections,
                    git_commands=lesson.git_commands
                )
                print(f"\nSerialization successful!")
                print(f"Response: {response.model_dump_json()}")
            except Exception as e:
                print(f"\nSerialization ERROR: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No lessons found in database!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_lessons()
