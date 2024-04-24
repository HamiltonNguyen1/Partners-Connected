"""
The purpose of this program is allow Heritage's CTE Department to add and store information about their partners.
This program allows them to filter out and search their partners which will be displayed on the screen.
It also includes a help chat bot where the user of the program can ask the bot for help and if the bot
doesn't help their problem, then the user can enter their email where a real human can enter their
question.
"""

import json
import tkinter as tk
from tkinter import ttk
import customtkinter
from tkinter import *
from PIL import ImageTk, Image
import time
import smtplib
from tkinter import messagebox
import sqlite3
from datetime import datetime
import requests
import webbrowser
import re
from tkinter import filedialog


# This connects the database and the backup database and makes the cursors as well.
backup_connection = sqlite3.connect('partnersBackupDatabase.db')
connection = sqlite3.connect('partnersDatabase.db')
connection_cursor = connection.cursor()
backup_connection_cursor = backup_connection.cursor()

connection_cursor.execute('''CREATE TABLE IF NOT EXISTS partners (
                    name text,
                    type text,
                    resources text,
                    email text,
                    phoneNum text,
                    description TEXT,
                    website TEXT
                )''')
backup_connection_cursor.execute('''CREATE TABLE IF NOT EXISTS backups (
                                fullBackUp TEXT,
                                time TEXT)''')
connection.commit()
backup_connection.commit()

def backup_screen():
    global backups_combobox
    backup_screen = tk.Tk()
    backup_screen.geometry("600x300")
    backup_screen.minsize(600, 300)
    backup_screen.maxsize(600, 300)
    backup_screen.title("Backup Management")
    frame = customtkinter.CTkFrame(master=backup_screen, width=1000, height=600,
                                   fg_color="#33383F", corner_radius=0)
    frame.place(x=0, y=0)
    help_menu_title = customtkinter.CTkLabel(backup_screen, text="Backup Management",
                                             font=("Arial bold", 30),
                                             fg_color="#33383F",
                                             text_color="#0087F2")
    help_menu_title.place(x=150, y=20)
    backup_connection_cursor.execute("SELECT * FROM backups")
    backups = backup_connection_cursor.fetchall()
    backup_dates = []
    for backup in backups:
        backup_dates.append(backup[1])
    backups_combobox = customtkinter.CTkComboBox(backup_screen,
                                                bg_color="#33383F",
                                                fg_color="#33383F",
                                                button_color="#0087F2",
                                                border_color="#0087F2",
                                                width=200, border_width=2,
                                                values=backup_dates,
                                                state='readonly'
                                                 )
    backups_combobox.place(x=205, y=100)

    backups_button = customtkinter.CTkButton(backup_screen, text="View Backup",
                                                command=lambda: show_backups(backups_combobox.get()),
                                                fg_color="#0087F2",
                                                text_color="#33383F",
                                                font=("Arial bold", 15),
                                                bg_color="#33383F",
                                                corner_radius=100, width=170)
    backups_button.place(x=120, y=160)

    replace_data_button = customtkinter.CTkButton(backup_screen, text="Replace Database",
                                                command=lambda: replace_database(backups_combobox.get()),
                                                fg_color="#0087F2",
                                                text_color="#33383F",
                                                font=("Arial bold", 15),
                                                bg_color="#33383F",
                                                corner_radius=100, width=170)
    replace_data_button.place(x=310, y=160)

def clear_backups():
    if (messagebox.askquestion("askquestion",
                               "Are you sure you want to delete all the backups?")):
        backup_connection_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = backup_connection_cursor.fetchall()

        for table in tables:
            table_name = table[0]
            backup_connection_cursor.execute(f"DELETE FROM {table_name}")

        backup_connection.commit()


def replace_database(backup_date):
    if (backup_date != ""):
        connection_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = connection_cursor.fetchall()

        for table in tables:
            table_name = table[0]
            connection_cursor.execute(f"DELETE FROM {table_name}")

        backup_connection_cursor.execute("SELECT * FROM backups WHERE time = ?", (backup_date,))
        backup = backup_connection_cursor.fetchall()
        resources = []
        for partner in json.loads(backup[0][0]):
            for resource in partner[2]:
                resources.append(resource)
            connection_cursor.execute("INSERT INTO partners VALUES (?, ?, ?, ?, ?, ?, ?)",
                                      (partner[0], partner[1],
                                       json.dumps(resources), partner[3],
                                       partner[4], partner[5], partner[6]))
        connection.commit()
    else:
        messagebox.showwarning("No datetime chosen", "Please choose a backup.")



def open_file_explorer():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    save_path = filedialog.asksaveasfilename(title="Save")
    return save_path

