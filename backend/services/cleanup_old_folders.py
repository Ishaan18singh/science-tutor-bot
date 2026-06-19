import os
import shutil

# The NCERT placeholder chapter names we want to remove
# (only if they're EMPTY - never deletes folders with real content)
def cleanup_empty_placeholder_folders(content_path="../content"):
    removed = []
    kept = []

    for subject in os.listdir(content_path):
        subject_path = os.path.join(content_path, subject)
        if not os.path.isdir(subject_path):
            continue

        for cls in os.listdir(subject_path):
            cls_path = os.path.join(subject_path, cls)
            if not os.path.isdir(cls_path):
                continue

            for chapter in os.listdir(cls_path):
                chapter_path = os.path.join(cls_path, chapter)
                if not os.path.isdir(chapter_path):
                    continue

                # Check folder contents
                files = os.listdir(chapter_path)
                has_real_content = any(
                    f.endswith(".txt") or f.endswith(".pdf") for f in files
                )

                if has_real_content:
                    kept.append(chapter_path)
                else:
                    # Only has .gitkeep or is empty -> safe to remove
                    shutil.rmtree(chapter_path)
                    removed.append(chapter_path)

    print(f"🗑️  Removed {len(removed)} empty placeholder folders")
    print(f"✅ Kept {len(kept)} folders with real content\n")

    print("Kept folders (have actual content):")
    for k in kept:
        print(f"   {k}")


if __name__ == "__main__":
    confirm = input("This will delete EMPTY chapter folders (keeps any with .txt/.pdf). Continue? (y/n): ")
    if confirm.lower() == 'y':
        cleanup_empty_placeholder_folders()
    else:
        print("Cancelled.")