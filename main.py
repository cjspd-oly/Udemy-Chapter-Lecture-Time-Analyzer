import json
import os

# Get absolute path of the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "autosave.json")

# Load JSON file
with open(JSON_PATH, "r", encoding="utf-8") as file:
    raw_data = json.load(file)

# Extract course data
courses = raw_data.get("json_data", {})


# Function to clear console (only when requested)
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


# Extract course data
courses = raw_data.get("json_data", {})


# Convert "hh:mm:ss" or "mm:ss" to seconds
def time_to_seconds(time_str):
    try:
        parts = list(map(int, time_str.split(":")))
        if len(parts) == 3:
            hours, minutes, seconds = parts
        elif len(parts) == 2:
            hours, minutes, seconds = 0, parts[0], parts[1]
        else:
            return 0
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return 0  # Ignore invalid time formats


# Convert seconds back to "hh:mm:ss"
def seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"


# Select course
def select_course():
    print("\n📚 **Available Courses**")
    course_ids = list(courses.keys())

    for idx, course_id in enumerate(course_ids, start=1):
        title = (
            courses[course_id]
            .get("curriculum_context", {})
            .get("data", {})
            .get("course_title", "Unknown Course")
        )
        print(f"{idx}. {title}")

    while True:
        try:
            choice = int(input("\n🔹 Select a course (1 to n): "))
            if 1 <= choice <= len(course_ids):
                return course_ids[choice - 1]
            print("⚠️ Invalid choice. Try again.")
        except ValueError:
            print("❌ Enter a valid number.")


# Select section
# Select section with total time
def select_section(course):
    sections = course.get("curriculum_context", {}).get("data", {}).get("sections", [])
    if not sections:
        print("⚠️ No sections available.")
        return None

    print("\n📖 **Sections Available**")
    for idx, section in enumerate(sections, start=1):
        title = section["title"]
        total_time = section.get("content_length_text", "Unknown Time")
        lecture_count = len(
            [
                item
                for item in section.get("items", [])
                if item.get("item_type") == "lecture"
            ]
        )
        print(f"{idx}. {title} ({lecture_count} lectures, ⏳ {total_time})")

    while True:
        try:
            choice = int(input("\n🔹 Select a section (1 to n): "))
            if 1 <= choice <= len(sections):
                return sections[choice - 1]
            print("⚠️ Invalid choice. Try again.")
        except ValueError:
            print("❌ Enter a valid number.")


# Task 1: Split section into custom time chunks
def split_section_by_time():
    selected_course_id = select_course()
    selected_course = courses[selected_course_id]

    selected_section = select_section(selected_course)
    if not selected_section:
        return

    lectures = [
        item
        for item in selected_section.get("items", [])
        if item.get("item_type") == "lecture"
    ]
    if not lectures:
        print("⚠️ No lectures available.")
        return

    while True:
        try:
            chunk_time = (
                int(
                    input(
                        "\n⏳ Enter chunk time in minutes (e.g., 60 for 1-hour sections): "
                    )
                )
                * 60
            )
            if chunk_time > 0:
                break
            print("⚠️ Time must be positive.")
        except ValueError:
            print("❌ Enter a valid number.")

    total_time = 0
    chunk_index = 1
    current_chunk = []

    print(
        f"\n📖 **Splitting Section: {selected_section['title']} into {chunk_time // 60}-minute chunks**"
    )

    for lecture in lectures:
        duration = time_to_seconds(lecture.get("content_summary", "0:00"))
        total_time += duration
        current_chunk.append(f"🎬 {lecture['title']} - {lecture['content_summary']}")

        if total_time >= chunk_time:
            print(f"\n🔹 **Chunk {chunk_index}:**")
            print("\n".join(current_chunk))
            print(f"🕒 **Total Time:** {seconds_to_time(total_time)}")
            chunk_index += 1
            total_time = 0
            current_chunk = []

    if current_chunk:
        print(f"\n🔹 **Chunk {chunk_index}:**")
        print("\n".join(current_chunk))
        print(f"🕒 **Total Time:** {seconds_to_time(total_time)}")


# Task 2: Sum time between selected lectures
def sum_lecture_time():
    selected_course_id = select_course()
    selected_course = courses[selected_course_id]

    selected_section = select_section(selected_course)
    if not selected_section:
        return

    lectures = [
        item
        for item in selected_section.get("items", [])
        if item.get("item_type") == "lecture"
    ]
    if not lectures:
        print("⚠️ No lectures available.")
        return

    print("\n🎬 **Lectures Available:**")
    for idx, lecture in enumerate(lectures, start=1):
        print(
            f"{idx}. {lecture.get('title', 'No Title')} - {lecture.get('content_summary', 'Unknown')}"
        )

    while True:
        try:
            start = int(input("\n🔹 Select START lecture (1 to n): "))
            end = int(input("🔹 Select END lecture (1 to n): "))

            if (
                1 <= start <= len(lectures)
                and 1 <= end <= len(lectures)
                and start <= end
            ):
                selected_lectures = lectures[start - 1 : end]
                break
            print("⚠️ Invalid range. Try again.")
        except ValueError:
            print("❌ Enter a valid number.")

    total_time = sum(
        time_to_seconds(lecture.get("content_summary", "0:00"))
        for lecture in selected_lectures
    )
    avg_time = total_time / len(selected_lectures) if selected_lectures else 0

    print("\n📊 **Lecture Time Summary**")
    print(f"🕒 **Total Time:** {seconds_to_time(total_time)}")
    print(f"📏 **Average Time per Lecture:** {seconds_to_time(int(avg_time))}")


# Main menu
def main():
    while True:
        print("\n🔹 **Choose a Task**")
        print("1. Split Section into Time Chunks")
        print("2. Sum Time Between Selected Lectures")
        print("3. Clear")
        print("4. Exit")

        choice = input("\n🔹 Enter choice (1-4): ")

        if choice == "1":
            clear_console()
            split_section_by_time()
        elif choice == "2":
            clear_console()
            sum_lecture_time()
        elif choice == "3":
            clear_console()
        elif choice == "4":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()