def show_backups(backup_date):
    if (backup_date != ""):
        backup_connection_cursor.execute("SELECT * FROM backups WHERE time = ?", (backup_date,))
        backup = backup_connection_cursor.fetchall()
        backup_file = open("backup.txt", "w")
        backup_file.truncate(0)
        backup_file.write(f"Date of backup: {backup_date}\n\n")
        print(backup[0])
        for partner in json.loads(backup[0][0]):
            backup_file.write(f"Partner Name: {partner[0]}\n")
            backup_file.write(f"Partner Type: {partner[1]}\n")
            backup_file.write(f"Resource(s):\n")
            for resource in json.loads(partner[2]):
                backup_file.write(f"{resource}\n")
            backup_file.write(f"Partner Email: {partner[3]}\n")
            backup_file.write(f"Partner Phone: {partner[4]}\n")
            backup_file.write(f"Partner Description: {partner[5]}\n")
            backup_file.write(f"Partner Website: {partner[6]}\n\n")
        backup_file.close()
        try:
            # Open the source file in read mode
            with open("backup.txt", 'r') as source_file:
                # Read the content of the source file
                file_content = source_file.read()

            # Prompt the user to enter the destination path
            destination_path = open_file_explorer()

            # Write the content to the destination file
            with open(destination_path, 'w') as destination_file:
                destination_file.write(file_content)

            print("File downloaded successfully")
        except:
            pass
    else:
        messagebox.showwarning("No datetime chosen", "Please choose a backup.")


# This function dynamically back-ups the database when it is updated or when the program is closed or opened.
def dynamic_backup():
    global connection, connection_cursor, backup_connection_cursor, \
        backup_connection

    # This will get the database and put it in the back-up database.
    connection_cursor.execute("SELECT * FROM partners")
    backup_connection_cursor.execute("INSERT INTO backups VALUES (?, ?)",
                                     (json.dumps(connection_cursor.fetchall()),
                                      str(datetime.now(

                                      ))))
    backup_connection.commit()

    # This tells the user that the program was backed up
    print("Back up at " + str(datetime.now()))


# This function opens up the help_menu, where the user can get help, instructions, and guidance from the chat bot.
# If the bot can't help the user, then the user can send their email and problem to the bot where it would be
# answered by a real person.
def help_menu():
    global text, help_entry, help_menu_screen, help_button

    # This sets up the screen.
    help_menu_screen = tk.Tk()
    help_menu_screen.geometry("398x500")
    help_menu_screen.minsize(398, 500)
    help_menu_screen.maxsize(398, 500)
    help_menu_screen.title("Help Menu")

    # Background Color
    help_menu_frame = customtkinter.CTkFrame(master=help_menu_screen,
                                             width=400,
                                             height=500,
                                             fg_color="#0087F2",
                                             corner_radius=0)
    help_menu_frame.place(x=0, y=0)

    # Help menu title
    help_menu_title = customtkinter.CTkLabel(help_menu_screen, text="Help "
                                                                    "Menu "
                                                                    "Chat "
                                                                    "Bot",
                                             font=("Arial bold", 25),
                                             fg_color="#0087F2",
                                             text_color="#33383F")
    help_menu_title.place(x=80, y=3)

    # Where the bots text and the user's text will be displayed.
    text = Text(help_menu_screen, bg="#33383F", fg="white", font=("Arial", 12),
                width=44,
                height=24, bd=0, state="normal",
                wrap=WORD)
    text.place(x=0, y=37)

    # Where the user can type what they need and send it to the bot.
    help_entry = customtkinter.CTkEntry(help_menu_screen,
                                        placeholder_text="Type "
                                                         "your "
                                                         "Question...",
                                        bg_color="#33383F",
                                        text_color="white",
                                        placeholder_text_color="white",
                                        border_color="#0087F2",
                                        border_width=2, font=("Arial", 15),
                                        width=320, corner_radius=0)
    help_entry.place(x=0, y=471)

    # Where the user presses the button after they are done writing their problem.
    help_button = customtkinter.CTkButton(help_menu_screen, text="Send",
                                          command=chat_bot,
                                          fg_color="#0087F2",
                                          text_color="#33383F",
                                          font=("Arial bold", 15),
                                          bg_color="#33383F", width=78,
                                          corner_radius=0)
    help_button.place(x=320, y=471)

    # To set up the bot's messages when the screen is first opened.
    chat_bot("message")


problem = False
email = False


