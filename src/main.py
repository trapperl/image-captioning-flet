# src/main.py
import flet as ft
import os
import openai
from dotenv import load_dotenv
import base64

dotenv_loaded = load_dotenv()  # Load .env first to ensure it's loaded even if env var is set
print(f"dotenv_loaded: {dotenv_loaded}")  # Debug print to check if dotenv was loaded
openai_api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key after loading dotenv: {openai_api_key}")  # Debug print
if not openai_api_key:
    print(".env file did not contain OPENAI_API_KEY, or not loaded properly")  # Debug print
openai.api_key = openai_api_key

TAGS_FILE = "tags.txt"

# Set minimum widths as constants
MIN_THUMBNAILS_WIDTH = 160
MIN_CENTRAL_WIDTH = 400
MIN_TAG_MANAGEMENT_WIDTH = 250

def main(page: ft.Page):
    page.title = "Image Captioning Tool"
    page.padding = 0
    page.spacing = 0

    # Declare settings_column first so it can be used in toggle_settings_visibility.
    settings_column = None

    def toggle_settings_visibility(e):
        nonlocal settings_column
        settings_column.visible = not settings_column.visible
        page.update()

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
    tag_input_field = ft.TextField(
        label="Add New Tag",
        width=150,
        fill_color=ft.Colors.BLACK,
        border_color=ft.Colors.GREY,
    )
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
    api_key_field = ft.Ref[ft.TextField]()  # Declare api_key_field as Ref
    # Set a default prompt value here.
    prompt_field = ft.TextField(
        value="Write a caption for this image as if it was going to be used to train a vision model.",
        label="Prompt", width=300, fill_color=ft.Colors.BLACK, border_color=ft.Colors.GREY
    )
    progress_bar = ft.ProgressBar()

    async def on_generate_caption_button_click(e):
        nonlocal current_image_path, api_key_field, prompt_field, progress_bar
        print("Generate Caption button clicked")

        page.update()
        api_key_from_field = api_key_field.current.value
        print(f"API Key from field: {api_key_from_field}")
        prompt = prompt_field.value
        print(f"Prompt: {prompt}")
        print(f"Current Image Path: {current_image_path}")

        api_key_to_use = api_key_from_field or openai.api_key

        if not api_key_to_use or not api_key_to_use.strip():  # Check for empty or whitespace API key
            page.snack_bar.content = ft.Text("Please enter your OpenAI API key in the text field or set a non-empty OPENAI_API_KEY in the .env file.")
            page.snack_bar.open = True
            page.update()
            return

        if current_image_path:
            progress_bar.visible = True
            page.update()
            try:
                generated_caption = await generate_caption_from_openai(
                    image_path=current_image_path,
                    prompt=prompt,
                    page=page,
                    api_key=api_key_to_use
                )
                caption_input.value = generated_caption
            except Exception as e:
                print(f"Error in generate_caption_from_openai: {e}")
                page.snack_bar.content = ft.Text(f"Error generating caption: {e}")
                page.snack_bar.open = True
            finally:
                progress_bar.visible = False
                page.update()
        else:
            page.snack_bar.content = ft.Text("No image selected to generate caption.")
            page.snack_bar.open = True
            page.update()

    generate_caption_button = ft.ElevatedButton("Generate Caption", on_click=on_generate_caption_button_click)

    # Create a single row for caption actions so they appear centered under the caption input.
    caption_actions_row = ft.Row(
        controls=[
            save_button,
            generate_caption_button,
            ft.IconButton(
                icon=ft.icons.SETTINGS,
                tooltip="Show settings",
                on_click=lambda e: toggle_settings_visibility(e),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )

    caption_column = ft.Column(
        controls=[
            caption_input,
            caption_actions_row,
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    async def generate_caption_from_openai(image_path, prompt, page, api_key):
        openai.api_key = api_key  # Set API key here to ensure it's used in this function call
        print("generate_caption_from_openai function entered")
        print(f"Image Path: {image_path}")
        print(f"API Key being used in generate_caption_from_openai: {openai.api_key}")
        try:
            print("Opening image file...")
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
                print("Image file opened successfully")
                print("Encoding image to base64...")
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                print("Image encoded to base64")
                print(f"OpenAI API Key in generate_caption_from_openai: {openai.api_key}")
                print("Calling OpenAI API...")
                print(f"Prompt being sent to OpenAI: {prompt}")
                print(f"Model being used: gpt-4o")
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                            ],
                        }
                    ],
                    max_tokens=300,
                )
                print("OpenAI API call successful")
                print(f"Raw OpenAI API response: {response}")
                print(f"OpenAI library version: {openai.__version__}")
                caption_content = response.choices[0].message.content
                print(f"Extracted caption content: {caption_content}")
                return caption_content
        except openai.APIError as e:
            print(f"OpenAI API error: {e}")
            page.snack_bar.content = ft.Text(f"OpenAI API error: {e}")
            page.snack_bar.open = True
            page.update()
            return f"Error generating caption: OpenAI API error: {e}"
        except FileNotFoundError:
            print(f"Error: Image file not found at path: {image_path}")
            page.snack_bar.content = ft.Text("Error: Image file not found.")
            page.snack_bar.open = True
            page.update()
            return "Error generating caption: Image file not found."
        except Exception as e:
            print(f"Unexpected error generating caption: {e}")
            page.snack_bar.content = ft.Text(f"Unexpected error generating caption: {e}")
            page.snack_bar.open = True
            page.update()
            return "Error generating caption."

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
            print(f"Thumbnail clicked, current_image_path set to: {image_path}")
        return inner_click

    def on_directory_picked(e: ft.FilePickerResultEvent):
        if e.path:
            print(f"Directory picked: {e.path}")
            selected_folder_path.value = f"Selected directory: {e.path}"
            image_files = []
            try:
                for filename in os.listdir(e.path):
                    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                        image_files.append(os.path.join(e.path, filename))

                thumbnails_column.controls.clear()
                print(f"Found {len(image_files)} image files in directory")
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
                    print(f"Setting current_image_path to first image: {current_image_path}")
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

    # Define the settings column to be used in central content.
    settings_column = ft.Column(
        visible=False,
        controls=[
            ft.Text("Settings", style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)),
            ft.TextField(ref=api_key_field, label="OpenAI API Key", password=True, can_reveal_password=True, width=300, fill_color=ft.Colors.BLACK, border_color=ft.Colors.GREY),
            prompt_field,
            progress_bar,
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Central content: image display, caption input area, settings (moved below the caption area), and folder info.
    central_content = ft.Container(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                image_display,
                caption_column,
                settings_column,
                selected_folder_path,
            ],
        ),
        expand=True,
        bgcolor=ft.Colors.BLACK,
        padding=20,
    )

    # Right column:
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

    page.window.min_width = MIN_THUMBNAILS_WIDTH + MIN_CENTRAL_WIDTH + MIN_TAG_MANAGEMENT_WIDTH + 40

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
