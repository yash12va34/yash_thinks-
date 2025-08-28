# TO DO LIST

tasks = []   # empty list to hold tasks

def add_task():
    task = input("Enter task: ")
    tasks.append({"task": task, "completed": False})
    print("✅ Task added successfully!")

def view_tasks():
    if not tasks:
        print("📭 No tasks in the list.")
    else:
        for i, t in enumerate(tasks, start=1):
            status = "✔️ Complete" if t["completed"] else "❌ Incomplete"
            print(f"{i}. {t['task']} - {status}")

def delete_task():
    view_tasks()
    try:
        task_num = int(input("Enter task number to delete: ")) - 1
        removed = tasks.pop(task_num)
        print(f"🗑️ Task '{removed['task']}' removed successfully.")
    except (IndexError, ValueError):
        print("⚠️ Invalid task number.")

def mark_as_complete():
    view_tasks()
    try:
        task_num = int(input("Enter task number to mark as complete: ")) - 1
        tasks[task_num]["completed"] = True
        print(f"✅ Task '{tasks[task_num]['task']}' marked as complete.")
    except (IndexError, ValueError):
        print("⚠️ Invalid task number.")

def main_menu():
    print("\n--- TO DO LIST MENU ---")
    print("1. Add task")
    print("2. View tasks")
    print("3. Delete task")
    print("4. Mark as complete")
    print("5. Exit")

def main():
    while True:
        main_menu()
        choice = input("Enter choice (1-5): ")

        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            delete_task()
        elif choice == "4":
            mark_as_complete()
        elif choice == "5":
            print("👋 Exiting program... Goodbye!")
            break
        else:
            print("⚠️ Invalid choice, try again.")

if __name__ == "__main__":
    main()