# After the user presses send, it runs this function where the bot can detect what the user said, and
# the response of the bot.
def chat_bot(message=""):
    global text, help_entry, help_menu_screen, help_button, email, problem, \
        email_address

    # These messages are displayed when the screen is first opened.
    if (message != ""):
        writing_function("Bot: Hello, welcome to the help menu!")
        writing_function("Bot: What can I help you with today?")
        writing_function(
            "Bot: Type \"1\" for help with adding & removing partners, \"2\" for help with searching and filtering partners, and \"3\" for other help.")

    # Else, if it isn't the first time the screen has been opened, it assumes the user had said something.
    else:

        # This will display what the user said.
        writing_function("You: " + help_entry.get())

        # This runs if the user had entered 3 in the entry, and entered their email as well
        # as their problem. This will email the user's problem to the help department,
        # where the people at the help department can open up a support case and email
        # the user back when they have answered their question.
        if (problem):

            # This will send the email to the help department where they can email the user once
            # the help department has answered their question.
            try:
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.starttls()
                mail.login("heritagehelpdepartment@gmail.com",
                           "ijwn sqcl ksln wagf")
                message = 'Subject: {}\n\n{}'.format(email_address,
                                                     help_entry.get())
                mail.sendmail("heritagehelpdepartment@gmail.com",
                              "heritagehelpdepartment@gmail.com",
                              message)
                message = 'Subject: {}\n\n{}'.format("Your Help Ticket Has Been Sent", "Please allow us to have some time to respond to this help ticket,"
                                                                                       " we appreciate your call for help and we want to help you. "
                                                                                       "Thanks for improving our program as help tickets are crucial to the "
                                                                                       "running of our program!\nPartners Connected")
                mail.sendmail("heritagehelpdepartment@gmail.com", email_address, message)

                writing_function(
                    "Bot: Your problem has been emailed to the Help Department.")
                writing_function("Bot: We will respond whenever we have the "
                                 "time.")
                writing_function(
                    "Bot: Is there anything else I can help with you today?")
                writing_function(
                    "Bot: Type \"1\" for help with adding & removing partners, \"2\" for help with searching and filtering partners, and \"3\" for other help.")
            except:
                writing_function(
                    "Bot: Sorry, your problem couldn't be emailed to the Help Department.")
                writing_function(
                    "Bot: Is there anything else I can help with you today?")
                writing_function(
                    "Bot: Type \"1\" for help with adding & removing partners, \"2\" for help with searching and filtering partners, and \"3\" for other help.")
            problem = False

        # This runs if the user had entered 3 in the entry, and entered their email.
        elif (email):
            if (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', help_entry.get())):
                email_address = help_entry.get()
                writing_function("Bot: Got it.")
                writing_function("Bot: Please state your problem.")
                problem = True
                email = False
            else:
                writing_function(
                    "Bot: The email you entered was invalid, please try again.")

        # If the user entered 1, that means they needed help with adding and removing partners, so the
        # bot will give them instructions and guidance on how to do so.
        elif (help_entry.get() == "1"):
            writing_function(
                "Bot: To add partners, simply enter the organization's name, type, email, and phone number.")
            writing_function(
                "Bot: You can add up to three resources per organization.")
            writing_function(
                "Bot: To remove a partner, simply choose the organization you want to remove and click \"Remove Partner\"")
            writing_function(
                "Bot: Is there anything else I can help you with today?")
            writing_function(
                "Bot: Type \"1\" for help with adding & removing partners, \"2\" for help with searching and filtering partners, and \"3\" for other help.")

        # If the user entered 2, that means that the user needed help with searching and filtering the organizations.
        # The bot will tell the user instructions and guidance on how to use the search bar and the filter.
        elif (help_entry.get() == "2"):
            writing_function(
                "Bot: When using the search bar, the program searches all five columns and sees if there is a match to what was typed in the search bar.")
            writing_function("Bot: The search bar is not case-sensitive.")
            writing_function(
                "Bot: The filter is used to filter out the different types of organizations by organization type.")
            writing_function(
                "Bot: Simply click and choose a category and it filter out the organization's in that category for you.")
            writing_function(
                "Bot: Is there anything else I can help you with today?")
            writing_function(
                "Bot: Type \"1\" for help with adding & removing partners, \"2\" for help with searching and filtering partners, and \"3\" for other help.")

        # If the user entered 3, that means they needed help other than what the bot provided, so
        # the bot tells them to enter their email so the bot can assist them further.
        elif (help_entry.get() == "3"):
            writing_function("Bot: Please enter your email.")
            email = True

        # This is if the user entered something invalid that wasn't in the options of what the bot listed.
        else:
            writing_function(
                "Bot: Sorry, I didn't quite understand, please try again.")

        # This will delete the users entry on the bottom after they have sent their message.
        help_entry.delete(0, len(help_entry.get()))


# This function is used to display the text in the help menu.
def writing_function(message):
    global text

    # This disables the help_button and the help_entry so the user can't type
    # or send anything while the bot is typing.
    help_button.configure(state=tk.DISABLED)
    help_entry.configure(state=tk.DISABLED)

    # This will display the message on the screen with a little delay so it has the typing effect.
    for i in message:
        text.configure(state=tk.NORMAL)
        text.insert(END, i)
        text.configure(state=tk.DISABLED)
        text.update()
        time.sleep(0.001)
        text.yview_moveto(1.0)

    # This will add a new line break in the text, then set all the widgets back to normal.
    text.configure(state=tk.NORMAL)
    text.insert(END, "\n")
    text.configure(state=tk.DISABLED)
    help_button.configure(state=tk.NORMAL)
    help_entry.configure(state=tk.NORMAL)


# This is the function that is used to filter out partners on the treeview.
# The user picks out the type of organization to filter out, and the program filters the treeview.
def filter_partners(type):
    global connection_cursor, backup_connection_cursor

    # This gets rid of all the partners on the treeview, so it can be updated.
    partner_display.delete(*partner_display.get_children())

    # If type isn't all, then the program will match the filter to the different partners, and if there is a match,
    # then the program adds it to the list to append to the treeview.
    # It opens up the database to gather the data in order to filter the partners on the display.
    filtered_partners = []
    connection_cursor.execute("SELECT * FROM partners")

    # This will sort the partners by if they have a website or not.
    if (type == "Website"):
        for i in range(len(connection_cursor.fetchall())):
            connection_cursor.execute("SELECT * FROM partners")
            if (connection_cursor.fetchall()[i][6] != ""):
                connection_cursor.execute("SELECT * FROM partners")
                filtered_partners.append(connection_cursor.fetchall()[i])
        treeview_insertion(filtered_partners)
    elif (type != "All"):
        for i in range(len(connection_cursor.fetchall())):
            connection_cursor.execute("SELECT * FROM partners")
            if (type == connection_cursor.fetchall()[i][1]):
                connection_cursor.execute("SELECT * FROM partners")
                filtered_partners.append(connection_cursor.fetchall()[i])
        treeview_insertion(filtered_partners)

    # Else, it just adds all the partners on the treeview.
    else:
        connection_cursor.execute("SELECT * FROM partners")
        treeview_insertion(connection_cursor.fetchall())


# This function is used to remove partners from the program.
# The user picks a partner from the combobox, and it deletes the partner from the database.
def remove_partner():
    global remove_org_combobox, org_names, connection_cursor, connection

    # If the combobox is empty, that means that the user didn't pick an option and the program
    # tells them to pick an option.
    if (remove_org_combobox.get() == ""):
        messagebox.showwarning("Invalid Option", "Please pick an option.")

    # Else, the user did pick an option and the program will delete the partner by searching for them in the list
    # of partners and finding a match, then deleting the partner.
    else:
        connection_cursor.execute("SELECT * FROM partners")
        for i in range(len(connection_cursor.fetchall())):
            connection_cursor.execute("SELECT * FROM partners")
            if (connection_cursor.fetchall()[i][0] ==
                    remove_org_combobox.get()):
                connection_cursor.execute("DELETE FROM partners WHERE name ="
                                          " ?",
                                          (remove_org_combobox.get(),))
                connection.commit()
                org_names.pop(i)

        # This will update the combobox, the treeview, labels and notify the user that the partner was removed.
        remove_org_combobox.configure(values=org_names)
        partner_display.delete(*partner_display.get_children())
        connection_cursor.execute("SELECT * FROM partners")
        treeview_insertion(connection_cursor.fetchall())
        messagebox.showinfo("Partner Removed", "Partner successfully removed.")
        remove_org_combobox.set("")
        dynamic_backup()

        connection_cursor.execute("""SELECT * FROM partners""")
        number_of_partners = connection_cursor.fetchall()
        total_partners_label.configure(text=f"{len(number_of_partners)} Partners and Counting!")


resources = []


# This function is used to add resources when adding a partner to the program.
# The user will enter a resource for the partner, then click the button which will make
# this function run where it would add the user's resource only if there aren't more than three resources.
def add_resource():
    global resources_combobox, resources

    # This will update the color of the combobox if previously it was red due to the user not entering a resource when
    # pressing the submit button.
    resources_combobox.configure(bg_color="#33383F",
                                 fg_color="#33383F", button_color="#0087F2",
                                 border_color="#0087F2")

    # If the length of resources aren't equal to 3 and the resource isn't empty, then the program adds the resource.
    if (resources_combobox.get() == ""):
        messagebox.showwarning("Empty Resource", "Adding an empty resource isn't allowed. Please try again.")
    elif (len(resources) != 3):
        resources.append(resources_combobox.get())

    # Else, the user gets warned that there are too many resources.
    else:
        messagebox.showwarning("Too Many Resources",
                               "You can only add up to three resources.")

    # Resets the combobox and updates the combobox.
    resources_combobox.set("")
    resources_combobox.configure(values=resources)


# This function is to remove resources from the partner that the user is trying to add.
# The user will pick a resource that they added, and when they click the button to remove the resource,
# then this function will run removing that resource.
def remove_resource():
    global resources_combobox, resources
    popped = False

    # This will update the color of the combobox if previously it was red due to the user not entering a resource when
    # pressing the submit button.
    resources_combobox.configure(bg_color="#33383F",
                                 fg_color="#33383F", button_color="#0087F2",
                                 border_color="#0087F2")

    # This will search all the resources for that partner and try to match it to the resource that the user picked.
    # If there is a match, the resource is removed.
    for i in range(len(resources)):
        if (resources_combobox.get() == resources[i]):
            resources.pop(i)
            popped = True

    # If a resource was removed, the combobox will update.
    if (popped):
        resources_combobox.configure(values=resources)

    # If the resource couldn't be found, then the user will be notified of this.
    else:
        messagebox.showwarning("Resource Could Not Be Removed",
                               "Resource not found.")

    # This will update the combobox.
    resources_combobox.set("")


# This function is used to check all the entries that the user inputted when trying to add a partner.
# It checks the name, type, email, phone, and resources entries and see if they are valid or not.
def add_partner():
    global org_name_entry, org_type_entry, email_entry, phone_entry, \
        resources_combobox, total_partners_label, \
        resources, filter_combobox, connection_cursor, connection
    name_entered = True
    type_entered = True
    email_entered = True
    phone_entered = True
    resources_entered = True
    description_entered = True
    valid_website = True

    # This will change the border colors of the entries to its original color if the color was changed in anyway before.
    org_name_entry.configure(border_color="#0087F2")
    org_type_entry.configure(border_color="#0087F2")
    email_entry.configure(border_color="#0087F2")
    phone_entry.configure(border_color="#0087F2")
    resources_combobox.configure(button_color="#0087F2",
                                 border_color="#0087F2",
                                 bg_color="#0087F2")
    website_entry.configure(border_color="#0087F2")

    # This will check the name entry and check if it's not empty or not.
    if (org_name_entry.get() == ""):
        org_name_entry.configure(border_color="red")
        name_entered = False

    # This will check the type of organization entry and check if it's not empty or not.
    if (org_type_entry.get() == ""):
        org_type_entry.configure(border_color="red")
        type_entered = False

    # This will check the email entry and check if it's not empty or not and check the validity of it.
    if (email_entry.get() == ""):
        email_entry.configure(border_color="red")
        email_entered = False
    elif (not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_entry.get())):
        messagebox.showwarning("Invalid Email Address", "Please enter a valid email address.")
        email_entry.configure(border_color="red")
        return

    # This will check the phone number entry and check if it's not empty or not and check the validity of the phone number.
    if (phone_entry.get() == ""):
        phone_entry.configure(border_color="red")
        phone_entered = False
    elif (not re.match(r'^\(\d{3}\) \d{3}-\d{4}$', phone_entry.get())):
        phone_entry.configure(border_color="red")
        messagebox.showwarning("Invalid Phone Number", "Please format the phone number into (XXX) XXX-XXXX form.")
        return

    # Checks if the description is empty or not.
    if (description_entry.get() == ""):
        description_entry.configure(border_color="red")
        description_entered = False

    # This will check the resources and see if there's no resources or not.
    if (len(resources) == 0):
        resources_combobox.configure(button_color="red", border_color="red",
                                     bg_color="red")
        resources_entered = False

    if (website_entry.get() != ""):
        try:
            response = requests.head(website_entry.get())
            if response.status_code != 200:
                valid_website = False
        except:
            valid_website = False
            website_entry.configure(border_color="red")

    # This will add the new partner to the database if all entries are met.
    if (name_entered and type_entered and email_entered and phone_entered
            and resources_entered and description_entered and valid_website):

        # This adds the partner to the database.
        connection_cursor.execute("INSERT INTO partners VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (org_name_entry.get(),
                                   org_type_entry.get(),
                                   json.dumps(resources), email_entry.get(),
                                   phone_entry.get(), description_entry.get(),
                                   website_entry.get()))

        # This will clear all the entries.
        org_name_entry.delete(0, len(org_name_entry.get()))
        org_type_entry.delete(0, len(org_type_entry.get()))
        resources.clear()
        email_entry.delete(0, len(email_entry.get()))
        phone_entry.delete(0, len(phone_entry.get()))
        description_entry.delete(0, len(description_entry.get()))
        website_entry.delete(0, len(description_entry.get()))
        filter_combobox.set("")

        # This will update the treeview and labels and notify the user that the partner was successfully added.
        partner_display.delete(*partner_display.get_children())
        connection_cursor.execute("SELECT * FROM partners")
        treeview_insertion(connection_cursor.fetchall())
        messagebox.showinfo("Partner Added", "Partner was successfully added.")
        connection.commit()
        dynamic_backup()

        connection_cursor.execute("""SELECT * FROM partners""")
        number_of_partners = connection_cursor.fetchall()
        total_partners_label.configure(text = f"{len(number_of_partners)} Partners and Counting!")
        update_removal_partners_combobox()

    elif (not valid_website):
        messagebox.showwarning("Invalid Website",
                               "Please enter a valid website or leave the entry blank.")

    # Else, the program tells the user to fill out all the entries.
    else:
        messagebox.showwarning("Could Not Add Partner",
                               "Please fill out all required entries.")


