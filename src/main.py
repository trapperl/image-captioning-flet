# src/main.py
import flet as ft
import os

TAGS_FILE = "tags.txt"

# Set minimum widths as constants
MIN_THUMBNAILS_WIDTH = 160
MIN_CENTRAL_WIDTH = 400
MIN_TAG_MANAGEMENT_WIDTH = 250

def main(page: ft.Page):
    page.title = "Image Captioning Tool"
    page.padding = 0
    page.spacing = 0
    
    # Set dark theme and background
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK

    # Main image display
    image_display = ft.Image(
        src="https://via.placeholder.com/300",
        width=400,
        height=400,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(10),
    )

    # Caption input area (set to same width as the image display)
    caption_input = ft.TextField(
        label="Enter Caption",
        multiline=True,
        min_lines=3,
        max_lines=5,
        width=400,
        filled=True,
        fill_color=ft.Colors.BLACK,
        border_color=ft.Colors.GREY,
    )

    page.snack_bar = ft.SnackBar(ft.Text(""))
    selected_folder_path = ft.Text("No folder selected", italic=True)
    
    # Initialize variables
    current_image_path = None
    tags = []
    editing_tag = None

    def load_tags():
        nonlocal tags
        if os.path.exists(TAGS_FILE):
            try:
                loaded_tags = [line.strip() for line in open(TAGS_FILE) if line.strip()]
                tags = loaded_tags if loaded_tags else ["cat", "dog", "house", "car"]
            except Exception as e:
                print(f"Error loading tags: {e}")
                tags = ["cat", "dog", "house", "car"]
        else:
            tags = ["cat", "dog", "house", "car"]

    load_tags()

    # Tag input field and add button
    tag_input_field = ft.TextField(label="Add New Tag", width=150,fill_color=ft.Colors.BLACK, border_color=ft.Colors.GREY,)
    add_tag_button = ft.ElevatedButton("Add Tag")
    tag_input_row = ft.Column(controls=[tag_input_field, add_tag_button], width=150, tight=True)

    # Tag list area (will fill available space inside the scrollable container)
    tag_list_column = ft.Column()
    tag_list_container = ft.Container(
        content=tag_list_column,
        expand=True,
        padding=ft.padding.only(right=40)
    )

    # Tag edit container (this area will remain fixed at the bottom)
    tag_edit_container = ft.Container()

    def save_caption(image_path, caption_text):
        if image_path:
            caption_file_path = os.path.splitext(image_path)[0] + ".txt"
            try:
                with open(caption_file_path, 'w') as f:
                    f.write(caption_text)
                page.snack_bar.content = ft.Text("Caption saved!")
            except Exception as e:
                page.snack_bar.content = ft.Text(f"Error saving caption: {e}")
        else:
            page.snack_bar.content = ft.Text("No image selected to save caption for.")
        page.snack_bar.open = True
        page.update()

    def load_caption(image_path):
        if image_path:
            caption_file_path = os.path.splitext(image_path)[0] + ".txt"
            if os.path.exists(caption_file_path):
                try:
                    return open(caption_file_path).read()
                except Exception as e:
                    print(f"Error loading caption: {e}")
                    return ""
            return ""
        return ""

    def on_save_button_click(e):
        nonlocal current_image_path
        save_caption(current_image_path, caption_input.value)

    save_button = ft.ElevatedButton("Save Caption", on_click=on_save_button_click)
    # Place the caption field above the save button in a column.
    caption_column = ft.Column(controls=[caption_input, save_button], spacing=10)

    def save_tags_to_file():
        try:
            with open(TAGS_FILE, 'w') as f:
                for tag in tags:
                    f.write(tag + "\n")
        except Exception as e:
            print(f"Error saving tags: {e}")

    def delete_tag(tag_to_delete):
        nonlocal tags
        tags.remove(tag_to_delete)
        save_tags_to_file()
        update_tag_list()
        page.snack_bar.content = ft.Text(f"Tag '{tag_to_delete}' deleted.")
        page.snack_bar.open = True
        page.update()

    def edit_tag(tag_to_edit):
        nonlocal editing_tag
        editing_tag = tag_to_edit
        update_tag_list()

    def save_edited_tag(old_tag, new_tag):
        nonlocal tags, editing_tag
        if new_tag.strip() and new_tag.strip() != old_tag:
            try:
                tags[tags.index(old_tag)] = new_tag.strip()
                save_tags_to_file()
                page.snack_bar.content = ft.Text(f"Tag '{old_tag}' updated to '{new_tag.strip()}'.")
            except ValueError:
                page.snack_bar.content = ft.Text(f"Error updating tag '{old_tag}'. Tag not found.")
            page.snack_bar.open = True
        elif new_tag.strip() == old_tag:
            page.snack_bar.content = ft.Text("Tag name unchanged.")
            page.snack_bar.open = True
        else:
            page.snack_bar.content = ft.Text("Tag name cannot be empty.")
            page.snack_bar.open = True
        editing_tag = None
        update_tag_list()

    def cancel_edit_tag(e):
        nonlocal editing_tag
        editing_tag = None
        update_tag_list()

    def update_tag_list():
        tag_list_column.controls.clear()
        for tag in tags:
            row = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.TextButton(
                            content=ft.Text(tag, overflow=ft.TextOverflow.ELLIPSIS),
                            on_click=lambda e, tag_text=tag: on_tag_click(tag_text)
                        ),
                        expand=True
                    ),
                    ft.IconButton(
                        icon=ft.icons.EDIT,
                        tooltip="Edit tag",
                        on_click=lambda e, tag_to_edit=tag: edit_tag(tag_to_edit),
                        width=20, height=20, padding=0
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        tooltip="Delete tag",
                        on_click=lambda e, tag_to_delete=tag: delete_tag(tag_to_delete),
                        width=20, height=20, padding=0
                    ),
                ],
                spacing=5
            )
            tag_list_column.controls.append(row)

        # Update the separate tag edit area (fixed below)
        if editing_tag is not None:
            edit_field = ft.TextField(value=editing_tag, expand=True)
            tag_edit_container.content = ft.Column(
                controls=[
                    ft.Text("Edit Tag:", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    edit_field,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton("Save", on_click=lambda e: save_edited_tag(editing_tag, edit_field.value)),
                            ft.ElevatedButton("Cancel", on_click=cancel_edit_tag)
                        ],
                        spacing=5
                    )
                ],
                spacing=10
            )
        else:
            tag_edit_container.content = None

        tag_list_column.update()
        tag_edit_container.update()
        page.update()

    def on_tag_click(tag_text):
        caption_input.value += " " + tag_text
        page.update()

    def add_tag(e):
        nonlocal tags
        new_tag = tag_input_field.value.strip()
        if new_tag and new_tag not in tags:
            tags.append(new_tag)
            save_tags_to_file()
            update_tag_list()
            tag_input_field.value = ""
            page.update()

    add_tag_button.on_click = add_tag

    def on_thumbnail_click(image_path):
        def inner_click(e):
            nonlocal current_image_path
            current_image_path = image_path
            image_display.src = image_path
            caption_input.value = load_caption(image_path)
            page.update()
        return inner_click

    def on_directory_picked(e: ft.FilePickerResultEvent):
        if e.path:
            selected_folder_path.value = f"Selected directory: {e.path}"
            image_files = []
            try:
                for filename in os.listdir(e.path):
                    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                        image_files.append(os.path.join(e.path, filename))
                
                thumbnails_column.controls.clear()
                for image_path in image_files:
                    thumbnail_image = ft.Image(
                        src=image_path,
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=ft.border_radius.all(8),
                        tooltip=image_path,
                    )
                    thumbnails_column.controls.append(
                        ft.Container(
                            content=ft.GestureDetector(
                                content=thumbnail_image,
                                on_tap=on_thumbnail_click(image_path),
                            ),
                            padding=5,
                            width=100,
                        )
                    )
                if image_files:
                    current_image_path = image_files[0]
                    image_display.src = image_files[0]
                    caption_input.value = load_caption(image_files[0])
                page.update()
            except Exception as ex:
                print(f"Error listing images: {ex}")
                selected_folder_path.value = "Error listing images"
        else:
            selected_folder_path.value = "Cancelled!"
        page.update()

    directory_picker = ft.FilePicker(on_result=on_directory_picked)
    page.overlay.append(directory_picker)
    select_folder_button = ft.ElevatedButton(
        "Select Folder",
        on_click=lambda _: directory_picker.get_directory_path()
    )

    # Left column (thumbnails)
    thumbnails_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    image_thumbnails_container = ft.Container(
        content=thumbnails_column,
        width=MIN_THUMBNAILS_WIDTH,
        bgcolor=ft.Colors.BLACK,
        padding=10,
        border=ft.border.only(right=ft.BorderSide(1, ft.Colors.OUTLINE))
    )
    
    # Central content
    central_content = ft.Container(
        content=ft.Column(
            controls=[
                image_display,
                caption_column,
                selected_folder_path
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        ),
        expand=True,
        bgcolor=ft.Colors.BLACK,
        padding=20,
    )
    
    # Right column:
    # Create a scrollable column for the tag input and list.
    tags_scrollable_container = ft.Column(
        controls=[
            ft.Text("Tags", style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)),
            tag_input_row,
            tag_list_container,
        ],
        spacing=10,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
    # Then create a column that places the scrollable area on top and the fixed edit area below.
    tag_management_container = ft.Container(
        content=ft.Column(
            controls=[
                tags_scrollable_container,
                tag_edit_container
            ],
            spacing=10,
            expand=True,
        ),
        width=MIN_TAG_MANAGEMENT_WIDTH,
        bgcolor=ft.Colors.BLACK,
        padding=10,
        border=ft.border.only(left=ft.BorderSide(1, ft.Colors.OUTLINE))
    )
    
    # Main layout
    main_row = ft.Row(
        controls=[
            image_thumbnails_container,
            central_content,
            tag_management_container
        ],
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH
    )
    
    # Set window constraints
    page.window.min_width = MIN_THUMBNAILS_WIDTH + MIN_CENTRAL_WIDTH + MIN_TAG_MANAGEMENT_WIDTH + 40
    
    # Add everything to the page
    page.add(
        ft.Container(
            content=ft.Column([
                main_row,
                select_folder_button
            ]),
            expand=True,
            padding=10
        )
    )
    
    update_tag_list()

if __name__ == "__main__":
    ft.app(target=main)