# Each time the search bar updates, this function will be run, matching the users search to what is on the treeview.
def search_partners(search_variable):
    partner_search_list = []
    filter_combobox.set("All")

    # This will delete all the partners on the display.
    partner_display.delete(*partner_display.get_children())

    # This loops through all the partners in the database on the display.
    connection_cursor.execute("SELECT * FROM partners")
    partner_list = connection_cursor.fetchall()
    for j in range(len(partner_list)):
        # The following five for loops will check whether if data from the columns in the treeview match with the user's search.
        # If there is a match, it will be displayed on the treeview.

        # Checks data from Organization Name.
        for k in range(len(str(partner_list[j][0])) - len(str(search_variable)) + 1):
            if search_variable.lower() == partner_list[j][0][k:(k + len(str(search_variable)))].lower():
                partner_search_list.append(partner_list[j])

        # Checks data from Organization Type.
        for k in range(len(str(partner_list[j][1])) - len(str(search_variable)) + 1):
            if search_variable.lower() == partner_list[j][1][k:(k + len(str(search_variable)))].lower():
                partner_search_list.append(partner_list[j])

        # Checks data from the Resources.
        for k in range(len(json.loads(partner_list[j][2]))):
            for l in range(len(str(json.loads(partner_list[j][2])[k])) - len(str(search_variable)) + 1):
                if (search_variable.lower() == json.loads(partner_list[j][2])[k][l:(l + len(str(search_variable)))].lower()):
                    partner_search_list.append(partner_list[j])

        # Checks data from Emails.
        for k in range(len(str(partner_list[j][3])) - len(str(search_variable)) + 1):
            if search_variable.lower() == partner_list[j][3][k:(k + len(str(search_variable)))].lower():
                partner_search_list.append(partner_list[j])

        # Check data from Phone Numbers.
        for k in range(len(str(partner_list[j][4])) - len(str(search_variable)) + 1):
            if search_variable.lower() == partner_list[j][4][k:(k + len(str(search_variable)))].lower():
                partner_search_list.append(partner_list[j])

    # This will filter any duplicate organizations on the list and update the treeview.
    partner_list.clear()
    filtered = []
    for i in partner_search_list:
        if i not in filtered:
            filtered.append(i)
    treeview_insertion(filtered)


# This function is used to insert the partners on the display.
def treeview_insertion(partners):
    global connection_cursor, connection
    # This will add the partners in the parameter to the display.
    for partner in partners:
        partner_resources = json.loads(partner[2])

        # Reformats the resources for each partner so it isn't just a list showing.
        resources_reformated = ""
        for i in range(len(partner_resources)):
            resources_reformated += partner_resources[i] + ", "
        resources_reformated = resources_reformated[:(len(resources_reformated)
                                                      - 2)]

        # Appends the partner to the display.
        partner_display.insert("", "end", values=(partner[0], partner[1],
                                                  resources_reformated,
                                                  partner[3], partner[4]))


# When the user hovers over the treeview, this makes sure to display the description for that partner.
def display_message(event):

    # Identifies the specific partner the user is hovering over, then displays the description.
    item_id = partner_display.identify_row(event.y)
    if (item_id != ""):
        item_values = partner_display.item(item_id)['values'][0]
        connection_cursor.execute("""SELECT * FROM partners WHERE name = ? """,
                                  (item_values,))
        data = connection_cursor.fetchall()

        message_label.configure(text=data[0][5], wraplength=200, anchor="sw")
        update_message_position(event)


# When the user isn't hovering over the treeview, it makes sure to get rid of any description.
def clear_message(event):
    message_label.configure(text="")
    message_label.place_forget()


# This updates the message label so it follows the users mouse.
def update_message_position(event):
    x, y = root.winfo_pointerx(), root.winfo_pointery()
    message_label.place(x=x, y=y, anchor="sw")


# When the user double-clicks a partner, it will pop up the partners website if they have one.
def display_website(event):

    # Get all selected items
    selected_items = partner_display.selection()

    # Makes sure a row is selected
    if not selected_items:
        return
    else:
        # Gets the selected item
        item_iid = selected_items[0]

        # Gets the website from the selected item, then displays the website if the partner has one.
        item_text = partner_display.item(item_iid, "values")[0]
        connection_cursor.execute("""SELECT * FROM partners WHERE name = ?""",
                                  (item_text,))
        website = connection_cursor.fetchall()[0][6]
        if (website != ""):
            webbrowser.open(website)
        else:
            messagebox.showwarning("No Website",
                                   "The partner doesn't have a website.")

# Checks if org type contains a digit or not, which it shouldn't.
def validate_type_input(char):
    return not char.isdigit()


# This function updates the combobox of all partners that can be removed.
def update_removal_partners_combobox():
    global org_names
    org_names = []
    connection_cursor.execute("SELECT * FROM partners")
    for i in range(len(connection_cursor.fetchall())):
        connection_cursor.execute("SELECT * FROM partners")
        org_names.append(connection_cursor.fetchall()[i][0])
    remove_org_combobox.configure(values=org_names)


# Set up for the main screen.
root = tk.Tk()
root.geometry("1540x800")
root.minsize(1540, 800)
root.maxsize(1540, 800)
root.title("Partners Connected")
frame = customtkinter.CTkFrame(master=root, width=1540, height=800,
                               fg_color="#33383F", corner_radius=0)
frame.place(x=0, y=0)

partners_image = customtkinter.CTkImage(light_image=Image.open("Partners.png"),
                                        dark_image=Image.open("Partners.png"),
                                        size=(700, 233))
program_label = customtkinter.CTkLabel(root, image=partners_image, text="")
program_label.place(x=428, y=-20)

# The main display of the partners for the program.
partner_display = ttk.Treeview(root, height=17, selectmode='browse')
partner_display.place(x=30, y=200)

# The scrollbar for the display.
partner_display_scrollbar = ttk.Scrollbar(root, orient="vertical",
                                          command=partner_display.yview)
partner_display_scrollbar.place(x=1482, y=200, relheight=0.459)

# This sets up the display for the partners, setting up the headings, width, columns, and information.
partner_display['show'] = "headings"
partner_display["columns"] = ("1", "2", "3", "4", "5")
columns = ["1", "2", "3", "4", "5"]
headings = ["Organization Name", "Type of Organization", "Resources", "Email",
            "Phone Number"]
widths = [250, 200, 550, 300, 150]

# This will set up the headings and columns for the display.
for head, column, size in zip(headings, columns, widths):
    partner_display.heading(column, text=head)
    partner_display.column(column, anchor="c", width=size)
connection_cursor.execute("SELECT * FROM partners")
treeview_insertion(connection_cursor.fetchall())

# This is the label guiding the user that the entry below is the search bar.
search_label = customtkinter.CTkLabel(root, text="Search",
                                      font=("Arial bold", 25),
                                      fg_color="#33383F", text_color="white")
search_label.place(x=352, y=110)

# This is the search entry, so the user can search the information they need.
# It will update the display for each key the user presses.
search_var = customtkinter.StringVar()
search_entry = customtkinter.CTkEntry(root, corner_radius=100,
                                      bg_color="#33383F",
                                      text_color="white",
                                      placeholder_text_color="white",
                                      border_color="#0087F2",
                                      border_width=2, font=("Arial", 15),
                                      width=200, textvariable=search_var)
search_entry.place(x=350, y=150)

# This is the button that the user can press if they need help in any way.
help_menu_image = ImageTk.PhotoImage(Image.open("questionMark.png"))
help_menu_button = customtkinter.CTkButton(root, text="",
                                           image=help_menu_image,
                                           command=help_menu,
                                           fg_color="#0087F2",
                                           bg_color="#33383F",
                                           corner_radius=100, width=20,
                                           height=20)
help_menu_button.place(x=1435, y=710)

# This is the label guiding the user that the combobox below is where they can filter out the different
# type of organizations.
filter_label = customtkinter.CTkLabel(root, text="Filter",
                                      font=("Arial bold", 25),
                                      fg_color="#33383F", text_color="white")
filter_label.place(x=1002, y=110)

# This is the combobox where the user can click on different types of organizations and it will filter them out.
# The 25 partners on the list originally will have their organization types in this combobox.
partner_types = ["All", "Website"]
connection_cursor.execute("SELECT * FROM partners")
for i in range(len(connection_cursor.fetchall())):
    connection_cursor.execute("SELECT * FROM partners")
    partner_types.append(connection_cursor.fetchall()[i][1])
filter_type = customtkinter.StringVar()
filter_combobox = customtkinter.CTkComboBox(root,
                                            command=filter_partners,
                                            variable=filter_type,
                                            bg_color="#33383F",
                                            fg_color="#33383F",
                                            button_color="#0087F2",
                                            border_color="#0087F2",
                                            width=200, border_width=2,
                                            values=partner_types,
                                            state='readonly')
filter_combobox.place(x=1000, y=150)

# This label tells the user that this part of the program is where you can remove partners from the display.
remove_partner_label = customtkinter.CTkLabel(root, text="Remove Partner",
                                              font=("Arial bold", 25),
                                              fg_color="#33383F",
                                              text_color="white")
remove_partner_label.place(x=1000, y=585)

# This is the combobox that the user can click that lists all the organizations that the user can remove.
# The partners on the list will have their names on this list.
remove_combobox_var = customtkinter.StringVar(value="")
remove_org_combobox = customtkinter.CTkComboBox(root,
                                                command=remove_resource,
                                                variable=remove_combobox_var,
                                                bg_color="#33383F",
                                                fg_color="#33383F",
                                                button_color="#0087F2",
                                                border_color="#0087F2",
                                                width=175, border_width=2,
                                                state='readonly')
remove_org_combobox.place(x=1010, y=635)
update_removal_partners_combobox()

# This is the button that the user presses once they pick an organization to remove.
remove_org_button = customtkinter.CTkButton(root, text="Remove Partner",
                                            command=remove_partner,
                                            fg_color="#0087F2",
                                            text_color="#33383F",
                                            font=("Arial bold", 15),
                                            bg_color="#33383F",
                                            corner_radius=100, width=170)
remove_org_button.place(x=1013, y=675)

# This is the label that tells the user that that part of the program is where they can add new partners.
add_partner_label = customtkinter.CTkLabel(root, text="Add Partner",
                                           font=("Arial bold", 25),
                                           fg_color="#33383F",
                                           text_color="white",
                                           bg_color="#33383F")
add_partner_label.place(x=400, y=585)

# This is the place where the user can enter the name of the organization that they are trying to add.
org_name_entry = customtkinter.CTkEntry(root, placeholder_text="Organization "
                                                               "Name",
                                        corner_radius=100, bg_color="#33383F",
                                        text_color="white",
                                        placeholder_text_color="white",
                                        border_color="#0087F2",
                                        border_width=2, font=("Arial", 15),
                                        width=200)
org_name_entry.place(x=150, y=635)

# This is the place where the user can enter the type of organization that they are trying to add.
org_type_entry = customtkinter.CTkEntry(root, placeholder_text="Organization "
                                                               "Type",
                                        corner_radius=100, bg_color="#33383F",
                                        text_color="white",
                                        placeholder_text_color="white",
                                        border_color="#0087F2",
                                        border_width=2, font=("Arial", 15),
                                        width=200)
org_type_entry.place(x=150, y=685)

# This is the place where the user can list the type of resources that the organization offers that they
# are trying to add.
resources_var = customtkinter.StringVar(value="")
resources_combobox = customtkinter.CTkComboBox(root,
                                               command=add_resource,
                                               variable=resources_var,
                                               bg_color="#33383F",
                                               fg_color="#33383F",
                                               button_color="#0087F2",
                                               border_color="#0087F2",
                                               width=175, border_width=2,
                                               values=[])
resources_combobox.place(x=383, y=635)

# This is the button that the user can press when they are entering resources one by one.
add_resources_button = customtkinter.CTkButton(root, text="Add Resource",
                                               command=add_resource,
                                               fg_color="#0087F2",
                                               text_color="#33383F",
                                               font=("Arial bold", 15),
                                               bg_color="#33383F",
                                               corner_radius=100, width=170)
add_resources_button.place(x=386, y=675)

# This is the button that the user can press when they want to remove a resource that they added for that
# organization when trying to add it.
remove_resources_button = customtkinter.CTkButton(root, text="Remove "
                                                             "Resource",
                                                  command=remove_resource,
                                                  fg_color="#0087F2",
                                                  text_color="#33383F",
                                                  font=("Arial bold", 15),
                                                  bg_color="#33383F",
                                                  corner_radius=100, width=170)
remove_resources_button.place(x=386, y=715)

# This is the entry where the user can enter the organizations email that they are trying to add.
email_entry = customtkinter.CTkEntry(root, placeholder_text="Organization "
                                                            "Email",
                                     corner_radius=100, bg_color="#33383F",
                                     text_color="white",
                                     placeholder_text_color="white",
                                     border_color="#0087F2",
                                     border_width=2, font=("Arial", 15),
                                     width=200)
email_entry.place(x=595, y=635)

# This is the entry where the user can enter the organizations phone number that they are trying to add.
phone_entry = customtkinter.CTkEntry(root, placeholder_text="Organization "
                                                            "Phone "
                                                            "#",
                                     corner_radius=100,
                                     bg_color="#33383F",
                                     text_color="white",
                                     placeholder_text_color="white",
                                     border_color="#0087F2",
                                     border_width=2, font=("Arial", 15),
                                     width=200)
phone_entry.place(x=595, y=685)

website_entry = customtkinter.CTkEntry(root, placeholder_text="Website ("
                                                              "Optional)",
                                       corner_radius=100,
                                       bg_color="#33383F",
                                       text_color="white",
                                       placeholder_text_color="white",
                                       border_color="#0087F2",
                                       border_width=2, font=("Arial", 15),
                                       width=200)
website_entry.place(x=595, y=735)

description_entry = customtkinter.CTkEntry(root,
                                           placeholder_text="Organization "
                                                            "Description",
                                           corner_radius=100,
                                           bg_color="#33383F",
                                           text_color="white",
                                           placeholder_text_color="white",
                                           border_color="#0087F2",
                                           border_width=2, font=("Arial", 15),
                                           width=200)
description_entry.place(x=150, y=735)
# This is the button that the user can press once they are done adding all the information for the
# organization that they are trying to add.
add_partner_button = customtkinter.CTkButton(root, text="Add Partner",
                                             command=add_partner,
                                             fg_color="#0087F2",
                                             text_color="#33383F",
                                             font=("Arial bold", 15),
                                             bg_color="#33383F",
                                             corner_radius=100, width=170)
add_partner_button.place(x=386, y=755)

view_backups_button = customtkinter.CTkButton(root, text="View Backups",
                                             command=backup_screen,
                                             fg_color="#0087F2",
                                             text_color="#33383F",
                                             font=("Arial bold", 15),
                                             bg_color="#33383F",
                                             corner_radius=100, width=170)
view_backups_button.place(x=1330, y=590)

connection_cursor.execute("""SELECT * FROM partners""")
number_of_partners = connection_cursor.fetchall()

# Label displaying total partners in the program.
total_partners_label = customtkinter.CTkLabel(root, text=f"{len(number_of_partners)} Partners and Counting!",
                                           font=("Arial bold", 20),
                                           fg_color="#33383F",
                                           text_color="#0087F2",
                                           bg_color="#33383F")
total_partners_label.place(x=35, y=148)

# Tracing each key the user presses for the search bar so the program can update the display.
search_var.trace("w", lambda *args: search_partners(search_var.get()))

filter_type.trace("w", lambda *args: filter_partners(filter_type))
validate_entry = root.register(validate_type_input)
org_type_entry.configure(validate="key", validatecommand=(validate_entry, '%S'))
# This backs up the database when the program is opened.
dynamic_backup()

partner_display.bind("<Double-1>", display_website)


# Hides the message label until it is used when hovering over the treeview.
message_label = tk.Label(root, text="")
message_label.place(x = -10, y = -10)

partner_display.bind("<Motion>", display_message)
partner_display.bind("<Leave>", clear_message)
root.mainloop()
# This backs up the database when the program is closed.
dynamic_backup()
